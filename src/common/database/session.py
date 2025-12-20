from collections.abc import Callable
from typing import TypeAlias

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    create_async_engine,
)
from sqlalchemy.orm import sessionmaker

SessionFactory: TypeAlias = Callable[[], AsyncSession]


def make_engine(
    db_uri: str,
) -> AsyncEngine:
    return create_async_engine(db_uri, pool_recycle=3600)


def make_session_factory(engine: AsyncEngine) -> SessionFactory:
    return sessionmaker(
        bind=engine,  # type: ignore
        autoflush=False,
        autocommit=False,
        autobegin=True,
        class_=AsyncSession,
    )
