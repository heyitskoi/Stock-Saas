import os
import tempfile
from fastapi.testclient import TestClient
import httpx
import pytest
import inspect
import tests.conftest as conf
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from database import Base, get_db
from main import app
import asyncio
from typing import AsyncGenerator, Generator
import json
from models import User, Item, Tenant
from datetime import datetime, timedelta

# Setup temporary SQLite DB path
db_fd, db_path = tempfile.mkstemp(prefix="test_async", suffix=".db")
os.close(db_fd)
os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"
os.environ["ASYNC_DATABASE_URL"] = f"sqlite+aiosqlite:///{db_path}"
os.environ.setdefault("SECRET_KEY", "test-secret")

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker  # noqa: E402
import database_async  # noqa: E402
import database  # noqa: E402
import main  # noqa: E402
from auth import get_password_hash  # noqa: E402


def _make_test_client(app):
    if "transport" in inspect.signature(TestClient).parameters:
        return TestClient(app, transport=httpx.WSGITransport(app))
    return TestClient(app)


engine = None
TestingSessionLocal = None
async_engine = None
TestingAsyncSessionLocal = None


@pytest.fixture
def client():
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
    tmp.close()
    global engine, TestingSessionLocal, async_engine, TestingAsyncSessionLocal
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
            admin = User(
                username="admin",
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
            main.app.state.rate_limiter.limit = 1000
            asyncio.get_event_loop().run_until_complete(
                main.app.state.rate_limiter.reset()
            )
        yield c

    main.app.dependency_overrides.clear()
    os.remove(tmp.name)


def _get_token(client: TestClient) -> str:
    resp = client.post(
        "/token",
        data={"username": "admin", "password": "admin"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert (
        resp.status_code == 200
    ), f"Token request failed: {resp.status_code}, {resp.text}"
    return resp.json()["access_token"]


def test_websocket_receives_inventory_updates(client):
    token = _get_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    with client.websocket_connect(f"/ws/inventory/1?token={token}") as ws:
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
    dest_user = User(
        username="dest_admin",
        hashed_password=get_password_hash("dest"),
        role="admin",
        tenant_id=dest.id,
        notification_preference="email",
    )
    _session.add(dest_user)
    _session.commit()

    client.post(
        "/items/add",
        json={"name": "ws-trans", "quantity": 5, "threshold": 0, "tenant_id": 1},
        headers=headers,
    )

    dest_token_resp = client.post(
        "/token",
        data={"username": "dest_admin", "password": "dest"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert dest_token_resp.status_code == 200
    dest_token = dest_token_resp.json()["access_token"]

    with client.websocket_connect(
        f"/ws/inventory/1?token={token}"
    ) as ws1, client.websocket_connect(
        f"/ws/inventory/{dest.id}?token={dest_token}"
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


@pytest.fixture(scope="function")
def db() -> Generator:
    _engine = create_engine(
        f"sqlite:///{db_path}", connect_args={"check_same_thread": False}
    )
    TestingSessionLocal = sessionmaker(bind=_engine, autocommit=False, autoflush=False)
    Base.metadata.create_all(bind=_engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=_engine)
        _engine.dispose()


@pytest.fixture(scope="function")
async def async_db() -> AsyncGenerator:
    _engine = create_async_engine(f"sqlite+aiosqlite:///{db_path}", future=True)
    TestingAsyncSessionLocal = async_sessionmaker(_engine, expire_on_commit=False)
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with TestingAsyncSessionLocal() as session:
        yield session
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await _engine.dispose()


@pytest.fixture(scope="function")
def client(db) -> Generator:
    def override_get_db():
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_user(db):
    # Create a test tenant
    tenant = Tenant(name="Test Tenant")
    db.add(tenant)
    db.commit()
    db.refresh(tenant)

    # Create a test user
    user = User(
        username="test@example.com",
        hashed_password="hashed_password",
        tenant_id=tenant.id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture(scope="function")
def test_item(db, test_user):
    item = Item(
        name="Test Item",
        available=10,
        in_use=0,
        threshold=5,
        tenant_id=test_user.tenant_id,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def test_websocket_connection(client):
    with client.websocket_connect("/ws") as websocket:
        data = websocket.receive_json()
        assert data["type"] == "connection_established"


def test_websocket_item_update(client, test_user, test_item):
    # First, connect to the websocket
    with client.websocket_connect("/ws") as websocket:
        # Receive the connection established message
        data = websocket.receive_json()
        assert data["type"] == "connection_established"

        # Update the item
        response = client.put(
            f"/items/{test_item.id}",
            json={"name": "Updated Item", "threshold": 10},
            headers={"Authorization": f"Bearer {test_user.id}"},
        )
        assert response.status_code == 200

        # Receive the update message
        data = websocket.receive_json()
        assert data["type"] == "item_updated"
        assert data["item"]["name"] == "Updated Item"
        assert data["item"]["threshold"] == 10


def test_websocket_item_delete(client, test_user, test_item):
    with client.websocket_connect("/ws") as websocket:
        # Receive the connection established message
        data = websocket.receive_json()
        assert data["type"] == "connection_established"

        # Delete the item
        response = client.delete(
            f"/items/{test_item.id}",
            headers={"Authorization": f"Bearer {test_user.id}"},
        )
        assert response.status_code == 204

        # Receive the delete message
        data = websocket.receive_json()
        assert data["type"] == "item_deleted"
        assert data["item_id"] == test_item.id


def test_websocket_item_create(client, test_user):
    with client.websocket_connect("/ws") as websocket:
        # Receive the connection established message
        data = websocket.receive_json()
        assert data["type"] == "connection_established"

        # Create a new item
        response = client.post(
            "/items/",
            json={
                "name": "New Item",
                "qty": 10,
                "threshold": 5,
                "min_par": 0,
            },
            headers={"Authorization": f"Bearer {test_user.id}"},
        )
        assert response.status_code == 200

        # Receive the create message
        data = websocket.receive_json()
        assert data["type"] == "item_created"
        assert data["item"]["name"] == "New Item"
        assert data["item"]["available"] == 10
        assert data["item"]["threshold"] == 5


def test_websocket_multiple_clients(client, test_user, test_item):
    # Connect two clients
    with client.websocket_connect("/ws") as websocket1:
        with client.websocket_connect("/ws") as websocket2:
            # Both clients should receive connection established
            data1 = websocket1.receive_json()
            data2 = websocket2.receive_json()
            assert data1["type"] == "connection_established"
            assert data2["type"] == "connection_established"

            # Update the item
            response = client.put(
                f"/items/{test_item.id}",
                json={"name": "Updated Item", "threshold": 10},
                headers={"Authorization": f"Bearer {test_user.id}"},
            )
            assert response.status_code == 200

            # Both clients should receive the update
            data1 = websocket1.receive_json()
            data2 = websocket2.receive_json()
            assert data1["type"] == "item_updated"
            assert data2["type"] == "item_updated"
            assert data1["item"]["name"] == "Updated Item"
            assert data2["item"]["name"] == "Updated Item"


def test_websocket_tenant_isolation(client, test_user, test_item):
    # Create a second tenant and user
    tenant2 = Tenant(name="Test Tenant 2")
    db = next(get_db())
    db.add(tenant2)
    db.commit()
    db.refresh(tenant2)

    user2 = User(
        username="test2@example.com",
        hashed_password="hashed_password",
        tenant_id=tenant2.id,
    )
    db.add(user2)
    db.commit()
    db.refresh(user2)

    # Connect two clients with different users
    with client.websocket_connect("/ws") as websocket1:
        with client.websocket_connect("/ws") as websocket2:
            # Both clients should receive connection established
            data1 = websocket1.receive_json()
            data2 = websocket2.receive_json()
            assert data1["type"] == "connection_established"
            assert data2["type"] == "connection_established"

            # Update the item (which belongs to tenant1)
            response = client.put(
                f"/items/{test_item.id}",
                json={"name": "Updated Item", "threshold": 10},
                headers={"Authorization": f"Bearer {test_user.id}"},
            )
            assert response.status_code == 200

            # Only the client from tenant1 should receive the update
            data1 = websocket1.receive_json()
            assert data1["type"] == "item_updated"
            assert data1["item"]["name"] == "Updated Item"

            # The second client should not receive any messages
            with pytest.raises(Exception):
                websocket2.receive_json(timeout=1)


def test_websocket_reconnection(client, test_user, test_item):
    # First connection
    with client.websocket_connect("/ws") as websocket1:
        data = websocket1.receive_json()
        assert data["type"] == "connection_established"

        # Update the item
        response = client.put(
            f"/items/{test_item.id}",
            json={"name": "Updated Item", "threshold": 10},
            headers={"Authorization": f"Bearer {test_user.id}"},
        )
        assert response.status_code == 200

        # Receive the update
        data = websocket1.receive_json()
        assert data["type"] == "item_updated"
        assert data["item"]["name"] == "Updated Item"

    # Second connection
    with client.websocket_connect("/ws") as websocket2:
        data = websocket2.receive_json()
        assert data["type"] == "connection_established"

        # Update the item again
        response = client.put(
            f"/items/{test_item.id}",
            json={"name": "Updated Item 2", "threshold": 15},
            headers={"Authorization": f"Bearer {test_user.id}"},
        )
        assert response.status_code == 200

        # Receive the update
        data = websocket2.receive_json()
        assert data["type"] == "item_updated"
        assert data["item"]["name"] == "Updated Item 2"
        assert data["item"]["threshold"] == 15


def test_websocket_invalid_token(client):
    with pytest.raises(Exception):
        with client.websocket_connect("/ws?token=invalid_token") as websocket:
            websocket.receive_json()


def test_websocket_missing_token(client):
    with pytest.raises(Exception):
        with client.websocket_connect("/ws") as websocket:
            websocket.receive_json()


def test_websocket_connection_limit(client, test_user):
    # Try to connect more than the maximum allowed connections
    connections = []
    for _ in range(11):  # Assuming max_connections is 10
        try:
            websocket = client.websocket_connect("/ws")
            connections.append(websocket)
        except Exception as e:
            if len(connections) == 10:
                # The 11th connection should fail
                assert "Connection limit exceeded" in str(e)
            else:
                raise e

    # Clean up connections
    for websocket in connections:
        websocket.close()


def test_websocket_heartbeat(client, test_user):
    with client.websocket_connect("/ws") as websocket:
        # Receive the connection established message
        data = websocket.receive_json()
        assert data["type"] == "connection_established"

        # Send a heartbeat message
        websocket.send_json({"type": "heartbeat"})

        # Should receive a heartbeat response
        data = websocket.receive_json()
        assert data["type"] == "heartbeat_response"


def test_websocket_invalid_message(client, test_user):
    with client.websocket_connect("/ws") as websocket:
        # Receive the connection established message
        data = websocket.receive_json()
        assert data["type"] == "connection_established"

        # Send an invalid message
        websocket.send_json({"type": "invalid_type"})

        # Should receive an error message
        data = websocket.receive_json()
        assert data["type"] == "error"
        assert "Invalid message type" in data["detail"]


def test_websocket_connection_timeout(client, test_user):
    with client.websocket_connect("/ws") as websocket:
        # Receive the connection established message
        data = websocket.receive_json()
        assert data["type"] == "connection_established"

        # Wait for longer than the timeout period
        time.sleep(65)  # Assuming timeout is 60 seconds

        # Try to send a message
        with pytest.raises(Exception):
            websocket.send_json({"type": "heartbeat"})


def test_websocket_broadcast_to_all_tenants(client, test_user, test_item):
    # Create a second tenant and user
    tenant2 = Tenant(name="Test Tenant 2")
    db = next(get_db())
    db.add(tenant2)
    db.commit()
    db.refresh(tenant2)

    user2 = User(
        username="test2@example.com",
        hashed_password="hashed_password",
        tenant_id=tenant2.id,
    )
    db.add(user2)
    db.commit()
    db.refresh(user2)

    # Connect two clients with different users
    with client.websocket_connect("/ws") as websocket1:
        with client.websocket_connect("/ws") as websocket2:
            # Both clients should receive connection established
            data1 = websocket1.receive_json()
            data2 = websocket2.receive_json()
            assert data1["type"] == "connection_established"
            assert data2["type"] == "connection_established"

            # Update the item with broadcast flag
            response = client.put(
                f"/items/{test_item.id}",
                json={
                    "name": "Updated Item",
                    "threshold": 10,
                    "broadcast_to_all_tenants": True,
                },
                headers={"Authorization": f"Bearer {test_user.id}"},
            )
            assert response.status_code == 200

            # Both clients should receive the update
            data1 = websocket1.receive_json()
            data2 = websocket2.receive_json()
            assert data1["type"] == "item_updated"
            assert data2["type"] == "item_updated"
            assert data1["item"]["name"] == "Updated Item"
            assert data2["item"]["name"] == "Updated Item"
