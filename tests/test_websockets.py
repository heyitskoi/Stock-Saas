import os
import tempfile
from fastapi.testclient import TestClient
import httpx
import pytest
import inspect
import pyotp
import tests.conftest as conf

# Setup temporary SQLite DB path
db_fd, db_path = tempfile.mkstemp(prefix="test_async", suffix=".db")
os.close(db_fd)
os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"
os.environ["ASYNC_DATABASE_URL"] = f"sqlite+aiosqlite:///{db_path}"
os.environ.setdefault("SECRET_KEY", "test-secret")

from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker  # noqa: E402
import asyncio  # noqa: E402
import database_async  # noqa: E402
import database  # noqa: E402
import main  # noqa: E402
from models import User, Tenant  # noqa: E402
from auth import get_password_hash  # noqa: E402


def _make_test_client(app):
    if "transport" in inspect.signature(TestClient).parameters:
        return TestClient(app, transport=httpx.WSGITransport(app))
    return TestClient(app)


@pytest.fixture
def client():
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
    tmp.close()
    engine = create_engine(
        f"sqlite:///{tmp.name}", connect_args={"check_same_thread": False}
    )
    TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

    async_engine = create_async_engine(f"sqlite+aiosqlite:///{tmp.name}", future=True)
    TestingAsyncSessionLocal = async_sessionmaker(async_engine, expire_on_commit=False)

    # Patch database and main modules to use in-memory DB
    database.engine = engine
    database.SessionLocal = TestingSessionLocal
    main.engine = engine
    main.SessionLocal = TestingSessionLocal
    database_async.async_engine = async_engine
    database_async.AsyncSessionLocal = TestingAsyncSessionLocal
    main.app.router.on_startup.clear()

    database.Base.metadata.create_all(bind=engine)

    async def init_admin():
        async with TestingAsyncSessionLocal() as adb:
            tenant = Tenant(name="default")
            adb.add(tenant)
            await adb.commit()
            await adb.refresh(tenant)
            conf.ADMIN_TOTP_SECRET = pyotp.random_base32()
            admin = User(
                username="admin",
                hashed_password=get_password_hash("admin"),
                role="admin",
                tenant_id=tenant.id,
                totp_secret=conf.ADMIN_TOTP_SECRET,
                notification_preference="email",
            )
            adb.add(admin)
            await adb.commit()

    asyncio.get_event_loop().run_until_complete(init_admin())

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    main.app.dependency_overrides[database.get_db] = override_get_db

    async def override_get_async_db():
        async with TestingAsyncSessionLocal() as session:
            yield session

    main.app.dependency_overrides[database_async.get_async_db] = override_get_async_db

    with _make_test_client(main.app) as c:
        if hasattr(main.app.state, "rate_limiter"):
            main.app.state.rate_limiter.attempts.clear()
        yield c

    main.app.dependency_overrides.clear()
    os.remove(tmp.name)


def _get_token(client: TestClient) -> str:
    otp = pyotp.TOTP(conf.ADMIN_TOTP_SECRET).now()
    resp = client.post(
        "/token",
        data={"username": "admin", "password": "admin", "totp": otp},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert (
        resp.status_code == 200
    ), f"Token request failed: {resp.status_code}, {resp.text}"
    return resp.json()["access_token"]


def test_websocket_receives_inventory_updates(client):
    token = _get_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    with client.websocket_connect("/ws/inventory/1") as ws:
        resp = client.post(
            "/items/add",
            json={
                "name": "ws-item",
                "quantity": 1,
                "threshold": 0,
                "min_par": 0,
                "tenant_id": 1,
            },
            headers=headers,
        )
        assert resp.status_code == 200
        data = ws.receive_json()
        assert data["event"] == "update"
        assert data["item"] == "ws-item"
        assert data["available"] == 1
        assert data["in_use"] == 0


def test_websocket_transfer_notification(client):
    token = _get_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    from models import Tenant
    import database

    _session = database.SessionLocal()

    dest = Tenant(name="dest")
    _session.add(dest)
    _session.commit()
    _session.refresh(dest)

    client.post(
        "/items/add",
        json={"name": "ws-trans", "quantity": 5, "threshold": 0, "tenant_id": 1},
        headers=headers,
    )

    with client.websocket_connect("/ws/inventory/1") as ws1, client.websocket_connect(
        f"/ws/inventory/{dest.id}"
    ) as ws2:
        resp = client.post(
            "/items/transfer",
            json={
                "name": "ws-trans",
                "quantity": 2,
                "from_tenant_id": 1,
                "to_tenant_id": dest.id,
            },
            headers=headers,
        )
        assert resp.status_code == 200
        msg1 = ws1.receive_json()
        msg2 = ws2.receive_json()
        assert msg1["event"] == "transfer"
        assert msg2["event"] == "transfer"


def teardown_module(module):
    if os.path.exists(db_path):
        os.remove(db_path)
