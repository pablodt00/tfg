from datetime import datetime
from enum import Enum

from pydantic import Field

from common.schemas.base import ORMBaseSchema


class AlertConditionEnum(str, Enum):
    GREATER_THAN_OR_EQUAL = "GREATER_THAN_OR_EQUAL"
    LESS_THAN_OR_EQUAL = "LESS_THAN_OR_EQUAL"

    def __str__(self) -> str:
        return self.value


class Alert(ORMBaseSchema):
    id: int | None = None
    coin: str
    condition: AlertConditionEnum
    amount: float
    triggered: bool = Field(default=False)
    user_email: str
    created_at: datetime = Field(default_factory=datetime.now)

    @classmethod
    def from_alert(
        cls, coin: str, condition: AlertConditionEnum, user_email: str, amount: float
    ):
        return cls(
            coin=coin,
            condition=condition,
            user_email=user_email,
            amount=amount,
        )
