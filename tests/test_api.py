import os
import tempfile

# use a temporary sqlite database for tests before importing the app
db_fd, db_path = tempfile.mkstemp(prefix="test_api", suffix=".db")
os.close(db_fd)

# configure the database and secret key once for all tests
os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"
os.environ["SECRET_KEY"] = "test-secret"

from fastapi.testclient import TestClient
from main import app


import pytest


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def teardown_module(module):
    if os.path.exists(db_path):
        os.remove(db_path)


def get_token(client):
    response = client.post('/token', data={'username': 'admin', 'password': 'admin'})
    assert response.status_code == 200
    return response.json()['access_token']


def test_add_item_endpoint(client):
    token = get_token(client)
    headers = {'Authorization': f'Bearer {token}'}
    resp = client.post(
        '/items/add',
        json={'name': 'mouse', 'quantity': 2, 'threshold': 1, 'tenant_id': 1},
        headers=headers,
    )

    assert resp.status_code == 200
    data = resp.json()
    assert data['available'] == 2
    assert data['name'] == 'mouse'

    status_resp = client.get('/items/status', params={'name': 'mouse', 'tenant_id': 1}, headers=headers)
    assert status_resp.status_code == 200
    assert status_resp.json()['mouse']['available'] == 2


def test_issue_and_return_endpoints(client):
    token = get_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    # add initial stock
    add_resp = client.post(
        "/items/add",
        json={"name": "keyboard", "quantity": 5, "threshold": 1, "tenant_id": 1},
        headers=headers,
    )
    assert add_resp.status_code == 200

    # issue some items
    issue_resp = client.post(
        "/items/issue",
        json={"name": "keyboard", "quantity": 3, "tenant_id": 1},
        headers=headers,
    )
    assert issue_resp.status_code == 200
    data = issue_resp.json()
    assert data["available"] == 2
    assert data["in_use"] == 3

    # return a subset
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

    # create single item in inventory
    client.post(
        "/items/add",
        json={"name": "monitor", "quantity": 1, "threshold": 0, "tenant_id": 1},
        headers=headers,
    )

    # issuing more than available should fail
    fail_issue = client.post(
        "/items/issue",
        json={"name": "monitor", "quantity": 2, "tenant_id": 1},
        headers=headers,
    )
    assert fail_issue.status_code == 400

    # issue one correctly
    ok_issue = client.post(
        "/items/issue",
        json={"name": "monitor", "quantity": 1, "tenant_id": 1},
        headers=headers,
    )
    assert ok_issue.status_code == 200
    issued = ok_issue.json()
    assert issued["available"] == 0
    assert issued["in_use"] == 1

    # returning more than in_use should fail
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


def test_audit_log_endpoint(client):
    token = get_token(client)
    headers = {'Authorization': f'Bearer {token}'}

    client.post(
        '/items/add',
        json={'name': 'keyboard', 'quantity': 3, 'threshold': 1, 'tenant_id': 1},
        headers=headers,
    )
    client.post(
        '/items/issue',
        json={'name': 'keyboard', 'quantity': 1, 'tenant_id': 1},
        headers=headers,
    )

    resp = client.get('/audit/logs', params={'limit': 2, 'tenant_id': 1}, headers=headers)
    assert resp.status_code == 200
    logs = resp.json()
    assert len(logs) == 2
    assert all('action' in entry for entry in logs)


def test_export_audit_csv(client):
    token = get_token(client)
    headers = {'Authorization': f'Bearer {token}'}

    client.post(
        '/items/add',
        json={'name': 'csvitem', 'quantity': 1, 'threshold': 0, 'tenant_id': 1},
        headers=headers,
    )

    resp = client.get(
        '/analytics/audit/export',
        params={'limit': 1, 'tenant_id': 1},
        headers=headers,
    )
    assert resp.status_code == 200
    assert resp.headers['content-type'].startswith('text/csv')
    lines = resp.text.strip().splitlines()
    assert lines[0].startswith('id,user_id,item_id,action,quantity,timestamp')

def test_add_item_no_token(client):
    resp = client.post(
        '/items/add',
        json={'name': 'noauth', 'quantity': 1, 'threshold': 0, 'tenant_id': 1},
    )
    assert resp.status_code == 401


def test_add_item_user_role(client):
    from database import SessionLocal
    from models import User
    from auth import get_password_hash

    db = SessionLocal()
    user = User(
        username='regular',
        hashed_password=get_password_hash('regular'),
        role='user',
    )
    db.add(user)
    db.commit()
    db.close()

    resp = client.post('/token', data={'username': 'regular', 'password': 'regular'})
    assert resp.status_code == 200
    token = resp.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    resp = client.post(
        '/items/add',
        json={'name': 'user-item', 'quantity': 1, 'threshold': 0, 'tenant_id': 1},
        headers=headers,
    )
    assert resp.status_code == 403


def test_create_and_list_users(client):
    token = get_token(client)
    headers = {'Authorization': f'Bearer {token}'}

    create_resp = client.post(
        '/users/',
        json={
            'username': 'newuser',
            'password': 'secret',
            'role': 'manager',
            'tenant_id': 1,
        },
        headers=headers,
    )
    assert create_resp.status_code == 200
    data = create_resp.json()
    assert data['username'] == 'newuser'
    assert data['role'] == 'manager'

    list_resp = client.get('/users/', params={'tenant_id': 1}, headers=headers)
    assert list_resp.status_code == 200
    users = list_resp.json()
    assert any(u['username'] == 'newuser' for u in users)


def test_users_admin_required(client):
    from database import SessionLocal
    from models import User
    from auth import get_password_hash

    db = SessionLocal()
    user = User(
        username='limited',
        hashed_password=get_password_hash('limited'),
        role='user',
        tenant_id=1,
    )
    db.add(user)
    db.commit()
    db.close()

    resp = client.post('/token', data={'username': 'limited', 'password': 'limited'})
    assert resp.status_code == 200
    token = resp.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    resp = client.get('/users/', params={'tenant_id': 1}, headers=headers)
    assert resp.status_code == 403

    resp = client.post(
        '/users/',
        json={'username': 'fail', 'password': 'fail', 'role': 'user', 'tenant_id': 1},
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


