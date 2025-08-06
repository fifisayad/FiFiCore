import os

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from ..decorator.singleton import singleton
from ..models.decorated_base import DecoratedBase


@singleton
class DatabaseProvider:
    """
    This is a abstract class for providing enginge to database we consider it.
    """

    engine: AsyncEngine
    session_maker: async_sessionmaker

    def __init__(
        self,
        user: str | None = None,
        password: str | None = None,
        host: str | None = None,
        port: int | None = None,
        db_name: str | None = None,
        db_tech: str | None = None,
        db_lib: str | None = None,
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

        # TODO: add try catch for raising Exception for DB connection
        if not user:
            user = os.getenv("DATABASE_USER", "")
        if not password:
            password = os.getenv("DATABASE_PASS", "")
        if not host:
            host = os.getenv("DATABASE_HOST", "")
        if not port:
            port = int(os.getenv("DATABASE_PORT", 0))
        if not db_name:
            db_name = os.getenv("DATABASE_NAME", "")
        if not db_tech:
            db_tech = os.getenv("DATABASE_TECH", "sqllite")
        if not db_lib:
            db_lib = os.getenv("DATABASE_LIB", "aiosqlite")

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
            poolclass=NullPool,
        )
        self.session_maker = async_sessionmaker(self.engine, expire_on_commit=False)

    def get_new_seddion(self) -> AsyncSession:
        """get_new_seddion.
        get a new session of session pool.

        Args:

        Returns:
            AsyncSession:
        """
        return self.session_maker()

    async def shutdown(self):
        """shutdown.
        dispose database engine in terms of gracefully shutting down
        """
        await self.engine.dispose()

    async def init_models(self):
        """init_models.
        initialize and create tables which are defined in the project in the
        database
        """
        async with self.engine.begin() as conn:
            await conn.run_sync(DecoratedBase.metadata.create_all)
