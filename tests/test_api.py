import os
import tempfile

# use a temporary sqlite database for tests before importing the app
db_fd, db_path = tempfile.mkstemp(prefix="test_api", suffix=".db")
os.close(db_fd)
os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"
# minimal secret for JWT signing during tests
os.environ.setdefault("SECRET_KEY", "test-secret")

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
    resp = client.post('/items/add', json={'name': 'mouse', 'quantity': 2, 'threshold': 1}, headers=headers)
    assert resp.status_code == 200
    assert resp.json()['available'] == 2

    status_resp = client.get('/items/status', params={'name': 'mouse'}, headers=headers)
    assert status_resp.status_code == 200
    assert status_resp.json()['mouse']['available'] == 2


def test_issue_and_return_endpoints(client):
    token = get_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    # add initial stock
    add_resp = client.post(
        "/items/add",
        json={"name": "keyboard", "quantity": 5, "threshold": 1},
        headers=headers,
    )
    assert add_resp.status_code == 200

    # issue some items
    issue_resp = client.post(
        "/items/issue",
        json={"name": "keyboard", "quantity": 3, "threshold": 0},
        headers=headers,
    )
    assert issue_resp.status_code == 200
    data = issue_resp.json()
    assert data["available"] == 2
    assert data["in_use"] == 3

    # return a subset
    return_resp = client.post(
        "/items/return",
        json={"name": "keyboard", "quantity": 2, "threshold": 0},
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
        json={"name": "monitor", "quantity": 1, "threshold": 0},
        headers=headers,
    )

    # issuing more than available should fail
    fail_issue = client.post(
        "/items/issue",
        json={"name": "monitor", "quantity": 2, "threshold": 0},
        headers=headers,
    )
    assert fail_issue.status_code == 400

    # issue one correctly
    ok_issue = client.post(
        "/items/issue",
        json={"name": "monitor", "quantity": 1, "threshold": 0},
        headers=headers,
    )
    assert ok_issue.status_code == 200
    issued = ok_issue.json()
    assert issued["available"] == 0
    assert issued["in_use"] == 1

    # returning more than in_use should fail
    fail_return = client.post(
        "/items/return",
        json={"name": "monitor", "quantity": 2, "threshold": 0},
        headers=headers,
    )
    assert fail_return.status_code == 400

    status = client.get("/items/status", params={"name": "monitor"}, headers=headers)
    assert status.status_code == 200
    data = status.json()["monitor"]
    assert data["available"] == 0
    assert data["in_use"] == 1

