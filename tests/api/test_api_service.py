from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, MagicMock

import pytest

from api.api_service import APIService
from common.schemas.alert import Alert, AlertConditionEnum
from common.schemas.coin import Coin


def make_service():
    settings = MagicMock()
    coin_repo = AsyncMock()
    alert_repo = AsyncMock()

    mock_session = AsyncMock()

    @asynccontextmanager
    async def session_factory():
        yield mock_session

    service = APIService(
        settings=settings,
        coin_repository=coin_repo,
        alert_repository=alert_repo,
        session_factory=session_factory,
    )
    return service, coin_repo, alert_repo, mock_session


@pytest.mark.asyncio
async def test_get_coins_returns_list():
    service, coin_repo, _, _ = make_service()
    coin_repo.get_all = AsyncMock(return_value=[])

    result = await service.get_coins()
    assert result == []


@pytest.mark.asyncio
async def test_get_coins_returns_coins():
    service, coin_repo, _, _ = make_service()
    coin = Coin(coin="btc", last_price=50000.0, base_price=49000.0)
    coin_repo.get_all = AsyncMock(return_value=[coin])

    result = await service.get_coins()
    assert len(result) == 1
    assert result[0].coin == "btc"


@pytest.mark.asyncio
async def test_add_alert_calls_repository():
    service, _, alert_repo, _ = make_service()
    expected = Alert.from_alert(
        coin="btc",
        condition=AlertConditionEnum.GREATER_THAN_OR_EQUAL,
        user_email="x@y.com",
        amount=100.0,
    )
    alert_repo.add = AsyncMock(return_value=expected)

    result = await service.add_alert(
        email="x@y.com",
        coin="btc",
        amount=100.0,
        condition=AlertConditionEnum.GREATER_THAN_OR_EQUAL,
    )
    assert result.coin == "btc"
    assert result.user_email == "x@y.com"


@pytest.mark.asyncio
async def test_get_coins_propagates_exception():
    service, coin_repo, _, _ = make_service()
    coin_repo.get_all = AsyncMock(side_effect=RuntimeError("db error"))

    with pytest.raises(RuntimeError, match="db error"):
        await service.get_coins()
