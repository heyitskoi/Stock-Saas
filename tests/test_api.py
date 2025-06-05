import os
import tempfile

# use a temporary sqlite database for tests before importing the app
db_fd, db_path = tempfile.mkstemp(prefix="test_api", suffix=".db")
os.close(db_fd)
os.environ['DATABASE_URL'] = f'sqlite:///{db_path}'
os.environ.setdefault('SECRET_KEY', 'test-secret')

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


def test_audit_log_endpoint(client):
    token = get_token(client)
    headers = {'Authorization': f'Bearer {token}'}

    client.post('/items/add', json={'name': 'keyboard', 'quantity': 3, 'threshold': 1}, headers=headers)
    client.post('/items/issue', json={'name': 'keyboard', 'quantity': 1}, headers=headers)

    resp = client.get('/audit/logs', params={'limit': 2}, headers=headers)
    assert resp.status_code == 200
    logs = resp.json()
    assert len(logs) == 2
    assert all('action' in entry for entry in logs)
