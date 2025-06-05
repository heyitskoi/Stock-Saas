from database import SessionLocal
from models import User
from auth import get_password_hash

def test_limited_user_permissions(client):
    db = SessionLocal()
    user = User(
        username="limited",
        hashed_password=get_password_hash("limited"),
        role="user",
    )
    db.add(user)
    db.commit()
    db.close()

    resp = client.post("/token", data={"username": "limited", "password": "limited"})
    assert resp.status_code == 200
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.get("/users/", headers=headers)
    assert resp.status_code == 403

    resp = client.post(
        "/users/",
        json={"username": "fail", "password": "fail", "role": "user"},
        headers=headers,
    )
    assert resp.status_code == 403


def test_update_and_delete_endpoints(client):
    token = get_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    client.post(
        "/items/add",
        json={"name": "desk", "quantity": 1, "threshold": 0},
        headers=headers,
    )

    update_resp = client.put(
        "/items/update",
        json={"name": "desk", "new_name": "desk-pro", "threshold": 2},
        headers=headers,
    )
    assert update_resp.status_code == 200
    data = update_resp.json()
    assert data["name"] == "desk-pro"
    assert data["threshold"] == 2

    delete_resp = client.request(
        "DELETE",
        "/items/delete",
        json={"name": "desk-pro"},
        headers=headers,
    )
    assert delete_resp.status_code == 200

    status_resp = client.get(
        "/items/status",
        params={"name": "desk-pro"},
        headers=headers,
    )
    assert status_resp.status_code == 404


def test_usage_endpoints(client):
    token = get_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    client.post(
        "/items/add",
        json={"name": "stats", "quantity": 5, "threshold": 0},
        headers=headers,
    )
    # Add more test logic here for /analytics/usage and /analytics/usage/{item_name}
