from pydantic import BaseModel, Field, field_validator
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
    period: int = 14
    timeframe: Literal["1m", "5m"] = "1m"

    @field_validator("period")
    def must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("period must be greater than 0")
        return v


IndicatorSubscriptionRequest = Annotated[
    Union[RSISubscriptionRequest],
    Field(discriminator="indicator"),
]
