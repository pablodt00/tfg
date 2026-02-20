from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from common.database.repositories.coin_repository import CoinRepository


@pytest.mark.asyncio
async def test_get_by_coin_returns_none_when_not_found():
    repo = CoinRepository()
    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = None
    mock_session.execute = AsyncMock(return_value=mock_result)

    result = await repo.get_by_coin(coin="btc", session=mock_session)
    assert result is None


@pytest.mark.asyncio
async def test_get_by_coin_returns_coin_when_found():
    repo = CoinRepository()
    mock_session = AsyncMock()

    mock_db_row = MagicMock()
    mock_db_row.id = 1
    mock_db_row.coin = "btc"
    mock_db_row.last_price = 50000.0
    mock_db_row.base_price = 49000.0
    mock_db_row.price_1_min_change_percent = None
    mock_db_row.price_5_min_change_percent = None
    mock_db_row.base_timestamp = datetime.now()
    mock_db_row.updated_at = datetime.now()

    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = mock_db_row
    mock_session.execute = AsyncMock(return_value=mock_result)

    result = await repo.get_by_coin(coin="btc", session=mock_session)
    assert result is not None
    assert result.coin == "btc"
