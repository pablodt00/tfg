# pylint: disable=redefined-outer-name
from unittest.mock import AsyncMock, MagicMock

import pytest

from gateway.coingecko_service import CoinGeckoAPIService


@pytest.fixture
def mock_settings():
    return MagicMock()


@pytest.fixture
def mock_coingecko_client():
    return MagicMock()


@pytest.fixture
def mock_logger():
    return MagicMock()


@pytest.fixture
def service(mock_settings, mock_coingecko_client, mock_logger):
    return CoinGeckoAPIService(
        settings=mock_settings,
        coingecko_client=mock_coingecko_client,
        logger=mock_logger,
    )


def test_initialization(service, mock_settings, mock_coingecko_client, mock_logger):
    assert service.settings is mock_settings
    assert service.client is mock_coingecko_client
    assert service.logger is mock_logger
    assert not service.must_stop


def test_signal_to_stop_execution(service):
    assert not service.must_stop
    service.signal_to_stop_execution()
    assert service.must_stop


@pytest.mark.asyncio
async def test_execute_stops_when_signaled(service, mock_logger, mock_coingecko_client):
    service.signal_to_stop_execution()
    await service.execute()
    mock_logger.debug.assert_called_with("CoinGeckoAPIService: Clean stop")
    mock_coingecko_client.get_coins_price_py_id.assert_not_called()


@pytest.mark.asyncio
async def test_execute_success(service, mock_coingecko_client, mock_logger):
    mock_coingecko_client.get_coins_price_py_id = AsyncMock(
        return_value={"bitcoin": {"usd": 50000}}
    )
    await service.execute()
    mock_coingecko_client.get_coins_price_py_id.assert_awaited_once()
    mock_logger.info.assert_any_call(
        "CoinGeckoAPIService: Successfully retrieved data from CoinGecko API",
        data={"bitcoin": {"usd": 50000}},
    )


@pytest.mark.asyncio
async def test_execute_exception(service, mock_coingecko_client, mock_logger):
    test_exception = Exception("API Error")
    mock_coingecko_client.get_coins_price_py_id = AsyncMock(side_effect=test_exception)

    with pytest.raises(Exception, match="API Error"):
        await service.execute()

    mock_logger.exception.assert_called_with(
        "CoinGeckoAPIService: Error calling CoinGecko API"
    )
