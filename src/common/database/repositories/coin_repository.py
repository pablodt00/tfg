from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from common.database.models import CoinModel
from common.database.repositories.crud_repository import CrudRepository
from common.schemas.coin import Coin


class CoinRepository(CrudRepository):
    def __init__(self) -> None:
        super().__init__(CoinModel, Coin)

    async def get_by_coin(self, coin: str, session: AsyncSession) -> Coin | None:
        stmt = select(self.sql_alchemy_model).where(self.sql_alchemy_model.coin == coin)
        result = await session.execute(stmt)
        db_data = result.scalars().first()
        if db_data is None:
            return None

        validated_result: Coin = self.schema.model_validate(db_data)
        return validated_result
