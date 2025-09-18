from pydantic import BaseModel, Field
from typing import Union, Annotated, Literal

from ..enums.exchanges import Exchange
from ..enums.markets import Market
from ..enums.indicators import IndicatorType


# --- Indicator Subscribe ---
class BaseIndicatorRequest(BaseModel):
    exchange: Exchange
    market: Market
    indicator: IndicatorType


# --- RSI specific ---
class RSISubscriptionRequest(BaseIndicatorRequest):
    indicator: Literal[IndicatorType.RSI]
    period: Literal[5, 10, 14] = 14
    timeframe: Literal["1m", "5m"] = "1m"


IndicatorSubscriptionRequest = Annotated[
    Union[RSISubscriptionRequest],
    Field(discriminator="indicator"),
]
