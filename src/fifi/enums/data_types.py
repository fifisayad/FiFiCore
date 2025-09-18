from enum import Enum


class DataType(Enum):
    INFO = "info"
    TRADES = "trades"
    ORDERBOOK = "orderbook"
    CANDLE = "candle"
