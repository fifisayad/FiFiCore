from typing import List
import pytest

from src.fifi.exceptions import IntegrityConflictException
from src.fifi import Repository
from tests.repository.materials import *


@pytest.mark.asyncio
class TestRepositoryCreate:
    user_repo = Repository(UserModel)

    async def test_create_repository(self, database_provider_test, user_factory):
        new_user_schema = user_factory()
        new_user = await self.user_repo.create(data=new_user_schema)

        LOGGER.info(f"user model is: {new_user.to_dict()}")
        assert new_user.email == new_user_schema.email
        assert new_user.username == new_user_schema.username
        assert new_user.is_active == new_user_schema.is_active

    async def test_create_integrity_exception_repository(
        self, database_provider_test, user_factory
    ):
        first_user_schema = user_factory()
        first_user = await self.user_repo.create(data=first_user_schema)
        LOGGER.info(f"first user data: {first_user.to_dict()}")
        # Username and Email are unique in the user table it's not going to create again
        second_user_schema = user_factory()
        second_user_schema.email = first_user_schema.email
        LOGGER.info(f"second user data: {second_user_schema.model_dump()}")
        with pytest.raises(IntegrityConflictException):
            second_user = await self.user_repo.create(data=second_user_schema)

    async def test_create_many_repository(self, database_provider_test, user_factory):
        users: List[UserSchema] = [user_factory() for i in range(5)]
        created_users = await self.user_repo.create_many(data=users)
        for i in range(5):
            assert users[i].username == created_users[i].username
            assert users[i].email == created_users[i].email
            assert users[i].is_active == created_users[i].is_active

    async def test_ceate_many_empty_data_repository(
        self, database_provider_test, user_factory
    ):
        users = []
        created_users = await self.user_repo.create_many(users)
        assert created_users == users

    async def test_create_many_repository_integrity_exception(
        self, database_provider_test, user_factory
    ):
        users = [user_factory() for i in range(3)]
        # copy last user in terms of bring it back
        users.append(users[-1])
        with pytest.raises(IntegrityConflictException):
            await self.user_repo.create_many(data=users)
