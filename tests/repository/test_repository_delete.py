from src.fifi import Repository
from src.fifi.exceptions import EntityException
from tests.repository.materials import *


@pytest.mark.asyncio
class TestRepositoryDelete:
    user_repo = Repository(UserModel)

    async def test_delete_by_id(self, database_provider_test, user_factory):
        new_user_schema = user_factory()
        new_user = await self.user_repo.create(data=new_user_schema)

        LOGGER.info(f"user created: {new_user is not None}")
        is_deleted = await self.user_repo.remove_by_id(id_=new_user.id)
        LOGGER.info(f"user removed: {is_deleted == 1}")

        assert is_deleted == 1

    async def test_delete_by_id_with_wrong_colmun(
        self, database_provider_test, user_factory
    ):
        new_user_schema = user_factory()
        new_user = await self.user_repo.create(data=new_user_schema)

        LOGGER.info(f"user created: {new_user is not None}")
        is_deleted = 0
        with pytest.raises(EntityException):
            is_deleted = await self.user_repo.remove_by_id(
                id_=new_user.id, column="dummy_colmun"
            )
        assert is_deleted == 0
        LOGGER.info(f"user not Removed")
        is_deleted = await self.user_repo.remove_by_id(id_=new_user.id)
        assert is_deleted == 1
        LOGGER.info(f"user NOW Removed without dummy colmun")

    async def test_delete_many_repository(self, database_provider_test, user_factory):
        users = [user_factory() for i in range(5)]
        LOGGER.info(f"5 users created")
        created_users = await self.user_repo.create_many(data=users, return_models=True)
        is_deleted = await self.user_repo.remove_many_by_ids(
            ids=[user.id for user in created_users]
        )
        LOGGER.info(f"5 users deleted")
        assert is_deleted == 5

    async def test_delete_many_repository_mix_id(
        self, database_provider_test, user_factory
    ):
        new_user_schema = user_factory()
        new_user = await self.user_repo.create(data=new_user_schema)
        is_deleted = await self.user_repo.remove_many_by_ids(
            ids=[new_user.id, "dummy_id"]
        )
        assert is_deleted == 1
