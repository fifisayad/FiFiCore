import pytest

from src.fifi.exceptions import FiFiException
from src.fifi import Repository
from tests.repository.materials import *


@pytest.mark.asyncio
class TestRepositoryRead:
    user_repo = Repository(UserModel)

    async def test_read_by_id(self, database_provider_test, user_factory):
        new_user_schema = user_factory()
        new_user = await self.user_repo.create(data=new_user_schema)

        LOGGER.info(f"user id is: {new_user.id}")
        got_user = await self.user_repo.get_one_by_id(id_=new_user.id)
        LOGGER.info(f"got user model is: {got_user.to_dict()}")

        assert got_user.to_dict() == new_user.to_dict()

    async def test_read_by_id_column_exception(
        self, database_provider_test, user_factory
    ):
        id_ = "example"
        with pytest.raises(FiFiException):
            await self.user_repo.get_one_by_id(id_=id_, column="uuid")
