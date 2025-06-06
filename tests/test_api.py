import os
import tempfile

# Setup temporary SQLite database before importing app
db_fd, db_path = tempfile.mkstemp(prefix="test_api", suffix=".db")
os.close(db_fd)
os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"
os.environ["ASYNC_DATABASE_URL"] = f"sqlite+aiosqlite:///{db_path}"
os.environ["SECRET_KEY"] = "test-secret"

from fastapi.testclient import TestClient
from main import app
import pytest
from datetime import datetime, timedelta
from tests.factories import UserFactory, ItemFactory, AuditLogFactory


@pytest.fixture
def client():
    with TestClient(app) as c:
        if hasattr(app.state, "rate_limiter"):
            app.state.rate_limiter.attempts.clear()
        yield c


def teardown_module(module):
    if os.path.exists(db_path):
        os.remove(db_path)
    try:
        from tests.factories import _session as factory_session

        factory_session.close()
    except Exception:
        pass


def get_token(client):
    response = client.post("/token", data={"username": "admin", "password": "admin"})
    assert response.status_code == 200
    return response.json()["access_token"]


def test_add_item_endpoint(client):
    token = get_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    resp = client.post(
        "/items/add",
        json={"name": "mouse", "quantity": 2, "threshold": 1, "tenant_id": 1},
        headers=headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["available"] == 2
    assert data["name"] == "mouse"

    status_resp = client.get(
        "/items/status", params={"name": "mouse", "tenant_id": 1}, headers=headers
    )
    assert status_resp.status_code == 200
    assert status_resp.json()["mouse"]["available"] == 2


def test_issue_and_return_endpoints(client):
    token = get_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    client.post(
        "/items/add",
        json={"name": "keyboard", "quantity": 5, "threshold": 1, "tenant_id": 1},
        headers=headers,
    )

    issue_resp = client.post(
        "/items/issue",
        json={"name": "keyboard", "quantity": 3, "tenant_id": 1},
        headers=headers,
    )
    assert issue_resp.status_code == 200
    data = issue_resp.json()
    assert data["available"] == 2
    assert data["in_use"] == 3

    return_resp = client.post(
        "/items/return",
        json={"name": "keyboard", "quantity": 2, "tenant_id": 1},
        headers=headers,
    )
    assert return_resp.status_code == 200
    returned = return_resp.json()
    assert returned["available"] == 4
    assert returned["in_use"] == 1


def test_issue_return_errors(client):
    token = get_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    client.post(
        "/items/add",
        json={"name": "monitor", "quantity": 1, "threshold": 0, "tenant_id": 1},
        headers=headers,
    )

    fail_issue = client.post(
        "/items/issue",
        json={"name": "monitor", "quantity": 2, "tenant_id": 1},
        headers=headers,
    )
    assert fail_issue.status_code == 400

    ok_issue = client.post(
        "/items/issue",
        json={"name": "monitor", "quantity": 1, "tenant_id": 1},
        headers=headers,
    )
    assert ok_issue.status_code == 200

    fail_return = client.post(
        "/items/return",
        json={"name": "monitor", "quantity": 2, "tenant_id": 1},
        headers=headers,
    )
    assert fail_return.status_code == 400

    status = client.get(
        "/items/status",
        params={"name": "monitor", "tenant_id": 1},
        headers=headers,
    )
    assert status.status_code == 200
    data = status.json()["monitor"]
    assert data["available"] == 0
    assert data["in_use"] == 1


def test_negative_quantity_validation(client):
    token = get_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.post(
        "/items/add",
        json={"name": "bad", "quantity": -1, "threshold": 0, "tenant_id": 1},
        headers=headers,
    )
    assert resp.status_code == 422

    resp = client.post(
        "/items/add",
        json={"name": "good", "quantity": 1, "threshold": 0, "tenant_id": 1},
        headers=headers,
    )
    assert resp.status_code == 200

    issue_fail = client.post(
        "/items/issue",
        json={"name": "good", "quantity": -2, "tenant_id": 1},
        headers=headers,
    )
    assert issue_fail.status_code == 422


def test_audit_log_endpoint(client):
    token = get_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    client.post(
        "/items/add",
        json={"name": "keyboard", "quantity": 3, "threshold": 1, "tenant_id": 1},
        headers=headers,
    )
    client.post(
        "/items/issue",
        json={"name": "keyboard", "quantity": 1, "tenant_id": 1},
        headers=headers,
    )

    resp = client.get(
        "/audit/logs", params={"limit": 2, "tenant_id": 1}, headers=headers
    )
    assert resp.status_code == 200
    logs = resp.json()
    assert len(logs) == 2
    assert all("action" in entry for entry in logs)


def test_export_audit_csv(client):
    token = get_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    client.post(
        "/items/add",
        json={"name": "csvitem", "quantity": 1, "threshold": 0, "tenant_id": 1},
        headers=headers,
    )

    start = client.post(
        "/analytics/audit/export",
        params={"limit": 1, "tenant_id": 1},
        headers=headers,
    )
    assert start.status_code == 200
    task_id = start.json()["task_id"]

    for _ in range(5):
        resp = client.get(f"/analytics/audit/export/{task_id}", headers=headers)
        if resp.status_code == 200:
            break

    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/csv")
    lines = resp.text.strip().splitlines()
    assert lines[0].startswith("id,user_id,item_id,action,quantity,timestamp")


def test_add_item_no_token(client):
    resp = client.post(
        "/items/add",
        json={"name": "noauth", "quantity": 1, "threshold": 0, "tenant_id": 1},
    )
    assert resp.status_code == 401


def test_add_item_user_role(client):
    UserFactory(username="regular", password="regular", role="user", tenant_id=1)

    resp = client.post("/token", data={"username": "regular", "password": "regular"})
    assert resp.status_code == 200
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.post(
        "/items/add",
        json={"name": "user-item", "quantity": 1, "threshold": 0, "tenant_id": 1},
        headers=headers,
    )
    assert resp.status_code == 403


def test_create_and_list_users(client):
    token = get_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    create_resp = client.post(
        "/users/",
        json={
            "username": "newuser",
            "password": "secret",
            "role": "manager",
            "tenant_id": 1,
            "notification_preference": "email",
        },
        headers=headers,
    )
    assert create_resp.status_code == 200
    data = create_resp.json()
    assert data["username"] == "newuser"
    assert data["role"] == "manager"
    assert data["notification_preference"] == "email"

    list_resp = client.get("/users/", params={"tenant_id": 1}, headers=headers)
    assert list_resp.status_code == 200
    users = list_resp.json()
    assert any(u["username"] == "newuser" for u in users)


def test_users_admin_required(client):
    UserFactory(username="limited", password="limited", role="user", tenant_id=1)

    resp = client.post("/token", data={"username": "limited", "password": "limited"})
    assert resp.status_code == 200
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.get("/users/", params={"tenant_id": 1}, headers=headers)
    assert resp.status_code == 403

    resp = client.post(
        "/users/",
        json={"username": "fail", "password": "fail", "role": "user", "tenant_id": 1},
        headers=headers,
    )
    assert resp.status_code == 403


def test_update_and_delete_endpoints(client):
    token = get_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    client.post(
        "/items/add",
        json={"name": "desk", "quantity": 1, "threshold": 0, "tenant_id": 1},
        headers=headers,
    )

    update_resp = client.put(
        "/items/update",
        json={"name": "desk", "tenant_id": 1, "new_name": "desk-pro", "threshold": 2},
        headers=headers,
    )
    assert update_resp.status_code == 200
    data = update_resp.json()
    assert data["name"] == "desk-pro"
    assert data["threshold"] == 2

    delete_resp = client.request(
        "DELETE",
        "/items/delete",
        json={"name": "desk-pro", "tenant_id": 1},
        headers=headers,
    )
    assert delete_resp.status_code == 200

    status_resp = client.get(
        "/items/status",
        params={"name": "desk-pro", "tenant_id": 1},
        headers=headers,
    )
    assert status_resp.status_code == 404


def test_update_and_delete_user(client):
    token = get_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    create_resp = client.post(
        "/users/",
        json={
            "username": "temp",
            "password": "pwd",
            "role": "user",
            "tenant_id": 1,
            "notification_preference": "email",
        },
        headers=headers,
    )
    assert create_resp.status_code == 200
    user_id = create_resp.json()["id"]

    update_resp = client.put(
        "/users/update",
        json={
            "id": user_id,
            "username": "temp2",
            "role": "manager",
            "notification_preference": "slack",
        },
        headers=headers,
    )
    assert update_resp.status_code == 200
    data = update_resp.json()
    assert data["username"] == "temp2"
    assert data["role"] == "manager"
    assert data["notification_preference"] == "slack"

    delete_resp = client.request(
        "DELETE",
        "/users/delete",
        json={"id": user_id},
        headers=headers,
    )
    assert delete_resp.status_code == 200

    list_resp = client.get("/users/", params={"tenant_id": 1}, headers=headers)
    assert all(u["id"] != user_id for u in list_resp.json())


def test_usage_endpoints(client):
    token = get_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    item_name = "stats-analytics"

    client.post(
        "/items/add",
        json={"name": item_name, "quantity": 5, "threshold": 0, "tenant_id": 1},
        headers=headers,
    )

    client.post(
        "/items/issue",
        json={"name": item_name, "quantity": 3, "tenant_id": 1},
        headers=headers,
    )

    client.post(
        "/items/return",
        json={"name": item_name, "quantity": 1, "tenant_id": 1},
        headers=headers,
    )

    usage_resp = client.get(
        f"/analytics/usage/{item_name}",
        params={"tenant_id": 1, "days": 30},
        headers=headers,
    )
    assert usage_resp.status_code == 200
    usage_data = usage_resp.json()
    total_issued = sum(entry["issued"] for entry in usage_data)
    total_returned = sum(entry["returned"] for entry in usage_data)
    assert total_issued == 3
    assert total_returned == 1

    overall_resp = client.get(
        "/analytics/usage",
        params={"tenant_id": 1, "days": 30},
        headers=headers,
    )
    assert overall_resp.status_code == 200
    overall = overall_resp.json()
    assert sum(e["issued"] for e in overall) >= 3
    assert sum(e["returned"] for e in overall) >= 1


def test_usage_invalid_dates(client):
    token = get_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    start = datetime.utcnow()
    end = start - timedelta(days=1)
    resp = client.get(
        "/analytics/usage",
        params={"start_date": start.isoformat(), "end_date": end.isoformat()},
        headers=headers,
    )
    assert resp.status_code == 400


def test_token_rate_limiting(client):
    for _ in range(5):
        resp = client.post("/token", data={"username": "admin", "password": "admin"})
        assert resp.status_code == 200

    blocked = client.post("/token", data={"username": "admin", "password": "admin"})
    assert blocked.status_code == 429


def test_user_route_rate_limiting(client):
    token = get_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    for _ in range(5):
        resp = client.get("/users/", params={"tenant_id": 1}, headers=headers)
        assert resp.status_code == 200

    blocked = client.get("/users/", params={"tenant_id": 1}, headers=headers)
    assert blocked.status_code == 429
