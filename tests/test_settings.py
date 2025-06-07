from tests.conftest import get_token


def test_update_and_get_settings(client):
    token = get_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.put(
        "/settings",
        json={"tenant_id": 1, "settings": {"example": "value"}},
        headers=headers,
    )
    assert resp.status_code == 200
    assert resp.json()["example"] == "value"

    resp = client.get("/settings", params={"tenant_id": 1}, headers=headers)
    assert resp.status_code == 200
    assert resp.json()["example"] == "value"

