import os
import sqlite3
from typing import Optional
import pytest
import logging
from sqlalchemy import Column, Integer, Select, String
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncEngine
from sqlalchemy import text
from sqlalchemy.ext.asyncio.session import AsyncSession

from src.fifi import SQLAlchemyEngineBase
from src.fifi import DecoratedBase
from src.fifi import db_async_session


class DummyModel(DecoratedBase):
    __tablename__ = "dummy"
    id = Column(Integer, primary_key=True)
    name = Column(String)


@pytest.fixture
def sql_alchemy_engine_base_test():
    sqlite3.connect("memory")
    engine_base = SQLAlchemyEngineBase(
        user="",
        password="",
        host="",
        port=0,
        db_name="memory",
        db_tech="sqlite",
        db_lib="aiosqlite",
    )
    yield engine_base
    os.remove("./memory")


@pytest.mark.asyncio
class TestSQLAlchemyEngineBase:

    async def test_engine_base_initializes_correctly(
        self, sql_alchemy_engine_base_test
    ):

        assert isinstance(sql_alchemy_engine_base_test.engine, AsyncEngine)
        assert isinstance(
            sql_alchemy_engine_base_test.session_maker, async_sessionmaker
        )

        async with sql_alchemy_engine_base_test.engine.begin() as conn:

            result = await conn.execute(
                text(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name='dummy';"
                )
            )
            table = result.scalar()
            logging.info(f"tables = {table}")
            assert table == "dummy"

    async def test_dict_decorated_base(self, sql_alchemy_engine_base_test):

        @db_async_session(sql_alchemy_engine_base_test.session_maker)
        async def data_seeder(session: Optional[AsyncSession] = None):
            if not session:
                raise Exception()
            fifi = DummyModel(name="FiFi")
            mehrdad = DummyModel(name="Mehrdad")
            session.add(fifi)
            session.add(mehrdad)

        @db_async_session(sql_alchemy_engine_base_test.session_maker)
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
