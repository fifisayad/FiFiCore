from enum import Enum


class IndicatorType(str, Enum):
    RSI = "rsi"
    MACD = "macd"
    SMA = "sma"
