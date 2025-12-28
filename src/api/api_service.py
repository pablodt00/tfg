from common.config.settings import Settings
from common.database import SessionFactory
from common.database.repositories.alert_repository import AlertRepository
from common.database.repositories.coin_repository import CoinRepository
from common.schemas.alert import Alert, AlertConditionEnum


class APIService:
    def __init__(
        self,
        settings: Settings,
        coin_repository: CoinRepository,
        alert_repository: AlertRepository,
        session_factory: SessionFactory,
    ):
        self.settings = settings

        self.coin_repository = coin_repository
        self.alert_repository = alert_repository
        self.session_factory = session_factory

    async def get_coins(self):
        try:
            async with self.session_factory() as session:
                coins = await self.coin_repository.get_all(session=session)
                return coins
        except Exception:  # pylint: disable=try-except-raise
            raise

    async def add_alert(
        self, email: str, coin: str, amount: float, condition: AlertConditionEnum
    ):
        try:
            async with self.session_factory() as session:
                new_alert = Alert.from_alert(
                    user_email=email,
                    coin=coin,
                    amount=amount,
                    condition=condition,
                )
                alert = await self.alert_repository.add(
                    session=session,
                    model=new_alert,
                )
                return alert
        except Exception:  # pylint: disable=try-except-raise
            raise
