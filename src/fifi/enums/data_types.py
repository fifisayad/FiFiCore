from enum import Enum


class DataType(str, Enum):
    INFO = "info"
    TRADES = "trades"
    ORDERBOOK = "orderbook"
    CANDLE = "candle"
