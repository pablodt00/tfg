from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from common.database.models import AlertModel
from common.database.repositories.crud_repository import CrudRepository
from common.schemas.alert import Alert


class AlertRepository(CrudRepository):
    def __init__(self) -> None:
        super().__init__(AlertModel, Alert)

    async def get_by_coin(self, coin: str, session: AsyncSession) -> list[Alert] | None:
        result = await session.execute(
            select(self.sql_alchemy_model).where(
                self.sql_alchemy_model.coin == coin,
                self.sql_alchemy_model.triggered.is_(False),
            )
        )
        data = result.scalars().all()
        return list(map(self.schema.model_validate, data))
