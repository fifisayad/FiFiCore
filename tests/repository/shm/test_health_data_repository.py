import time
import numpy as np
import pytest
from src.fifi.repository.shm.health_data_repository import HealthDataRepository


@pytest.fixture
def create_repo():
    repo = HealthDataRepository(name="test_health", create=True)
    yield repo
    repo.close()


class TestHealthDataRepository:
    def test_update(self, create_repo):
        repo: HealthDataRepository = create_repo
        assert not repo.is_updated()

        repo.set_is_updated()
        assert repo.is_updated()

        repo.clear_is_updated()
        assert not repo.is_updated()

    def test_time(self, create_repo):
        repo: HealthDataRepository = create_repo
        assert repo.get_time() == 0

        t = time.time()
        repo.set_time(int(t))
        assert repo.get_time() == int(t)
