from tests.conftest import get_token


def test_multi_tenant_isolation(client):
    from tests.factories import _session
    from models import Tenant, User
    from auth import get_password_hash

    tenant2 = Tenant(name="second")
    _session.add(tenant2)
    _session.commit()
    _session.refresh(tenant2)

    admin2 = User(
        username="admin2",
        hashed_password=get_password_hash("admin2"),
        role="admin",
        tenant_id=tenant2.id,
        notification_preference="email",
    )
    _session.add(admin2)
    _session.commit()

    token1 = get_token(client)
    resp = client.post("/token", data={"username": "admin2", "password": "admin2"})
    assert resp.status_code == 200
    token2 = resp.json()["access_token"]

    h1 = {"Authorization": f"Bearer {token1}"}
    h2 = {"Authorization": f"Bearer {token2}"}

    client.post(
        "/items/add",
        json={"name": "widget", "quantity": 2, "threshold": 0, "tenant_id": 1},
        headers=h1,
    )

    client.post(
        "/items/add",
        json={"name": "widget", "quantity": 5, "threshold": 0, "tenant_id": tenant2.id},
        headers=h2,
    )

    resp1 = client.get(
        "/items/status",
        params={"name": "widget", "tenant_id": 1},
        headers=h1,
    )
    resp2 = client.get(
        "/items/status",
        params={"name": "widget", "tenant_id": tenant2.id},
        headers=h2,
    )

    assert resp1.status_code == 200
    assert resp2.status_code == 200
    assert resp1.json()["widget"]["available"] == 2
    assert resp2.json()["widget"]["available"] == 5

    logs1 = client.get(
        "/audit/logs", params={"tenant_id": 1, "limit": 10}, headers=h1
    ).json()
    logs2 = client.get(
        "/audit/logs",
        params={"tenant_id": tenant2.id, "limit": 10},
        headers=h2,
    ).json()

    from models import Item

    t1_ids = {i.id for i in _session.query(Item).filter(Item.tenant_id == 1)}
    t2_ids = {i.id for i in _session.query(Item).filter(Item.tenant_id == tenant2.id)}

    assert all(log["item_id"] in t1_ids for log in logs1)
    assert all(log["item_id"] in t2_ids for log in logs2)


def test_update_item_not_found(client):
    token = get_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    resp = client.put(
        "/items/update",
        json={"name": "ghost", "tenant_id": 1, "new_name": "phantom"},
        headers=headers,
    )
    assert resp.status_code == 404


def test_delete_item_not_found(client):
    token = get_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    resp = client.request(
        "DELETE",
        "/items/delete",
        json={"name": "ghost", "tenant_id": 1},
        headers=headers,
    )
    assert resp.status_code == 404


def test_create_user_duplicate_username(client):
    token = get_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "username": "dup",
        "password": "x",
        "role": "user",
        "tenant_id": 1,
        "notification_preference": "email",
    }
    first = client.post("/users/", json=payload, headers=headers)
    assert first.status_code == 200
    second = client.post("/users/", json=payload, headers=headers)
    assert second.status_code == 400


def test_update_user_duplicate_username(client):
    token = get_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    _ = client.post(
        "/users/",
        json={
            "username": "user1",
            "password": "a",
            "role": "user",
            "tenant_id": 1,
            "notification_preference": "email",
        },
        headers=headers,
    )
    u2 = client.post(
        "/users/",
        json={
            "username": "user2",
            "password": "a",
            "role": "user",
            "tenant_id": 1,
            "notification_preference": "email",
        },
        headers=headers,
    )
    uid2 = u2.json()["id"]
    resp = client.put(
        "/users/update",
        json={"id": uid2, "username": "user1"},
        headers=headers,
    )
    assert resp.status_code == 400


def test_delete_user_not_found(client):
    token = get_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    resp = client.request(
        "DELETE",
        "/users/delete",
        json={"id": 9999},
        headers=headers,
    )
    assert resp.status_code == 404


def test_export_csv_not_found(client):
    token = get_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    resp = client.get("/analytics/audit/export/doesnotexist", headers=headers)
    assert resp.status_code == 404


def test_export_csv_pending(client):
    token = get_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    from routers import analytics

    # Prevent background task from completing immediately
    original = analytics._generate_csv
    analytics._generate_csv = lambda limit, tenant_id, task_id: None
    try:
        start = client.post(
            "/analytics/audit/export",
            params={"limit": 1, "tenant_id": 1},
            headers=headers,
        )
        assert start.status_code == 200
        task_id = start.json()["task_id"]
        resp = client.get(f"/analytics/audit/export/{task_id}", headers=headers)
        assert resp.status_code == 202
    finally:
        analytics._generate_csv = original


def test_register_success(client):
    resp = client.post(
        "/auth/register",
        json={"email": "new@example.com", "password": "secret", "is_admin": False},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["username"] == "new@example.com"
    assert data["tenant_id"]


def test_register_duplicate_username(client):
    payload = {"email": "dup@example.com", "password": "x"}
    first = client.post("/auth/register", json=payload)
    assert first.status_code == 200
    second = client.post("/auth/register", json=payload)
    assert second.status_code == 400


def test_register_missing_department(client):
    resp = client.post(
        "/auth/register",
        json={"email": "nodpt@example.com", "password": "pw", "department_id": 99},
    )
    assert resp.status_code == 404
