import pytest

from common.client.coingecko_client import CoinGeckoClient
from common.client.endpoints.coin_price_by_id import CoinPriceByIdParams, CoinPriceByIdEndpoint
from common.config.settings import Settings


@pytest.fixture(scope="module")
def settings():
    return Settings()

@pytest.fixture
def coingecko_client(settings):
    # Ensure API key and base URL are loaded from environment for integration tests
    if not settings.COINGECKO_API_KEY or not settings.COINGECKO_BASE_URL:
        pytest.skip("COINGECKO_API_KEY and COINGECKO_BASE_URL must be set for integration tests")
    return CoinGeckoClient(settings=settings)


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
