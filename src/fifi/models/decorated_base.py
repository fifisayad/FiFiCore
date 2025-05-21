from typing import Set
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase


class DecoratedBase(AsyncAttrs, DeclarativeBase):
    def to_dict(self, exclude: Set = set()):
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
            if column not in exclude
        }
