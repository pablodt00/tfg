from datetime import datetime

from common.schemas.coin import Coin, CoinEnum


def test_coin_enum_values():
    assert CoinEnum.BTC == "btc"
    assert CoinEnum.ETH == "eth"
    assert str(CoinEnum.BTC) == "btc"


def test_coin_from_coin_factory():
    coin = Coin.from_coin(coin="btc", last_price=50000.0, base_price=49000.0)
    assert coin.coin == "btc"
    assert coin.last_price == 50000.0
    assert coin.base_price == 49000.0
    assert coin.id is None


def test_coin_schema_fields():
    coin = Coin(coin="eth", last_price=3000.0, base_price=2900.0)
    assert coin.price_1_min_change_percent is None
    assert coin.price_5_min_change_percent is None
    assert isinstance(coin.base_timestamp, datetime)
    assert isinstance(coin.updated_at, datetime)
