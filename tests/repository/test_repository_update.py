from typing import Dict
from src.fifi import Repository
from tests.repository.materials import *
from src.fifi.exceptions import IntegrityConflictException


@pytest.mark.asyncio
class TestRepositoryUpdate:
    user_repo = Repository(UserModel)

    async def test_update_by_id(self, database_provider_test, user_factory):
        await database_provider_test.init_models()
        new_user_schema = user_factory()
        new_user = await self.user_repo.create(data=new_user_schema)

        LOGGER.info(f"user created: {new_user is not None}")
        miaad_schema = UserSchema(username="miaad", email="miaad@example.com")
        updated_user = await self.user_repo.update_by_id(
            data=miaad_schema,
            id_=new_user.id,
        )
        LOGGER.info(f"user updated: {updated_user.to_dict()}")

        got_user = await self.user_repo.get_one_by_id(id_=new_user.id)
        assert got_user is not None
        LOGGER.info(f"{got_user.to_dict()=}")

        assert updated_user.id == got_user.id
        assert updated_user.username == got_user.username
        assert updated_user.email == got_user.email

    async def test_update_many_repo(self, database_provider_test, user_factory):
        await database_provider_test.init_models()
        # Creating Fake Users
        users = [user_factory() for i in range(5)]
        created_users = await self.user_repo.create_many(data=users)
        LOGGER.info(f"user(s) created: {[user.username for user in created_users]}")

        # Updating Users
        update_dict = dict()
        count = 0  # avoid unique error
        for user in created_users:
            update_dict[user.id] = UserSchema(
                username=f"miaad{count}", email=f"miaad{count}@example.com"
            )
            count += 1
        updated_users = await self.user_repo.update_many_by_ids(updates=update_dict)
        updated_users_by_id = {user.id: user for user in updated_users}
        LOGGER.info(f"user updated: {[user.username for user in updated_users]}")

        for i, created_user in enumerate(created_users):
            updated_user = updated_users_by_id[created_user.id]
            assert updated_user.username == f"miaad{i}"
            assert updated_user.email == f"miaad{i}@example.com"

    async def test_update_many_by_ids_unique_error(
        self, database_provider_test, user_factory
    ):
        await database_provider_test.init_models()
        # Creating Fake Users
        users = [user_factory() for i in range(2)]
        created_users = await self.user_repo.create_many(data=users)
        LOGGER.info(f"user(s) created: {[user.username for user in created_users]}")

        # Updating Users
        update_dict: Dict[str, UserSchema] = dict()
        for user in created_users:
            update_dict[user.id] = UserSchema(
                username=f"miaad", email=f"miaad@example.com"
            )
        with pytest.raises(IntegrityConflictException):
            LOGGER.info("Catched IntegrityConflictException")
            updated_users = await self.user_repo.update_many_by_ids(updates=update_dict)

    async def test_update_entity(self, database_provider_test, user_factory):
        await database_provider_test.init_models()
        # Creating Fake Users
        user = user_factory()
        created_user = await self.user_repo.create(data=user)
        LOGGER.info(f"user created: {(created_user.id, created_user.username)}")

        created_user.username = "TakeShot"
        await self.user_repo.update_entity(created_user)

        shot_user = await self.user_repo.get_one_by_id(id_=created_user.id)

        assert shot_user is not None
        LOGGER.info(f"user updated: {(shot_user.id, shot_user.username)}")
        assert created_user.id == shot_user.id
        assert created_user.username == shot_user.username
