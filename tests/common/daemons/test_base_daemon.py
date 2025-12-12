# pylint: disable=redefined-outer-name
import signal
from unittest import mock

import pytest

from common.daemons.base_daemon import BaseDaemon


@pytest.fixture
def daemon():
    with mock.patch("signal.signal") as mock_signal:
        daemon_instance = BaseDaemon()
        daemon_instance.logger = mock.Mock()
        daemon_instance.mock_signal = mock_signal
        yield daemon_instance


def test_init_sets_signal_handlers(daemon):
    calls = [
        mock.call(signal.SIGINT, daemon.stop),
        mock.call(signal.SIGTERM, daemon.stop),
    ]
    daemon.mock_signal.assert_has_calls(calls, any_order=True)
    assert daemon.mock_signal.call_count == 2


def test_stop_method(daemon):
    assert daemon.rerun is True
    test_signum = signal.SIGTERM
    daemon.stop(test_signum, None)
    assert daemon.rerun is False
    daemon.logger.info.assert_called_once_with(
        "%s: Stop signal received. Signal: %s.", "BaseDaemon", test_signum
    )


def test_execute_raises_not_implemented_error(daemon):
    with pytest.raises(NotImplementedError, match="Method execute not overridden"):
        daemon.execute()


def test_start_loop(daemon):
    daemon.execute = mock.Mock(side_effect=lambda: setattr(daemon, "rerun", False))

    daemon.start()

    daemon.logger.info.assert_called_once_with("%s: Daemon started.", "BaseDaemon")
    daemon.execute.assert_called_once()
