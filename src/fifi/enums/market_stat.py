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
    ATR14 = 6
    ATR7 = 7
    ATR5 = 8
