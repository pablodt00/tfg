from unittest.mock import MagicMock, patch

from app.webapp_daemon import (
    COIN_NAME_TO_SYMBOL,
    DEFAULT_COINS_DATA,
    fetch_coins_data,
    fetch_coins_raw,
    send_alert,
    _change_color,
)


def test_coin_name_to_symbol_contains_bitcoin():
    assert "Bitcoin" in COIN_NAME_TO_SYMBOL
    assert COIN_NAME_TO_SYMBOL["Bitcoin"] == "btc"


def test_default_coins_data_has_all_coins():
    assert len(DEFAULT_COINS_DATA["Name"]) == len(COIN_NAME_TO_SYMBOL)


def test_default_coins_data_placeholders():
    assert all(v == "-" for v in DEFAULT_COINS_DATA["Last Price (€)"])
    assert all(v == "-" for v in DEFAULT_COINS_DATA["Price Change 1 min"])
    assert all(v == "-" for v in DEFAULT_COINS_DATA["Price Change 5 mins"])


@patch("app.webapp_daemon.requests.get")
def test_fetch_coins_data_success(mock_get):
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {
            "coin": "btc",
            "last_price": 50000.0,
            "price_1_min_change_percent": 0.5,
            "price_5_min_change_percent": 1.2,
        }
    ]
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response

    result = fetch_coins_data()

    assert result["Name"] == ["Bitcoin"]
    assert result["Last Price (€)"] == [50000.0]
    assert result["Price Change 1 min"] == ["0.5%"]
    assert result["Price Change 5 mins"] == ["1.2%"]


@patch("app.webapp_daemon.requests.get")
def test_fetch_coins_data_none_change_percent(mock_get):
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {
            "coin": "eth",
            "last_price": 3000.0,
            "price_1_min_change_percent": None,
            "price_5_min_change_percent": None,
        }
    ]
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response

    result = fetch_coins_data()

    assert result["Price Change 1 min"] == ["-"]
    assert result["Price Change 5 mins"] == ["-"]


@patch("app.webapp_daemon.st")
@patch("app.webapp_daemon.requests.get")
def test_fetch_coins_data_request_error_returns_default(mock_get, mock_st):
    mock_get.side_effect = Exception("connection error")

    result = fetch_coins_data()

    assert result == DEFAULT_COINS_DATA
    mock_st.error.assert_called_once()


@patch("app.webapp_daemon.requests.post")
def test_send_alert_success(mock_post):
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_post.return_value = mock_response
    logger = MagicMock()

    result = send_alert(
        "user@test.com", "Bitcoin", "GREATER_THAN_OR_EQUAL", 50000.0, logger
    )

    assert result is True
    mock_post.assert_called_once()
    call_kwargs = mock_post.call_args
    assert call_kwargs.kwargs["json"]["coin"] == "btc"
    assert call_kwargs.kwargs["json"]["email"] == "user@test.com"
    assert call_kwargs.kwargs["json"]["condition"] == "GREATER_THAN_OR_EQUAL"
    assert call_kwargs.kwargs["json"]["amount"] == 50000.0


@patch("app.webapp_daemon.st")
@patch("app.webapp_daemon.requests.post")
def test_send_alert_request_error_returns_false(mock_post, mock_st):
    mock_post.side_effect = Exception("network error")
    logger = MagicMock()

    result = send_alert(
        "user@test.com", "Ethereum", "LESS_THAN_OR_EQUAL", 3000.0, logger
    )

    assert result is False
    mock_st.error.assert_called_once()


def test_send_alert_uses_correct_symbol():
    with patch("app.webapp_daemon.requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response
        logger = MagicMock()

        send_alert("a@b.com", "Dogecoin", "LESS_THAN_OR_EQUAL", 0.1, logger)

        payload = mock_post.call_args.kwargs["json"]
        assert payload["coin"] == "doge"


@patch("app.webapp_daemon.requests.get")
def test_fetch_coins_raw_success(mock_get):
    mock_response = MagicMock()
    mock_response.json.return_value = [{"coin": "btc", "last_price": 50000.0,
                                        "price_1_min_change_percent": 0.5,
                                        "price_5_min_change_percent": 1.2}]
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response

    result = fetch_coins_raw()

    assert result is not None
    assert result[0]["coin"] == "btc"


@patch("app.webapp_daemon.requests.get")
def test_fetch_coins_raw_error_returns_none(mock_get):
    mock_get.side_effect = Exception("connection error")

    result = fetch_coins_raw()

    assert result is None


def test_change_color_positive():
    html = _change_color("1.5%")
    assert "#2ecc71" in html
    assert "▲" in html


def test_change_color_negative():
    html = _change_color("-2.3%")
    assert "#e74c3c" in html
    assert "▼" in html


def test_change_color_dash():
    html = _change_color("-")
    assert "—" in html


def test_change_color_zero():
    html = _change_color("0.0%")
    assert "#2ecc71" in html
