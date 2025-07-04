from pydantic import BaseModel
import pytest
from sqlalchemy.orm import Mapped, mapped_column

from src.fifi import Repository
from src.fifi import DatetimeDecoratedBase
from src.fifi import GetLogger
from faker import Faker

fake = Faker()
LOGGER = GetLogger().get()


@pytest.fixture
def mock_user_data():
    return UserSchema(username=fake.name(), email=fake.email(), is_active=True)


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
    async def test_create_repository(self, database_provider_test, mock_user_data):
        user_repo = Repository(UserModel)
        new_user = await user_repo.create(data=mock_user_data)

        LOGGER.info(f"user model is: {new_user.to_dict()}")
        assert new_user.email == mock_user_data.email
        assert new_user.username == mock_user_data.username
        assert new_user.is_active == mock_user_data.is_active
