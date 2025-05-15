from abc import ABC

from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncEngine


class EngineBase(ABC):
    """
    This is a abstract class for providing enginge to database we consider it.
    """

    engine: AsyncEngine
    session_maker: sessionmaker

    def __init__(self):
        """__init__.
        in this method we initiliaze our database engine and
        init our sessionmaker class in terms of passing to session injection
            self.engine = create_async_engine(
                url="postgresql+psycopg://{}:{}@{}:{}/{}".format(
                postgres_data.user,
                postgres_data.password,
                postgres_data.host,
                postgres_data.port,
                postgres_data.db,
            ),
            echo=False,
            pool_pre_ping=True,
        )
        self.session_maker = sessionmaker(self.engine, class_=AsyncSession, expire_on_commit=False)
        DecoratedBase.metadata.create_all(self.engine)
        """
        pass
