from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String, UniqueConstraint

from common.database.models import ORMBaseModel


class CoinModel(ORMBaseModel):
    __tablename__ = "coin"

    id = Column(Integer, primary_key=True, autoincrement=True)
    coin = Column(String, nullable=False)
    last_price = Column(Float, nullable=False)
    base_price = Column(Float, nullable=False)
    price_1_min_change_percent = Column(Float)
    price_5_min_change_percent = Column(Float)
    base_timestamp = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.now, nullable=False, onupdate=datetime.now
    )

    __table_args__ = (UniqueConstraint("coin"),)
