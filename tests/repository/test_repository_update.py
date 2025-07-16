from src.fifi import Repository
from tests.repository.materials import *


@pytest.mark.asyncio
class TestRepositoryUpdate:
    user_repo = Repository(UserModel)

    async def test_update_by_id(self, database_provider_test, user_factory):
        new_user_schema = user_factory()
        new_user = await self.user_repo.create(data=new_user_schema)

        LOGGER.info(f"user created: {new_user is not None}")
        updated_user = await self.user_repo.update_by_id(
            data=UserSchema(username="miaad", email="miaad@example.com"),
            id_=new_user.id,
        )
        LOGGER.info(f"user updated: {updated_user.to_dict()}")

        assert updated_user.id == new_user.id
        assert updated_user.username == "miaad"

    async def test_update_many_repo(self, database_provider_test, user_factory):
        # Creating Fake Users
        users = [user_factory() for i in range(5)]
        created_users = await self.user_repo.create_many(data=users, return_models=True)
        LOGGER.info(f"user(s) created: {[user.username for user in created_users]}")

        # Updating Users
        update_dict = dict()
        count = 0  # avoid unique error
        for user in created_users:
            update_dict[user.id] = UserSchema(
                username=f"miaad{count}", email=f"miaad{count}@example.com"
            )
            count += 1
        updated_users = await self.user_repo.update_many_by_ids(
            updates=update_dict, return_models=True
        )
        updated_users_by_id = {user.id: user for user in updated_users}
        LOGGER.info(f"user updated: {[user.username for user in updated_users]}")

        for i, created_user in enumerate(created_users):
            updated_user = updated_users_by_id[created_user.id]
            assert updated_user.username == f"miaad{i}"
            assert updated_user.email == f"miaad{i}@example.com"
