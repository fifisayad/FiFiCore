from enum import Enum


class Market(Enum):
    BTCUSD = "btcusd"
    ETHUSD = "ethusd"
    BTCUSD_PERP = "btcusd_perp"
    ETHUSD_PERP = "ethusd_perp"

    def is_perptual(self) -> bool:
        if "perp" in self.value:
            return True
        return False
