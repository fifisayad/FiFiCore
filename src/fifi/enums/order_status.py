from enum import Enum


class OrderStatus(Enum):
    ACTIVE = "active"
    FILLED = "filled"
    CANCELED = "canceled"
