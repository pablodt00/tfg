from unittest.mock import patch

import pytest

from processor.email_service import EmailService


def make_service():
    service = EmailService(api_key="test-key", from_email="from@test.com")
    return service


@pytest.mark.asyncio
async def test_send_alert_email_success():
    service = make_service()
    mock_response = {"id": "mock-id-123"}

    with patch("processor.email_service.asyncio.to_thread", return_value=mock_response):
        result = await service.send_alert_email(
            to_email="to@test.com",
            coin="btc",
            price=50000.0,
            condition="GREATER_THAN_OR_EQUAL",
            threshold=49000.0,
        )
    assert result is True


@pytest.mark.asyncio
async def test_send_alert_email_exception():
    service = make_service()

    with patch(
        "processor.email_service.asyncio.to_thread",
            side_effect=Exception("network error")
    ):
        result = await service.send_alert_email(
            to_email="to@test.com",
            coin="btc",
            price=50000.0,
            condition="GREATER_THAN_OR_EQUAL",
            threshold=49000.0,
        )
    assert result is False
