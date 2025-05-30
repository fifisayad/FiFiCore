import pytest


@pytest.mark.redis
def test_create_redis_client():
    assert 1 == 2
