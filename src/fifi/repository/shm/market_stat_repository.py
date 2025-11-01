import numpy as np
from typing import Optional

from ...enums.market import MarketStat
from ...enums import Market
from ...types.market import intervals_type
from ...helpers.get_logger import LoggerFactory
from .shm_base_repository import SHMBaseRepository, check_reader
from .health_data_repository import HealthDataRepository


class MarketStatRepository(SHMBaseRepository):
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
            columns=MarketStat.__len__(),
            create=create,
        )
        self._health_name = f"market_stat_health_{market.value}_{interval}"
        self.health = HealthDataRepository(name=self._health_name, create=create)
        self.LOGGER = LoggerFactory().get(self._name)

    def get_last_stat(self, stat: MarketStat) -> float:
        return self._data[-1, stat.value]

    def get_stat(
        self, stat: MarketStat, _from: Optional[int], _to: Optional[int]
    ) -> np.ndarray:
        data = self.extract_data(_from, _to)
        return data[:, stat.value]

    def set_last_stat(self, stat: MarketStat, value: float) -> None:
        self._data[-1, stat.value] = value

    def create_candle(self):
        self.new_row()

    def get_time(self) -> float:
        return self._data[-1, MarketStat.TIME.value]

    @check_reader
    def set_time(self, time: float) -> None:
        self._data[-1, MarketStat.TIME.value] = time
