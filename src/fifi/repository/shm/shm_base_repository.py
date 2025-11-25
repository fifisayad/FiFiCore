from typing import Optional
import numpy as np
from functools import wraps
from sys import version_info
from multiprocessing.shared_memory import SharedMemory
from multiprocessing.resource_tracker import unregister

from ...helpers.get_logger import LoggerFactory


def check_reader(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if self._reader:
            raise Exception("Reader couldn't set the value!!!")
        return func(self, *args, **kwargs)

    return wrapper


class SHMBaseRepository:
    _name: str
    _data: np.ndarray
    _rows: int
    _columns: int
    _sm: SharedMemory
    _reader: bool
    health = None

    def __init__(
        self, name: str, rows: int, columns: int, create: bool = False
    ) -> None:
        self._name = name
        self.LOGGER = LoggerFactory().get(self._name)
        self._rows = rows
        self._columns = columns

        if create:
            self._reader = False
            try:
                self.create()
            except FileExistsError:
                self.connect()
                self.close()
                self.create()
        else:
            self._reader = True
            self.connect()

        # access to arrays
        try:
            self._data = np.ndarray(
                shape=(self._rows, self._columns),
                dtype=np.double,
                buffer=self._sm.buf,
            )
        except TypeError:
            self.LOGGER.error(
                f"It probably happens because of wrong configuration not same as Monitoring Service.."
            )
            raise
        # initial value
        if create:
            self._data.fill(0)

    def create(self) -> None:
        size = self._rows * self._columns * 8
        self._sm = SharedMemory(name=self._name, create=True, size=size)

    def connect(self) -> None:
        if version_info.major == 3 and version_info.minor <= 12:
            self._sm = SharedMemory(name=self._name)
            unregister(self._sm._name, "shared_memory")
        elif version_info.major == 3 and version_info.minor >= 13:
            self._sm = SharedMemory(name=self._name, track=False)

    def close(self) -> None:
        if self.health:
            self.health.close()
        self._sm.close()
        if not self._reader:
            self._sm.unlink()

    def new_row(self) -> None:
        self._data[0].fill(0)
        self._data[:] = np.roll(self._data, shift=-1, axis=0)

    def extract_data(self, _from: Optional[int] = None, _to: Optional[int] = None):
        data = self._data
        if _from and _to:
            data = data[_from:_to]
        elif _from:
            data = data[_from:]
        elif _to:
            data = data[:_to]
        return data
