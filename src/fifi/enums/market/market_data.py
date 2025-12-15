from enum import Enum


class MarketData(Enum):
    CLOSE = 0
    OPEN = 1
    HIGH = 2
    LOW = 3
    VOL = 4
    TIME = 5
    PRICE = 6
    SELLER_VOL = 7
    BUYER_VOL = 8
    UNIQUE_TRADERS = 9
    BUYER_COUNT = 10
    SELLER_COUNT = 11
