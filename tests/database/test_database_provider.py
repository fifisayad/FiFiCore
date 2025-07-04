import os
import sqlite3
from typing import Optional
import pytest
import logging
from sqlalchemy import Column, Select, String
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncEngine
from sqlalchemy import text
from sqlalchemy.ext.asyncio.session import AsyncSession

from src.fifi import DatabaseProvider
from src.fifi import DecoratedBase
from src.fifi import db_async_session


class DummyModel(DecoratedBase):
    __tablename__ = "dummy"
    name = Column(String)


@pytest.fixture
def database_provider_test():
    sqlite3.connect("memory")
    db = DatabaseProvider(
        user="",
        password="",
        host="",
        port=0,
        db_name="memory",
        db_tech="sqlite",
        db_lib="aiosqlite",
    )
    yield db
    # remove singleton instance
    DatabaseProvider.instance = None
    # remove sqlite instance file
    os.remove("./memory")


@pytest.mark.asyncio
class TestDatabaseProvider:

    async def test_database_initializes_correctly(self, database_provider_test):

        assert isinstance(database_provider_test.engine, AsyncEngine)
        assert isinstance(database_provider_test.session_maker, async_sessionmaker)

        async with database_provider_test.engine.begin() as conn:

            result = await conn.execute(
                text(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name='dummy';"
                )
            )
            table = result.scalar()
            logging.info(f"tables = {table}")
            assert table == "dummy"

    async def test_dict_decorated_base(self, database_provider_test):
        @db_async_session
        async def data_seeder(session: Optional[AsyncSession] = None):
            if not session:
                raise Exception()
            fifi = DummyModel(name="FiFi")
            mehrdad = DummyModel(name="Mehrdad")
            session.add(fifi)
            session.add(mehrdad)
            await session.commit()

        @db_async_session
        async def data_reader(session: Optional[AsyncSession] = None) -> DummyModel:
            if not session:
                raise Exception()
            stmt = Select(DummyModel).where(DummyModel.name == "FiFi")
            result = await session.execute(stmt)
            return result.scalar_one()

        await data_seeder()
        fifi = await data_reader()
        logging.info(f"fifi object: {fifi.to_dict()}")
        assert isinstance(fifi.to_dict(), dict)
        assert isinstance(fifi, DummyModel)
        assert str(fifi.name) == "FiFi"
