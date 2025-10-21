from enum import Enum


class MarketStat(Enum):
    # last trade
    IS_UPDATED = 0
    PRICE = 1
    CANDLE_TIME = 2
    # indicators
    RSI14 = 3
    RSI7 = 4
    RSI5 = 5
    RSI3 = 6
    ATR14 = 7
    ATR7 = 8
    ATR5 = 9
    ATR3 = 10
    HMA = 11
