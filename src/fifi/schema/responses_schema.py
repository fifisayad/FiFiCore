from typing import List, Dict, Any, Literal
from pydantic import BaseModel

from ..enums.data_types import DataType


# --- Response Schema ---
class SubscriptionResponseSchema(BaseModel):
    channel: str


class CandleResponseSchema(BaseModel):
    type: str
    response: List[Dict[str, Any]]


class PublishDataSchema(BaseModel):
    data: dict
    type: DataType
    timeframe: Literal["1m", "5m"] = "1m"
