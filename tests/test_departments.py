import pytest
from tests.conftest import get_token

@pytest.mark.parametrize('endpoint', ['/departments/', '/departments/1', '/categories/'])
def test_department_category_endpoints_not_implemented(client, endpoint):
    token = get_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    resp = client.get(endpoint, headers=headers)
    assert resp.status_code == 404
