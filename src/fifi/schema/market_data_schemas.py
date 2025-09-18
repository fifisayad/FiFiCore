from pydantic import BaseModel, Field

from ..enums.exchanges import Exchange
from ..enums.markets import Market
from ..enums.data_types import DataType

from typing import List, Dict, Any, Union, Annotated, Literal


# --- Market Subscribe ---
class MarketSubscriptionBase(BaseModel):
    exchange: Exchange
    market: Market
    data_type: DataType


class NonCandleSubscription(MarketSubscriptionBase):
    data_type: Literal[DataType.TRADES, DataType.ORDERBOOK]


class CandleSubscription(MarketSubscriptionBase):
    data_type: Literal[DataType.CANDLE]
    timeframe: Literal["1m", "5m"]


MarketSubscriptionRequestSchema = Annotated[
    Union[CandleSubscription, NonCandleSubscription],
    Field(discriminator="data_type"),
]
