from common.database.models import AlertModel
from common.database.repositories.crud_repository import CrudRepository
from common.schemas.alert import Alert


class AlertRepository(CrudRepository):
    def __init__(self) -> None:
        super().__init__(AlertModel, Alert)
