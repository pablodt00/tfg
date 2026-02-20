from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import ASGITransport, AsyncClient

from api.api_service import APIService
from api.endpoints.app import build_api
from common.schemas.alert import Alert, AlertConditionEnum
from common.schemas.coin import Coin


def make_app():
    service = MagicMock(spec=APIService)
    app = build_api(api_service=service)
    return app, service


@pytest.mark.asyncio
async def test_health_ping():
    app, _ = make_app()
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/health/ping")
    assert response.status_code == 200
    assert response.json() == {"ping": "pong"}


@pytest.mark.asyncio
async def test_get_coins_success():
    app, service = make_app()
    coin = Coin(coin="btc", last_price=50000.0, base_price=49000.0)
    service.get_coins = AsyncMock(return_value=[coin])

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/coins/coins")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_coins_server_error():
    app, service = make_app()
    service.get_coins = AsyncMock(side_effect=Exception("fail"))

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/coins/coins")
    assert response.status_code == 500


@pytest.mark.asyncio
async def test_add_alert_success():
    app, service = make_app()
    alert = Alert.from_alert(
        coin="btc",
        condition=AlertConditionEnum.GREATER_THAN_OR_EQUAL,
        user_email="a@b.com",
        amount=1000.0,
    )
    service.add_alert = AsyncMock(return_value=alert)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/alerts/add",
            json={
                "coin": "btc",
                "amount": 1000.0,
                "email": "a@b.com",
                "condition": "GREATER_THAN_OR_EQUAL",
            },
        )
    assert response.status_code == 201
