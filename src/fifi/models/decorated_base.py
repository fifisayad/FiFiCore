from typing import Set
import uuid
from sqlalchemy import String
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class DecoratedBase(AsyncAttrs, DeclarativeBase):
    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )

    def to_dict(self, exclude: Set = set()):
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
            if column not in exclude
        }
