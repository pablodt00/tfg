from unittest.mock import AsyncMock, MagicMock

import pytest

from common.database.models.coin_model import CoinModel
from common.database.repositories.crud_repository import CrudRepository, RecordNotFound
from common.schemas.coin import Coin


def make_repo():
    return CrudRepository(sql_alchemy_model=CoinModel, schema=Coin)


@pytest.mark.asyncio
async def test_get_all_returns_list():
    repo = make_repo()
    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_session.execute = AsyncMock(return_value=mock_result)

    result = await repo.get_all(session=mock_session)
    assert result == []


@pytest.mark.asyncio
async def test_get_by_id_raises_not_found():
    repo = make_repo()
    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = None
    mock_session.execute = AsyncMock(return_value=mock_result)

    with pytest.raises(RecordNotFound):
        await repo.get_by_id(entity_id=999, session=mock_session)


@pytest.mark.asyncio
async def test_delete_raises_not_found():
    repo = make_repo()
    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = None
    mock_session.execute = AsyncMock(return_value=mock_result)

    with pytest.raises(RecordNotFound):
        await repo.delete(entity_id=999, session=mock_session)


@pytest.mark.asyncio
async def test_update_raises_not_found():
    repo = make_repo()
    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = None
    mock_session.execute = AsyncMock(return_value=mock_result)

    coin = Coin(coin="btc", last_price=1.0, base_price=1.0)
    with pytest.raises(RecordNotFound):
        await repo.update(entity_id=999, model=coin, session=mock_session)
