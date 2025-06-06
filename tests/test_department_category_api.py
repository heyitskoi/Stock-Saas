from tests.conftest import get_token


def test_department_crud(client):
    token = get_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.post(
        "/api/departments/",
        json={"name": "Ops", "icon": "box"},
        headers=headers,
    )
    assert resp.status_code == 200
    dept = resp.json()

    resp = client.get("/api/departments/", headers=headers)
    assert any(d["id"] == dept["id"] for d in resp.json())

    resp = client.put(
        f"/api/departments/{dept['id']}",
        json={"name": "Operations", "icon": "box"},
        headers=headers,
    )
    assert resp.status_code == 200
    assert resp.json()["name"] == "Operations"

    resp = client.get("/api/departments/public")
    assert any(d["id"] == dept["id"] for d in resp.json())

    resp = client.delete(f"/api/departments/{dept['id']}", headers=headers)
    assert resp.status_code == 200


def test_category_crud(client):
    token = get_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    dept = client.post(
        "/api/departments/",
        json={"name": "Sales", "icon": None},
        headers=headers,
    ).json()

    resp = client.post(
        "/api/categories/",
        json={"name": "Retail", "department_id": dept["id"], "icon": None},
        headers=headers,
    )
    assert resp.status_code == 200
    cat = resp.json()

    resp = client.get("/api/categories/", headers=headers)
    assert any(c["id"] == cat["id"] for c in resp.json())

    resp = client.put(
        f"/api/categories/{cat['id']}",
        json={"name": "Retail2", "department_id": dept["id"], "icon": None},
        headers=headers,
    )
    assert resp.status_code == 200
    assert resp.json()["name"] == "Retail2"

    resp = client.delete(f"/api/categories/{cat['id']}", headers=headers)
    assert resp.status_code == 200
