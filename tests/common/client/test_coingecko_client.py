import pytest

from common.client.coingecko_client import CoinGeckoClient
#from common.client.endpoints.coin_price_by_id import CoinPriceByIdEndpoint
from common.config.settings import Settings


@pytest.mark.asyncio
async def test_ping_endpoint():
    client = CoinGeckoClient(
        Settings(),
    )

    assert await client.ping() == {'gecko_says': '(V3) To the Moon!'}

# @pytest.mark.asyncio
# async def test_coin_price_by_id_endpoint():
#     client = CoinGeckoClient(
#         Settings(),
#     )
#
#     response = await client.get_coins_price_py_id(
#         coin_price_data=CoinPriceByIdEndpoint.get_default_request()
#     )
