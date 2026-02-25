import os
import asyncio
import sqlite3
import pytest
import pytest_asyncio

from src.fifi import DatabaseProvider


@pytest_asyncio.fixture
async def database_provider_test():
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
    print("shutting down db....")
    await db.shutdown()
    # remove singleton instance
    DatabaseProvider.instance = None
    # remove sqlite instance file
    os.remove("./memory")


@pytest_asyncio.fixture
async def get_test_session(database_provider_test):
    async for session in database_provider_test.get_db_session():
        yield session
        break
