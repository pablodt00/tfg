from unittest.mock import ANY, AsyncMock, MagicMock, patch

from structlog.typing import FilteringBoundLogger

from gateway.coingecko_controller import CoinGeckoAPIController
from gateway.coingecko_service import CoinGeckoAPIService


def test_start():
    """Tests that the controller's started flag is set correctly."""
    service = MagicMock(spec=CoinGeckoAPIService)
    logger = MagicMock(spec=FilteringBoundLogger)
    controller = CoinGeckoAPIController(service, logger)

    assert not controller.started
    controller.start()
    assert controller.started


def test_stop():
    """Tests that the stop signal is correctly sent to the service."""
    service = MagicMock(spec=CoinGeckoAPIService)
    logger = MagicMock(spec=FilteringBoundLogger)
    controller = CoinGeckoAPIController(service, logger)

    controller.stop()

    service.signal_to_stop_execution.assert_called_once()


def test_execute_when_not_started():
    """Tests that an error is logged if execute is called before start."""
    service = MagicMock(spec=CoinGeckoAPIService)
    logger = MagicMock(spec=FilteringBoundLogger)
    controller = CoinGeckoAPIController(service, logger)

    controller.execute()

    logger.error.assert_called_once_with(
        "CoinGeckoAPIController: Controller not initialized",
    )
    service.execute.assert_not_called()


def test_execute():
    """Tests the successful execution flow."""
    service = MagicMock(spec=CoinGeckoAPIService)
    service.execute = AsyncMock()
    logger = MagicMock(spec=FilteringBoundLogger)
    controller = CoinGeckoAPIController(service, logger)

    with patch("gateway.coingecko_controller.asyncio.run") as asyncio_run_mock:
        controller.start()
        controller.execute()

        service.execute.assert_called_once()
        asyncio_run_mock.assert_called_once_with(ANY)


def test_execute_with_runtime_error():
    """Tests that a RuntimeError during service execution is caught and logged."""
    service = MagicMock(spec=CoinGeckoAPIService)
    service.execute = AsyncMock()
    logger = MagicMock(spec=FilteringBoundLogger)
    controller = CoinGeckoAPIController(service, logger)
    error_message = "test error"

    with patch(
        "gateway.coingecko_controller.asyncio.run",
        side_effect=RuntimeError(error_message),
    ) as asyncio_run_mock:
        controller.start()
        controller.execute()

        service.execute.assert_called_once()
        asyncio_run_mock.assert_called_once_with(ANY)
        logger.error.assert_called_once_with(
            "CoinGeckoAPIController: Error during service execution",
            error=error_message,
        )
