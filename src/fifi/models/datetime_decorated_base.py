from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column

from ..helpers.get_current_time import GetCurrentTime
from ..models.decorated_base import DecoratedBase


class DatetimeDecoratedBase(DecoratedBase):
    __abstract__ = True
    updated_at: Mapped[datetime] = mapped_column(
        index=True,
        doc="Last Update Time",
        default=GetCurrentTime.get,
        onupdate=GetCurrentTime.get,
    )
    created_at: Mapped[datetime] = mapped_column(
        index=True, doc="Creation Time", default=GetCurrentTime.get
    )
