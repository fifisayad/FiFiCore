import numpy as np
from typing import Optional

from ...enums.market import MarketData
from ...enums import Market
from ...types.market import intervals_type
from ...helpers.get_logger import LoggerFactory
from .shm_base_repository import SHMBaseRepository, check_reader
from .health_data_repository import HealthDataRepository


class MarketDataRepository(SHMBaseRepository):
    def __init__(
        self,
        market: Market,
        interval: intervals_type,
        create: bool = False,
        rows: int = 200,
    ) -> None:
        super().__init__(
            name=f"market_data_{market.value}_{interval}",
            rows=rows,
            columns=MarketData.__len__(),
            create=create,
        )
        self._health_name = f"market_health_data_{market.value}_{interval}"
        self.health = HealthDataRepository(name=self._health_name, create=create)
        self.LOGGER = LoggerFactory().get(self._name)

    def extract_data(self, _from: Optional[int] = None, _to: Optional[int] = None):
        data = self._data
        if _from:
            data = data[_from:]
        if _to:
            data = data[:_to]
        return data

    def get_closes(
        self, _from: Optional[int] = None, _to: Optional[int] = None
    ) -> np.ndarray:
        data = self.extract_data(_from, _to)
        return data[:, MarketData.CLOSE.value]

    def get_highs(
        self, _from: Optional[int] = None, _to: Optional[int] = None
    ) -> np.ndarray:
        data = self.extract_data(_from, _to)
        return data[:, MarketData.HIGH.value]

    def get_lows(
        self, _from: Optional[int] = None, _to: Optional[int] = None
    ) -> np.ndarray:
        data = self.extract_data(_from, _to)
        return data[:, MarketData.LOW.value]

    def get_opens(
        self, _from: Optional[int] = None, _to: Optional[int] = None
    ) -> np.ndarray:
        data = self.extract_data(_from, _to)
        return data[:, MarketData.OPEN.value]

    def get_vols(
        self, _from: Optional[int] = None, _to: Optional[int] = None
    ) -> np.ndarray:
        data = self.extract_data(_from, _to)
        return data[:, MarketData.VOL.value]

    def get_last_trade(self) -> float:
        return self._data[-1, MarketData.PRICE.value]

    def get_time(self) -> float:
        return self._data[-1, MarketData.TIME.value]

    @check_reader
    def create_new_candle(self) -> None:
        self._data[0].fill(0)
        self._data = np.roll(self._data, shift=-1, axis=0)

    @check_reader
    def set_close_price(self, price: float) -> None:
        self._data[-1, MarketData.CLOSE.value] = price

    @check_reader
    def set_open_price(self, price: float) -> None:
        self._data[-1, MarketData.OPEN.value] = price

    @check_reader
    def set_low_price(self, price: float) -> None:
        self._data[-1, MarketData.LOW.value] = price

    @check_reader
    def set_high_price(self, price: float) -> None:
        self._data[-1, MarketData.HIGH.value] = price

    @check_reader
    def set_last_trade(self, price: float) -> None:
        self._data[-1, MarketData.PRICE.value] = price

    @check_reader
    def set_time(self, time: float) -> None:
        self._data[-1, MarketData.TIME.value] = time
