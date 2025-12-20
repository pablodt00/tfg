from datetime import datetime

from pydantic import Field

from common.schemas.base import ORMBaseSchema


class Coin(ORMBaseSchema):
    id: int | None = None
    coin: str
    last_price: float
    base_price: float
    price_1_min_change_percent: float | None = None
    price_5_min_change_percent: float | None = None
    base_timestamp: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    @classmethod
    def from_coin(cls, coin: str, last_price: float, base_price: float):
        return cls(
            coin=coin,
            last_price=last_price,
            base_price=base_price,
        )
