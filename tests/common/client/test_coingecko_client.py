# pylint: disable=protected-access
from unittest.mock import AsyncMock, MagicMock

import pytest

from common.client.coingecko_client import CoinGeckoClient, CoinGeckoEndpoints
from common.client.exceptions import (
    CoinGeckoMissingAPIKeyError,
    CoinGeckoMissingBaseURLError,
)


def make_settings(api_key="test-key", base_url="https://api.coingecko.com", timeout=10):
    s = MagicMock()
    s.COINGECKO_API_KEY = api_key
    s.COINGECKO_BASE_URL = base_url
    s.COINGECKO_TIMEOUT = timeout
    return s


def test_client_raises_on_missing_api_key():
    settings = make_settings(api_key="")
    with pytest.raises(CoinGeckoMissingAPIKeyError):
        CoinGeckoClient(settings=settings)


def test_client_raises_on_missing_base_url():
    settings = make_settings(base_url="")
    with pytest.raises(CoinGeckoMissingBaseURLError):
        CoinGeckoClient(settings=settings)


def test_client_headers():
    settings = make_settings(api_key="my-api-key")
    client = CoinGeckoClient(settings=settings)
    headers = client._headers()
    assert headers["x-cg-demo-api-key"] == "my-api-key"
    assert headers["Accept"] == "application/json"


def test_coingecko_endpoints_init():
    endpoints = CoinGeckoEndpoints()
    assert endpoints.ping_endpoint is not None
    assert endpoints.coin_price_by_id_endpoint is not None


@pytest.mark.asyncio
async def test_ping_returns_response():
    settings = make_settings()
    mock_http = AsyncMock()
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"gecko_says": "(V3) To the Moon!"}
    mock_http.request = AsyncMock(return_value=mock_response)

    client = CoinGeckoClient(settings=settings, client=mock_http)
    result = await client.ping()
    assert result == {"gecko_says": "(V3) To the Moon!"}


@pytest.mark.asyncio
async def test_context_manager():
    settings = make_settings()
    mock_http = AsyncMock()
    async with CoinGeckoClient(settings=settings, client=mock_http) as c:
        assert c is not None
