from datetime import datetime
from enum import Enum

from pydantic import Field

from common.schemas.base import ORMBaseSchema


class CoinEnum(str, Enum):
    BTC = "btc"
    ETH = "eth"
    USDT = "usdt"
    BNB = "bnb"
    XRP = "xrp"
    SOL = "sol"
    USDC = "usdc"
    DOGE = "doge"
    ADA = "ada"
    DOT = "dot"

    def __str__(self) -> str:
        return self.value


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
