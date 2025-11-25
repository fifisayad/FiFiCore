import pytest
import numpy as np

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

    def test_extract_data(self, create_base_repo):
        base_repo: SHMBaseRepository = create_base_repo
        data = np.arange(25).reshape((5, 5))
        base_repo._data = data
        ex_data = base_repo.extract_data(_from=1, _to=3)
        assert np.array_equal(ex_data, data[1:3])
        ex_data = base_repo.extract_data(_from=0, _to=4)
        assert np.array_equal(ex_data, data[0:4])
        ex_data = base_repo.extract_data(_from=-3, _to=-1)
        assert np.array_equal(ex_data, data[-3:-1])
        ex_data = base_repo.extract_data(_from=-3)
        assert np.array_equal(ex_data, data[-3:])
        ex_data = base_repo.extract_data(_to=1)
        assert np.array_equal(ex_data, data[:1])

    def test_new_row(self, create_base_repo):
        base_repo: SHMBaseRepository = create_base_repo
        data = np.arange(25).reshape((5, 5))
        base_repo._data = data
        base_repo.new_row()
        assert not base_repo._data[-1].any()
        assert np.array_equal(data, base_repo._data)
        assert data.base is not None
        assert base_repo._data.base is not None
        assert np.array_equal(data.base, base_repo._data.base)
