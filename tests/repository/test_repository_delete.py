from src.fifi import Repository
from tests.repository.materials import *


# TODO: add tests for delete methods
@pytest.mark.asyncio
class TestRepositoryDelete:
    user_repo = Repository(UserModel)
