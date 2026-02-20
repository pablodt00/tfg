from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from processor.email_service import EmailService


def make_service():
    with patch("processor.email_service.SendgridAPI"):
        service = EmailService(api_key="test-key", from_email="from@test.com")
    return service


@pytest.mark.asyncio
async def test_send_alert_email_success():
    service = make_service()
    mock_response = MagicMock()
    mock_response.status_code = 202
    service.client.send = AsyncMock(return_value=mock_response)

    result = await service.send_alert_email(
        to_email="to@test.com",
        coin="btc",
        price=50000.0,
        condition="GREATER_THAN_OR_EQUAL",
        threshold=49000.0,
    )
    assert result is True


@pytest.mark.asyncio
async def test_send_alert_email_failure_status():
    service = make_service()
    mock_response = MagicMock()
    mock_response.status_code = 500
    service.client.send = AsyncMock(return_value=mock_response)

    result = await service.send_alert_email(
        to_email="to@test.com",
        coin="btc",
        price=50000.0,
        condition="GREATER_THAN_OR_EQUAL",
        threshold=49000.0,
    )
    assert result is False


@pytest.mark.asyncio
async def test_send_alert_email_exception():
    service = make_service()
    service.client.send = AsyncMock(side_effect=Exception("network error"))

    result = await service.send_alert_email(
        to_email="to@test.com",
        coin="btc",
        price=50000.0,
        condition="GREATER_THAN_OR_EQUAL",
        threshold=49000.0,
    )
    assert result is False
