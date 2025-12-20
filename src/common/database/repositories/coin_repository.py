from common.database.models import CoinModel
from common.database.repositories.crud_repository import CrudRepository
from common.schemas.coin import Coin


class CoinRepository(CrudRepository):
    def __init__(self) -> None:
        super().__init__(CoinModel, Coin)
