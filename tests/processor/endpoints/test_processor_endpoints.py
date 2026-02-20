# pylint: disable=duplicate-code
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import ASGITransport, AsyncClient

from processor.endpoints.app import build_processor_daemon
from processor.processor_service import ProcessorService


def make_app():
    service = MagicMock(spec=ProcessorService)
    app = build_processor_daemon(processor_service=service)
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
async def test_process_event_success():
    app, service = make_app()
    service.process_data = AsyncMock(return_value=None)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post("/event/", json={"btc": {"eur": 50000.0}})
    assert response.status_code == 200
    assert response.json()["status"] == "success"


@pytest.mark.asyncio
async def test_process_event_server_error():
    app, service = make_app()
    service.process_data = AsyncMock(side_effect=Exception("processing error"))

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post("/event/", json={"btc": {"eur": 50000.0}})
    assert response.status_code == 500
