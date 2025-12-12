from unittest.mock import MagicMock, call, patch

from structlog.typing import FilteringBoundLogger

from common.config.settings import Settings
from common.daemons.heartbeat_handler import make_heartbeat_handler
from gateway import coingecko_base_daemon
from gateway.coingecko_base_daemon import CoinGeckoBaseDaemon
from gateway.coingecko_controller import CoinGeckoAPIController


def test_start():
    settings = Settings()
    controller = MagicMock(spec=CoinGeckoAPIController)
    heartbeat_handler = make_heartbeat_handler(settings=settings)
    logger = MagicMock(spec=FilteringBoundLogger)
    logger.bind.return_value = logger

    with patch("common.daemons.base_daemon.BaseDaemon.start") as super_start:
        daemon = CoinGeckoBaseDaemon(controller, heartbeat_handler, logger)
        daemon.start()

        logger.info.assert_called_with("CoinGeckoBaseDaemon: Starting daemon")
        assert controller.start.call_count == 1
        assert super_start.call_count == 1


def test_execute():
    settings = Settings()
    controller = MagicMock(spec=CoinGeckoAPIController)
    heartbeat_handler = make_heartbeat_handler(settings=settings)
    logger = MagicMock(spec=FilteringBoundLogger)
    logger.bind.return_value = logger

    coingecko_base_daemon.SLEEP_TIME_BETWEEN_RUNS_SECONDS = 1

    with patch("gateway.coingecko_base_daemon.time.sleep") as sleep_mock:
        daemon = CoinGeckoBaseDaemon(controller, heartbeat_handler, logger)
        daemon.execute()

        expected_calls = [
            call("CoinGeckoBaseDaemon: Executing task"),
            call("CoinGeckoBaseDaemon: Heartbeat signal sent"),
            call("CoinGeckoBaseDaemon: Sleeping before next execution"),
        ]
        logger.info.assert_has_calls(expected_calls)
        assert controller.execute.call_count == 1
        sleep_mock.assert_called_once_with(1)


def test_execute_with_exceptions():
    settings = Settings()
    controller = MagicMock(spec=CoinGeckoAPIController)
    heartbeat_handler = make_heartbeat_handler(settings=settings)
    logger = MagicMock(spec=FilteringBoundLogger)
    logger.bind.return_value = logger
    controller.execute.side_effect = BaseException("Some exception")

    coingecko_base_daemon.SLEEP_TIME_BETWEEN_RUNS_SECONDS = 1

    with patch("gateway.coingecko_base_daemon.time.sleep") as sleep_mock:
        daemon = CoinGeckoBaseDaemon(controller, heartbeat_handler, logger)
        daemon.execute()

        expected_calls = [
            call("CoinGeckoBaseDaemon: Executing task"),
            call("CoinGeckoBaseDaemon: Heartbeat signal sent"),
            call("CoinGeckoBaseDaemon: Sleeping before next execution"),
        ]
        logger.info.assert_has_calls(expected_calls)
        logger.exception.assert_called_once_with(
            "CoinGeckoBaseDaemon: Error during controller execution",
        )
        assert controller.execute.call_count == 1
        sleep_mock.assert_called_once_with(1)


def test_stop():
    settings = Settings()
    controller = MagicMock(spec=CoinGeckoAPIController)
    heartbeat_handler = make_heartbeat_handler(settings=settings)
    logger = MagicMock(spec=FilteringBoundLogger)
    logger.bind.return_value = logger

    with patch("common.daemons.base_daemon.BaseDaemon.stop") as super_stop:
        daemon = CoinGeckoBaseDaemon(controller, heartbeat_handler, logger)
        daemon.stop(15, None)

        expected_calls = [
            call("CoinGeckoBaseDaemon: Stopping daemon", signal_number=15),
            call("CoinGeckoBaseDaemon: Signalling controller to stop"),
        ]
        logger.info.assert_has_calls(expected_calls)
        assert controller.stop.call_count == 1
        super_stop.assert_called_once_with(15, None)


def test_heartbeat():
    controller = MagicMock(spec=CoinGeckoAPIController)
    heartbeat_handler = MagicMock()
    logger = MagicMock(spec=FilteringBoundLogger)
    logger.bind.return_value = logger

    daemon = CoinGeckoBaseDaemon(controller, heartbeat_handler, logger)
    daemon.heartbeat()

    logger.info.assert_called_with("CoinGeckoBaseDaemon: Heartbeat signal sent")
    assert heartbeat_handler.call_count == 1
