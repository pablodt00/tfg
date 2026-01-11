# pylint: disable=too-many-arguments, too-many-positional-arguments
from datetime import datetime, timedelta

import structlog
from structlog.typing import FilteringBoundLogger

from common.config.settings import Settings
from common.database import SessionFactory
from common.database.repositories.alert_repository import AlertRepository
from common.database.repositories.coin_repository import CoinRepository
from common.schemas.alert import AlertConditionEnum
from common.schemas.coin import Coin
from processor.email_service import EmailService

default_logger = structlog.get_logger()


class ProcessorService:
    def __init__(
        self,
        settings: Settings,
        coin_repository: CoinRepository,
        alert_repository: AlertRepository,
        session_factory: SessionFactory,
        logger: FilteringBoundLogger = default_logger,
    ):
        self.settings = settings
        self.coin_repository = coin_repository
        self.alert_repository = alert_repository
        self.session_factory = session_factory
        self.logger = logger
        self.email_service = EmailService(
            api_key=self.settings.SENDGRID_API_KEY,
            from_email=self.settings.FROM_EMAIL,
        )

    async def process_coin(self, coin: str, data: dict):
        coin_price = data[coin]["eur"]
        async with self.session_factory() as session:
            try:
                db_coin = await self.coin_repository.get_by_coin(
                    session=session, coin=coin
                )
                if db_coin is None:
                    self.logger.info(
                        "ProcessorService: Coin not in DB, adding...", coin=coin
                    )
                    new_coin = Coin.from_coin(
                        coin=coin,
                        last_price=coin_price,
                        base_price=coin_price,
                    )
                    await self.coin_repository.add(
                        session=session,
                        model=new_coin,
                    )
                    self.logger.info("ProcessorService: Added new coin", coin=coin)
                else:
                    self.logger.info(
                        "ProcessorService: Coin in DB. Updating...", coin=coin
                    )
                    last_price = db_coin.last_price
                    price_1_min_change_percent = round(
                        ((coin_price - last_price) / coin_price) * 100, 2
                    )
                    db_coin.price_1_min_change_percent = price_1_min_change_percent
                    db_coin.last_price = coin_price
                    if datetime.now() >= db_coin.base_timestamp + timedelta(minutes=5):
                        self.logger.info(
                            "ProcessorService: 5 minutes passed, updating base price",
                            coin=coin,
                        )
                        base_price = db_coin.base_price
                        price_5_min_change_percent = round(
                            ((coin_price - base_price) / coin_price) * 100, 2
                        )
                        db_coin.price_5_min_change_percent = price_5_min_change_percent
                        db_coin.base_price = coin_price
                        db_coin.base_timestamp = datetime.now()
                    await self.coin_repository.update(
                        session=session, model=db_coin, entity_id=db_coin.id
                    )
                    self.logger.info("ProcessorService: Updated coin", coin=coin)

                await session.commit()
            except Exception:
                await session.rollback()
                raise

    async def check_alerts(self, coin: str, data: dict):
        coin_price = data[coin]["eur"]
        async with self.session_factory() as session:
            try:
                self.logger.info("Getting alerts for coin", coin=coin)
                alerts = await self.alert_repository.get_by_coin(
                    coin=coin,
                    session=session,
                )

                for alert in alerts:
                    if alert.condition == AlertConditionEnum.GREATER_THAN_OR_EQUAL:
                        if coin_price >= alert.amount:
                            self.logger.info("Alert triggered for coin", coin=coin)
                            await self.send_alert(
                                coin=coin,
                                coin_price=coin_price,
                                condition=alert.condition.value,
                                threshold=alert.amount,
                                email=alert.user_email,
                            )
                            alert.triggered = True
                            await self.alert_repository.update(
                                session=session, model=alert, entity_id=alert.id
                            )
                    else:
                        if coin_price <= alert.amount:
                            self.logger.info("Alert triggered for coin", coin=coin)
                            await self.send_alert(
                                coin=coin,
                                coin_price=coin_price,
                                condition=alert.condition.value,
                                threshold=alert.amount,
                                email=alert.user_email,
                            )
                            alert.triggered = True
                            await self.alert_repository.update(
                                session=session, model=alert, entity_id=alert.id
                            )

                await session.commit()
            except Exception:
                await session.rollback()
                raise

    async def send_alert(
        self, coin: str, coin_price: float, condition: str, threshold: float, email: str
    ):
        await self.email_service.send_alert_email(
            to_email=email,
            coin=coin,
            price=coin_price,
            condition=condition,
            threshold=threshold,
        )

    async def process_data(self, data: dict):
        for coin in data:
            await self.process_coin(coin, data)
            await self.check_alerts(coin, data)

        self.logger.info("ProcessorService: Processed last received data")
