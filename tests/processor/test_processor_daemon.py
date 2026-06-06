# pylint: disable=too-many-arguments, too-many-positional-arguments
from unittest.mock import MagicMock, patch

from processor.processor_daemon import execute


@patch("processor.processor_daemon.build_processor_daemon")
@patch("processor.processor_daemon.ProcessorService")
@patch("processor.processor_daemon.AlertRepository")
@patch("processor.processor_daemon.CoinRepository")
@patch("processor.processor_daemon.make_session_factory")
@patch("processor.processor_daemon.make_engine")
@patch("processor.processor_daemon.Settings")
def test_execute_builds_app(
    mock_settings_cls,
    mock_make_engine,
    mock_make_session_factory,
    _mock_coin_repo_cls,
    _mock_alert_repo_cls,
    mock_processor_service_cls,
    mock_build_processor_daemon,
):
    mock_settings = MagicMock()
    mock_settings.db_uri_as_string = "postgresql+asyncpg://user:pass@host/db"
    mock_settings_cls.return_value = mock_settings

    mock_app = MagicMock()
    mock_build_processor_daemon.return_value = mock_app

    result = execute()

    mock_settings_cls.assert_called_once()
    mock_make_engine.assert_called_once_with(db_uri=mock_settings.db_uri_as_string)
    mock_make_session_factory.assert_called_once()
    mock_processor_service_cls.assert_called_once()
    mock_build_processor_daemon.assert_called_once()
    assert result is mock_app
