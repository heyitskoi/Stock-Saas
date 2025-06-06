from tests.conftest import get_token


def test_dashboard_workflow_not_supported(client):
    token = get_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    # Attempt to create a department
    resp = client.post('/departments/', json={"name": "IT"}, headers=headers)
    assert resp.status_code == 404

    # Attempt to create a category
    resp = client.post('/categories/', json={"name": "Hardware", "department_id": 1}, headers=headers)
    assert resp.status_code == 404

    # Create item using existing endpoint
    resp = client.post('/items/add', json={"name": "Laptop", "quantity": 5, "threshold": 1, "tenant_id": 1}, headers=headers)
    assert resp.status_code == 200

    # Attempt to transfer stock between departments
    resp = client.post(
        '/items/transfer',
        json={"name": "Laptop", "from_department_id": 1, "to_department_id": 2, "quantity": 1},
        headers=headers,
    )
    assert resp.status_code == 422

    # Verify audit logs exist for added item
    logs = client.get('/audit/logs', params={"tenant_id": 1, "limit": 10}, headers=headers)
    assert logs.status_code == 200
    assert any(log["action"] == "add" for log in logs.json())
