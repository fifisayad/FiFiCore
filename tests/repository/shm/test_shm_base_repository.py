import pytest

from src.fifi.repository.shm.shm_base_repository import SHMBaseRepository


@pytest.fixture
def create_base_repo():
    base_repo = SHMBaseRepository(
        name="test_base",
        rows=5,
        columns=5,
        create=True,
    )
    yield base_repo
    base_repo.close()


class TestSHMBaseRepository:
    def test_init(self, create_base_repo):
        base_repo: SHMBaseRepository = create_base_repo
        assert base_repo._data.shape == (5, 5)
        assert not base_repo._reader
