from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from gateway.coingecko_service import CoinGeckoAPIService


def make_service():
    settings = MagicMock()
    kafka_producer = MagicMock()
    logger = MagicMock()
    service = CoinGeckoAPIService(
        settings=settings,
        kafka_producer=kafka_producer,
        logger=logger,
    )
    return service, kafka_producer


def test_signal_to_stop():
    service, _ = make_service()
    assert service.must_stop is False
    service.signal_to_stop_execution()
    assert service.must_stop is True


def test_publish_to_kafka():
    service, kafka_producer = make_service()
    message = MagicMock()
    service.publish_to_kafka(message)
    kafka_producer.produce_message.assert_called_once_with(message)


@pytest.mark.asyncio
async def test_execute_does_nothing_when_stopped():
    service, kafka_producer = make_service()
    service.must_stop = True
    await service.execute()
    kafka_producer.produce_message.assert_not_called()


@pytest.mark.asyncio
async def test_execute_calls_coingecko_and_publishes():
    service, kafka_producer = make_service()
    mock_coin_data = MagicMock()

    with patch("gateway.coingecko_service.CoinGeckoClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.get_coins_price_py_id = AsyncMock(return_value=mock_coin_data)
        mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)

        await service.execute()

    kafka_producer.produce_message.assert_called_once_with(mock_coin_data)
