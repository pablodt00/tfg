from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from common.schemas.alert import Alert, AlertConditionEnum
from common.schemas.coin import Coin
from processor.processor_service import ProcessorService


def make_service():
    settings = MagicMock()
    settings.RESEND_API_KEY = "test-key"
    settings.FROM_EMAIL = "from@test.com"
    coin_repo = AsyncMock()
    alert_repo = AsyncMock()
    logger = MagicMock()

    mock_session = AsyncMock()
    mock_session.commit = AsyncMock()
    mock_session.rollback = AsyncMock()

    @asynccontextmanager
    async def session_factory():
        yield mock_session

    with patch("processor.processor_service.EmailService"):
        service = ProcessorService(
            settings=settings,
            coin_repository=coin_repo,
            alert_repository=alert_repo,
            session_factory=session_factory,
            logger=logger,
        )

    return service, coin_repo, alert_repo, mock_session


@pytest.mark.asyncio
async def test_process_coin_creates_new_coin():
    service, coin_repo, _, _ = make_service()
    coin_repo.get_by_coin = AsyncMock(return_value=None)
    coin_repo.add = AsyncMock()

    await service.process_coin("btc", {"btc": {"eur": 50000.0}})

    coin_repo.add.assert_called_once()


@pytest.mark.asyncio
async def test_process_coin_updates_existing_coin():
    service, coin_repo, _, _ = make_service()
    existing = Coin(coin="btc", last_price=49000.0, base_price=48000.0)
    coin_repo.get_by_coin = AsyncMock(return_value=existing)
    coin_repo.update = AsyncMock(return_value=existing)

    await service.process_coin("btc", {"btc": {"eur": 50000.0}})

    coin_repo.update.assert_called_once()


@pytest.mark.asyncio
async def test_check_alerts_triggers_gte_alert():
    service, _, alert_repo, _ = make_service()
    alert = Alert.from_alert(
        coin="btc",
        condition=AlertConditionEnum.GREATER_THAN_OR_EQUAL,
        user_email="user@test.com",
        amount=49000.0,
    )
    alert_repo.get_by_coin = AsyncMock(return_value=[alert])
    alert_repo.update = AsyncMock(return_value=alert)
    service.email_service.send_alert_email = AsyncMock(return_value=True)

    await service.check_alerts("btc", {"btc": {"eur": 50000.0}})

    service.email_service.send_alert_email.assert_called_once()
    assert alert.triggered is True


@pytest.mark.asyncio
async def test_check_alerts_does_not_trigger_when_not_met():
    service, _, alert_repo, _ = make_service()
    alert = Alert.from_alert(
        coin="btc",
        condition=AlertConditionEnum.GREATER_THAN_OR_EQUAL,
        user_email="user@test.com",
        amount=60000.0,
    )
    alert_repo.get_by_coin = AsyncMock(return_value=[alert])
    service.email_service.send_alert_email = AsyncMock()

    await service.check_alerts("btc", {"btc": {"eur": 50000.0}})

    service.email_service.send_alert_email.assert_not_called()


@pytest.mark.asyncio
async def test_check_alerts_triggers_lte_alert():
    service, _, alert_repo, _ = make_service()
    alert = Alert.from_alert(
        coin="btc",
        condition=AlertConditionEnum.LESS_THAN_OR_EQUAL,
        user_email="user@test.com",
        amount=51000.0,
    )
    alert_repo.get_by_coin = AsyncMock(return_value=[alert])
    alert_repo.update = AsyncMock(return_value=alert)
    service.email_service.send_alert_email = AsyncMock(return_value=True)

    await service.check_alerts("btc", {"btc": {"eur": 50000.0}})

    service.email_service.send_alert_email.assert_called_once()


@pytest.mark.asyncio
async def test_process_data_calls_process_and_check():
    service, coin_repo, alert_repo, _ = make_service()
    coin_repo.get_by_coin = AsyncMock(return_value=None)
    coin_repo.add = AsyncMock()
    alert_repo.get_by_coin = AsyncMock(return_value=[])

    data = {"btc": {"eur": 50000.0}}
    await service.process_data(data)

    coin_repo.add.assert_called_once()
