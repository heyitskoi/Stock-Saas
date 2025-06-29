import os
import tempfile
import asyncio
import pytest
from fastapi.testclient import TestClient
import httpx
import inspect

os.environ.setdefault("SECRET_KEY", "test-secret")

from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker  # noqa: E402

import database  # noqa: E402
import database_async  # noqa: E402
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

    # Patch database and main modules to use temp DB
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
            admin = User(
                username="admin",
                email="admin@example.com",
                hashed_password=get_password_hash("admin"),
                role="admin",
                tenant_id=tenant.id,
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
            asyncio.get_event_loop().run_until_complete(
                main.app.state.rate_limiter.reset()
            )
        yield c

    main.app.dependency_overrides.clear()
    os.remove(tmp.name)


def get_token(client: TestClient) -> str:
    resp = client.post(
        "/token",
        data={"username": "admin", "password": "admin"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert (
        resp.status_code == 200
    ), f"Token request failed: {resp.status_code}, {resp.text}"
    return resp.json()["access_token"]
