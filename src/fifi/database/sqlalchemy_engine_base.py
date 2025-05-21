import asyncio
from abc import ABC

from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from ..models.decorated_base import DecoratedBase


class SQLAlchemyEngineBase(ABC):
    """
    This is a abstract class for providing enginge to database we consider it.
    """

    engine: AsyncEngine
    session_maker: async_sessionmaker

    def __init__(
        self,
        user: str,
        password: str,
        host: str,
        port: int,
        db_name: str,
        db_tech: str = "sqllite",
        db_lib: str = "aiosqlite",
    ):
        """__init__.

        Args:
            user (str): user
            password (str): password
            host (str): host
            port (int): port
            db_name (str): db_name
            db_tech (str): db_tech
            db_lib (str): db_lib
        """

        self.engine = create_async_engine(
            url="{}+{}://{}:{}@{}:{}/{}".format(
                db_tech,
                db_lib,
                user,
                password,
                host,
                port,
                db_name,
            ),
            echo=False,
            pool_pre_ping=True,
        )
        self.session_maker = async_sessionmaker(self.engine, expire_on_commit=False)

        asyncio.run(self.init_models())

    async def init_models(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(DecoratedBase.metadata.create_all)
