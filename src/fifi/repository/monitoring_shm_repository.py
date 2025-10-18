import numpy as np
from sys import version_info
from multiprocessing.shared_memory import SharedMemory
from multiprocessing.resource_tracker import unregister
from typing import Any, Dict, List

from ..enums import Market, MarketStat, Candle
from ..helpers.get_logger import LoggerFactory

LOGGER = LoggerFactory().get(__name__)


class MonitoringSHMRepository:
    stat_name: str = "market_stat"
    stats: np.ndarray
    stats_length: int
    stats_sm: SharedMemory
    candles_name: str = "candle_data"
    candles: np.ndarray
    candles_length: int = 200
    candles_specs_length: int
    candles_sm: SharedMemory
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
        self.candles_specs_length = Candle.__len__()

        if create:
            self.reader = False
            try:
                self.create_stat_shm()
            except FileExistsError:
                self.connect_stat_shm()
                self.close_stat()
                self.create_stat_shm()
            try:
                self.create_candles_shm()
            except FileExistsError:
                self.connect_candles_shm()
                self.close_candles()
                self.create_candles_shm()
        else:
            self.reader = True
            self.connect_stat_shm()
            self.connect_candles_shm()

        # access to arrays
        try:
            self.stats = np.ndarray(
                shape=(len(markets), self.stats_length),
                dtype=np.double,
                buffer=self.stats_sm.buf,
            )
            self.candles = np.ndarray(
                shape=(len(markets), self.candles_specs_length, self.candles_length),
                dtype=np.double,
                buffer=self.candles_sm.buf,
            )
        except TypeError:
            LOGGER.error(
                f"It probably happens because of markets configuration not equalt to monitoring service...."
            )
            raise
        # initial value
        if create:
            self.stats.fill(0)
            self.candles.fill(0)

    def create_stat_shm(self) -> None:
        stat_size = len(self.row_index) * self.stats_length * 8
        self.stats_sm = SharedMemory(name=self.stat_name, create=True, size=stat_size)

    def create_candles_shm(self) -> None:
        candles_size = (
            len(self.row_index) * self.candles_specs_length * self.candles_length * 8
        )
        self.candles_sm = SharedMemory(
            name=self.candles_name, create=True, size=candles_size
        )

    def connect_stat_shm(self) -> None:
        if version_info.major == 3 and version_info.minor <= 12:
            self.stats_sm = SharedMemory(name=self.stat_name)
            unregister(self.stats_sm._name, "shared_memory")
        elif version_info.major == 3 and version_info.minor >= 13:
            self.stats_sm = SharedMemory(name=self.stat_name, track=False)

    def connect_candles_shm(self) -> None:
        if version_info.major == 3 and version_info.minor <= 12:
            self.candles_sm = SharedMemory(name=self.candles_name)
            unregister(self.candles_sm._name, "shared_memory")
        elif version_info.major == 3 and version_info.minor >= 13:
            self.candles_sm = SharedMemory(name=self.candles_name, track=False)

    def close(self) -> None:
        self.close_candles()
        self.close_stat()

    def close_candles(self) -> None:
        self.candles_sm.close()
        if not self.reader:
            self.candles_sm.unlink()

    def close_stat(self) -> None:
        self.stats_sm.close()
        if not self.reader:
            self.stats_sm.unlink()

    def get_candles(self, market: Market) -> np.ndarray:
        return self.candles[self.row_index[market]]

    def set_candles(self, market: Market, candles: np.ndarray) -> None:
        if self.reader:
            raise Exception("Reader couldn't set the value!!!")
        self.candles[self.row_index[market]] = candles

    def get_close_prices(self, market: Market) -> np.ndarray:
        return self.candles[self.row_index[market]][Candle.CLOSE.value]

    def set_close_prices(self, market: Market, close_prices: np.ndarray) -> None:
        if self.reader:
            raise Exception("Reader couldn't set the value!!!")
        self.candles[self.row_index[market]][Candle.CLOSE.value] = close_prices

    def get_open_prices(self, market: Market) -> np.ndarray:
        return self.candles[self.row_index[market]][Candle.OPEN.value]

    def set_open_prices(self, market: Market, open_prices: np.ndarray) -> None:
        if self.reader:
            raise Exception("Reader couldn't set the value!!!")
        self.candles[self.row_index[market]][Candle.OPEN.value] = open_prices

    def get_high_prices(self, market: Market) -> np.ndarray:
        return self.candles[self.row_index[market]][Candle.HIGH.value]

    def set_high_prices(self, market: Market, high_prices: np.ndarray) -> None:
        if self.reader:
            raise Exception("Reader couldn't set the value!!!")
        self.candles[self.row_index[market]][Candle.HIGH.value] = high_prices

    def get_low_prices(self, market: Market) -> np.ndarray:
        return self.candles[self.row_index[market]][Candle.LOW.value]

    def set_low_prices(self, market: Market, low_prices: np.ndarray) -> None:
        if self.reader:
            raise Exception("Reader couldn't set the value!!!")
        self.candles[self.row_index[market]][Candle.LOW.value] = low_prices

    def get_vols(self, market: Market) -> np.ndarray:
        return self.candles[self.row_index[market]][Candle.VOL.value]

    def set_vols(self, market: Market, vols: np.ndarray) -> None:
        if self.reader:
            raise Exception("Reader couldn't set the value!!!")
        self.candles[self.row_index[market]][Candle.VOL.value] = vols

    def get_stat(self, market: Market, stat: MarketStat) -> Any:
        return self.stats[self.row_index[market]][stat.value]

    def set_stat(self, market: Market, stat: MarketStat, value: Any) -> None:
        if self.reader:
            raise Exception("Reader couldn't set the value!!!")
        self.stats[self.row_index[market]][stat.value] = value

    def get_current_candle_time(self, market: Market) -> Any:
        return self.stats[self.row_index[market]][MarketStat.CANDLE_TIME.value]

    def set_current_candle_time(self, market: Market, value: Any) -> None:
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
