from typing import Generic, Type, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from common.database.models import ORMBaseModel
from common.schemas.base import ORMBaseSchema


class RecordNotFound(Exception):
    pass


T = TypeVar("T", bound=ORMBaseSchema)


class CrudRepository(Generic[T]):
    def __init__(self, sql_alchemy_model: Type[ORMBaseModel], schema: Type[T]) -> None:
        self.sql_alchemy_model = sql_alchemy_model
        self.schema = schema

    async def get_all(self, session: AsyncSession) -> list[T]:
        result = await session.execute(select(self.sql_alchemy_model))
        data = result.scalars().all()
        return list(map(self.schema.model_validate, data))

    async def get_by_id(self, entity_id: int, session: AsyncSession) -> T:
        stmt = select(self.sql_alchemy_model).where(
            self.sql_alchemy_model.id == entity_id
        )
        result = await session.execute(stmt)
        db_data = result.scalars().first()
        if db_data is None:
            raise RecordNotFound(f"Entity not found for id {entity_id}")

        validated_result: T = self.schema.model_validate(db_data)
        return validated_result

    async def add(self, model: T, session: AsyncSession) -> T:
        db_data = self.sql_alchemy_model(**model.model_dump())  # type: ignore
        session.add(db_data)
        await session.flush()

        await session.refresh(db_data)

        return self._orm_to_pydantic(db_data)

    async def delete(self, entity_id: int, session: AsyncSession) -> None:
        stmt = select(self.sql_alchemy_model).where(
            self.sql_alchemy_model.id == entity_id
        )
        result = await session.execute(stmt)
        db_data = result.scalars().first()
        if db_data is None:
            raise RecordNotFound(f"Entity not found for id {entity_id}")
        await session.delete(db_data)
        await session.flush()

    async def update(self, entity_id: int, model: T, session: AsyncSession) -> T:
        stmt = select(self.sql_alchemy_model).where(
            self.sql_alchemy_model.id == entity_id
        )
        result = await session.execute(stmt)
        stored_data = result.scalars().first()
        if not stored_data:
            raise RecordNotFound(f"Entity not found for id {entity_id}")

        for key, value in model.model_dump(exclude={"id", "updated_at"}).items():
            setattr(stored_data, key, value)

        await session.flush()
        await session.refresh(stored_data)

        result_obj: T = self.schema.model_validate(stored_data)

        return result_obj

    def _orm_to_pydantic(
        self, orm_record: ORMBaseModel, schema: Type[T] | None = None
    ) -> T:
        schema = schema or self.schema
        record: T = schema.model_validate(orm_record)
        return record
