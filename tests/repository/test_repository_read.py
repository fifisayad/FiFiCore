import pytest

from src.fifi.exceptions import EntityException
from src.fifi import Repository
from tests.repository.materials import *


# TODO: add tests for get by ids
@pytest.mark.asyncio
class TestRepositoryRead:
    user_repo = Repository(UserModel)

    async def test_read_by_id(self, database_provider_test, user_factory):
        await database_provider_test.init_models()
        new_user_schema = user_factory()
        new_user = await self.user_repo.create(data=new_user_schema)

        LOGGER.info(f"user id is: {new_user.id}")
        got_user = await self.user_repo.get_one_by_id(id_=new_user.id)

        assert got_user is not None
        LOGGER.info(f"got user model is: {got_user.to_dict()}")

        assert got_user.to_dict() == new_user.to_dict()

    async def test_read_by_id_column_exception(
        self, database_provider_test, user_factory
    ):
        await database_provider_test.init_models()
        id_ = "example"
        with pytest.raises(EntityException):
            await self.user_repo.get_one_by_id(id_=id_, column="uuid")

    async def test_read_by_ids(self, database_provider_test, user_factory):
        await database_provider_test.init_models()
        users_schema = user_factory(count=5)
        users = await self.user_repo.create_many(data=users_schema)

        users_id = [user.id for user in users]
        LOGGER.info(f"{users_id=}")

        got_users = await self.user_repo.get_many_by_ids(users_id)

        assert len(got_users) == len(users_id)
        for user in got_users:
            assert user.id in users_id
