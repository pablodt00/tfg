# pylint: disable=duplicate-code
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import ASGITransport, AsyncClient

from gateway.coingecko_service import CoinGeckoAPIService
from gateway.endpoints.app import build_coingecko_api_daemon


def make_app():
    service = MagicMock(spec=CoinGeckoAPIService)
    app = build_coingecko_api_daemon(coingecko_api_service=service)
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
async def test_fetch_coins_success():
    app, service = make_app()
    service.execute = AsyncMock(return_value=None)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post("/coingecko/fetch")
    assert response.status_code == 200
    assert response.json()["status"] == "success"


@pytest.mark.asyncio
async def test_fetch_coins_server_error():
    app, service = make_app()
    service.execute = AsyncMock(side_effect=Exception("coingecko down"))

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post("/coingecko/fetch")
    assert response.status_code == 500
