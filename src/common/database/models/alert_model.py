from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String

from common.database.models.base import ORMBaseModel


class AlertModel(ORMBaseModel):
    __tablename__ = "alert"

    id = Column(Integer, primary_key=True, autoincrement=True)
    coin = Column(String, nullable=False)
    condition = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    triggered = Column(Boolean, nullable=False, default=False)
    user_email = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
