from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from common.database.repositories.alert_repository import AlertRepository


@pytest.mark.asyncio
async def test_get_by_coin_returns_empty_list():
    repo = AlertRepository()
    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_session.execute = AsyncMock(return_value=mock_result)

    result = await repo.get_by_coin(coin="btc", session=mock_session)
    assert result == []


@pytest.mark.asyncio
async def test_get_by_coin_returns_alerts():
    repo = AlertRepository()
    mock_session = AsyncMock()

    mock_db_row = MagicMock()
    mock_db_row.id = 1
    mock_db_row.coin = "btc"
    mock_db_row.condition = "GREATER_THAN_OR_EQUAL"
    mock_db_row.amount = 50000.0
    mock_db_row.triggered = False
    mock_db_row.user_email = "user@test.com"
    mock_db_row.created_at = datetime.now()

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [mock_db_row]
    mock_session.execute = AsyncMock(return_value=mock_result)

    result = await repo.get_by_coin(coin="btc", session=mock_session)
    assert len(result) == 1
    assert result[0].coin == "btc"
