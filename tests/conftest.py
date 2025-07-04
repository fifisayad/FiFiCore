import os
import sqlite3
import pytest

from src.fifi import DatabaseProvider


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
