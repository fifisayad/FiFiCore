from src.fifi import Repository
from tests.repository.materials import *


# TODO: add tests for update methods
@pytest.mark.asyncio
class TestRepositoryUpdate:
    user_repo = Repository(UserModel)
