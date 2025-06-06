from tests.conftest import get_token


def test_rate_limiter_blocks_excess_token_requests(client):
    # Send five successful token requests within the rate limit
    for _ in range(5):
        token = get_token(client)
        assert token

    # Sixth request should exceed the limit and return HTTP 429
    resp = client.post(
        "/token",
        data={"username": "admin", "password": "admin"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert resp.status_code == 429
