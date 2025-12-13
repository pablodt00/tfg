# pylint: disable=redefined-outer-name
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from gateway.coingecko_service import CoinGeckoAPIService


@pytest.fixture
def mock_settings():
    return MagicMock()


@pytest.fixture
def mock_logger():
    return MagicMock()


@pytest.fixture
def service(mock_settings, mock_logger):
    return CoinGeckoAPIService(
        settings=mock_settings,
        logger=mock_logger,
    )


def test_initialization(service, mock_settings, mock_logger):
    assert service.settings is mock_settings
    assert service.logger is mock_logger
    assert not service.must_stop


def test_signal_to_stop_execution(service):
    assert not service.must_stop
    service.signal_to_stop_execution()
    assert service.must_stop


@pytest.mark.asyncio
@patch("gateway.coingecko_service.CoinGeckoClient")
async def test_execute_stops_when_signaled(mock_client_class, service, mock_logger):
    service.signal_to_stop_execution()
    await service.execute()
    mock_logger.debug.assert_called_with("CoinGeckoAPIService: Clean stop")
    mock_client_class.assert_not_called()


@pytest.mark.asyncio
@patch("gateway.coingecko_service.CoinGeckoClient")
async def test_execute_success(mock_client_class, service, mock_logger):
    mock_client_instance = AsyncMock()
    mock_client_instance.get_coins_price_py_id.return_value = {
        "bitcoin": {"usd": 50000}
    }
    mock_client_class.return_value.__aenter__.return_value = mock_client_instance

    await service.execute()

    mock_client_instance.get_coins_price_py_id.assert_awaited_once()
    mock_logger.info.assert_any_call(
        "CoinGeckoAPIService: Successfully retrieved data from CoinGecko API",
        data={"bitcoin": {"usd": 50000}},
    )


@pytest.mark.asyncio
@patch("gateway.coingecko_service.CoinGeckoClient")
async def test_execute_exception(mock_client_class, service, mock_logger):
    test_exception = Exception("API Error")
    mock_client_instance = AsyncMock()
    mock_client_instance.get_coins_price_py_id.side_effect = test_exception
    mock_client_class.return_value.__aenter__.return_value = mock_client_instance

    with pytest.raises(Exception, match="API Error"):
        await service.execute()

    mock_logger.exception.assert_called_with(
        "CoinGeckoAPIService: Error calling CoinGecko API"
    )
