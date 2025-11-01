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
            self.reader = True
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
        stat_size = self._rows * self._columns * 8
        self._sm = SharedMemory(name=self._name, create=True, size=stat_size)

    def connect(self) -> None:
        if version_info.major == 3 and version_info.minor <= 12:
            self._sm = SharedMemory(name=self._name)
            unregister(self._sm._name, "shared_memory")
        elif version_info.major == 3 and version_info.minor >= 13:
            self._sm = SharedMemory(name=self._name, track=False)

    def close(self) -> None:
        self._sm.close()
        if not self.reader:
            self._sm.unlink()

    def extract_data(self, _from: Optional[int] = None, _to: Optional[int] = None):
        data = self._data
        if _from:
            data = data[_from:]
        if _to:
            data = data[:_to]
        return data
