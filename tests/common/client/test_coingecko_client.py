# pylint: disable=redefined-outer-name
import pytest

from common.client.coingecko_client import CoinGeckoClient
from common.client.endpoints.coin_price_by_id import CoinPriceByIdEndpoint
from common.config.settings import Settings


@pytest.fixture
def coingecko_client():
    return CoinGeckoClient(settings=Settings())


@pytest.mark.asyncio
async def test_ping_endpoint(coingecko_client):
    async with coingecko_client as client:
        response = await client.ping()
        assert response == {"gecko_says": "(V3) To the Moon!"}


@pytest.mark.asyncio
async def test_coin_price_by_id_endpoint(coingecko_client):
    async with coingecko_client as client:
        response = await client.get_coins_price_py_id(
            coin_price_data=CoinPriceByIdEndpoint.get_default_request(),
        )

        assert response.btc is not None
