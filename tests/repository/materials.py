from pydantic import BaseModel
import pytest
from sqlalchemy.orm import Mapped, mapped_column


from src.fifi import DatetimeDecoratedBase
from src.fifi import LoggerFactory
from faker import Faker


fake = Faker()
LOGGER = LoggerFactory().get(__name__)


@pytest.fixture
def user_factory():
    def create_user(count: int = 1):
        if count == 1:
            return UserSchema(username=fake.name(), email=fake.email(), is_active=True)
        elif count > 1:
            users = []
            for i in range(count):
                users.append(
                    UserSchema(username=fake.name(), email=fake.email(), is_active=True)
                )
            return users

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
