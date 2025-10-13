import numpy as np
from multiprocessing.shared_memory import SharedMemory
from typing import Any, Dict, List

from ..enums import Market
from ..enums import MarketStat


class MonitoringSHMRepository:
    stat_name: str = "market_stat"
    stats: np.ndarray
    stats_length: int
    stats_sm: SharedMemory
    close_prices_name: str = "close_prices_data"
    close_prices: np.ndarray
    close_prices_length: int = 200
    close_prices_sm: SharedMemory
    reader: bool

    row_index: Dict[Market, int]

    def __init__(
        self, create: bool = False, markets: List[Market] = [Market.BTCUSD_PERP]
    ) -> None:
        # init row index
        self.row_index = dict()
        for i in range(len(markets)):
            self.row_index[markets[i]] = i
        self.stats_length = MarketStat.__len__()

        if create:
            self.reader = False
            try:
                self.create_stat_shm()
            except FileExistsError:
                self.connect_stat_shm()
                self.close_stat()
                self.create_stat_shm()
            try:
                self.create_close_prices_shm()
            except FileExistsError:
                self.connect_close_prices_shm()
                self.close_close_prices()
                self.create_close_prices_shm()
        else:
            self.reader = True
            self.connect_stat_shm()
            self.connect_close_prices_shm()

        # access to arrays
        self.stats = np.ndarray(
            shape=(len(markets), self.stats_length),
            dtype=np.double,
            buffer=self.stats_sm.buf,
        )
        self.close_prices = np.ndarray(
            shape=(len(markets), self.close_prices_length),
            dtype=np.double,
            buffer=self.close_price_sm.buf,
        )
        # initial value
        if create:
            self.stats.fill(0)
            self.close_prices.fill(0)

    def create_stat_shm(self) -> None:
        stat_size = len(self.row_index) * self.stats_length * 8
        self.stats_sm = SharedMemory(name=self.stat_name, create=True, size=stat_size)

    def create_close_prices_shm(self) -> None:
        close_prices_size = len(self.row_index) * self.close_prices_length * 8
        self.close_price_sm = SharedMemory(
            name=self.close_prices_name, create=True, size=close_prices_size
        )

    def connect_stat_shm(self) -> None:
        self.stats_sm = SharedMemory(name=self.stat_name)

    def connect_close_prices_shm(self) -> None:
        self.close_price_sm = SharedMemory(name=self.close_prices_name)

    def close(self) -> None:
        self.close_close_prices()
        self.close_stat()

    def close_close_prices(self) -> None:
        self.close_price_sm.close()
        self.close_price_sm.unlink()

    def close_stat(self) -> None:
        self.stats_sm.close()
        self.stats_sm.unlink()

    def get_close_prices(self, market: Market) -> np.ndarray:
        return self.close_prices[self.row_index[market]]

    def set_close_prices(self, market: Market, close_prices: np.ndarray) -> None:
        if self.reader:
            raise Exception("Reader couldn't set the value!!!")
        self.close_prices[self.row_index[market]] = close_prices

    def get_stat(self, market: Market, stat: MarketStat) -> Any:
        return self.stats[self.row_index[market]][stat.value]

    def set_stat(self, market: Market, stat: MarketStat, value: Any) -> None:
        if self.reader:
            raise Exception("Reader couldn't set the value!!!")
        self.stats[self.row_index[market]][stat.value] = value

    def get_current_candle(self, market: Market) -> Any:
        return self.stats[self.row_index[market]][MarketStat.CANDLE_TIME.value]

    def set_current_candle(self, market: Market, value: Any) -> None:
        if self.reader:
            raise Exception("Reader couldn't set the value!!!")
        self.stats[self.row_index[market]][MarketStat.CANDLE_TIME.value] = value

    def get_last_trade(self, market: Market) -> Any:
        return self.stats[self.row_index[market]][MarketStat.PRICE.value]

    def set_last_trade(self, market: Market, value: Any) -> None:
        if self.reader:
            raise Exception("Reader couldn't set the value!!!")
        self.stats[self.row_index[market]][MarketStat.PRICE.value] = value

    def is_updated(self, market: Market) -> bool:
        return bool(self.stats[self.row_index[market]][MarketStat.IS_UPDATED.value])

    def set_is_updated(self, market: Market) -> None:
        if self.reader:
            raise Exception("Reader couldn't set the value!!!")
        self.stats[self.row_index[market]][MarketStat.IS_UPDATED.value] = 1

    def clear_is_updated(self, market: Market) -> None:
        if self.reader:
            raise Exception("Reader couldn't set the value!!!")
        self.stats[self.row_index[market]][MarketStat.IS_UPDATED.value] = 0
