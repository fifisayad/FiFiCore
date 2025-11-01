from ...enums.market import HealthStat
from ...helpers.get_logger import LoggerFactory
from .shm_base_repository import SHMBaseRepository, check_reader


class HealthDataRepository(SHMBaseRepository):
    def __init__(self, name: str, create: bool = False) -> None:
        self._name = name
        self.LOGGER = LoggerFactory().get(self._name)
        super().__init__(
            name=self._name, rows=1, columns=HealthStat.__len__(), create=create
        )

    def is_updated(self) -> bool:
        return bool(self._data[HealthStat.IS_UPDATED.value])

    @check_reader
    def set_is_updated(self) -> None:
        self._data[HealthStat.IS_UPDATED.value] = 1

    @check_reader
    def clear_is_updated(self) -> None:
        self._data[HealthStat.IS_UPDATED.value] = 0

    def get_time(self) -> None:
        return self._data[HealthStat.TIME.value]

    @check_reader
    def set_time(self, time: int) -> None:
        self._data[HealthStat.TIME.value] = time
