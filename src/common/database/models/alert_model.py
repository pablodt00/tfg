from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime

from common.database.models.base import ORMBaseModel


class AlertModel(ORMBaseModel):
    __tablename__ = "alert"

    id = Column(Integer, primary_key=True, autoincrement=True)
    coin = Column(String, nullable=False)
    condition = Column(String, nullable=False)
    user_email = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
