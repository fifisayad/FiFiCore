from pydantic import BaseModel
import pytest
from sqlalchemy.orm import Mapped, mapped_column

from src.fifi.exceptions import IntegrityConflictException
from src.fifi import Repository
from src.fifi import DatetimeDecoratedBase
from src.fifi import GetLogger
from faker import Faker

fake = Faker()
LOGGER = GetLogger().get()


@pytest.fixture
def user_factory():
    def create_user():
        return UserSchema(username=fake.name(), email=fake.email(), is_active=True)

    return create_user


class UserSchema(BaseModel):
    username: str
    email: str
    is_active: bool = True


class UserModel(DatetimeDecoratedBase):
    __tablename__ = "user"
    username: Mapped[str] = mapped_column(nullable=False, unique=True, index=True)
    email: Mapped[str] = mapped_column(unique=True, index=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, server_default="TRUE")


@pytest.mark.asyncio
class TestRepository:
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
