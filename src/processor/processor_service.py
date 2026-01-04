# pylint: disable=too-many-arguments, too-many-positional-arguments
import asyncio
import json
import threading
from datetime import datetime, timedelta

import structlog
from structlog.typing import FilteringBoundLogger

from common.config.settings import Settings
from common.consumers.kafka_consumer import KafkaConsumer
from common.database import SessionFactory
from common.database.repositories.alert_repository import AlertRepository
from common.database.repositories.coin_repository import CoinRepository
from common.schemas.coin import Coin

default_logger = structlog.get_logger()


class ProcessorService:
    def __init__(
        self,
        settings: Settings,
        kafka_consumer: KafkaConsumer,
        coin_repository: CoinRepository,
        alert_repository: AlertRepository,
        session_factory: SessionFactory,
        logger: FilteringBoundLogger = default_logger,
    ):
        self.settings = settings
        self.kafka_consumer = kafka_consumer
        self.coin_repository = coin_repository
        self.alert_repository = alert_repository
        self.session_factory = session_factory
        self.logger = logger
        self._loop = None
        self._loop_thread = None

    def _start_event_loop(self):
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()

    async def _handle_message_async(self, message: str):
        self.logger.info("Received Kafka message", message=message)

        try:
            data = json.loads(message)
            self.logger.info("Processing message", data=data)
            await self.process_data(data)
        except json.JSONDecodeError:
            self.logger.error("Failed to decode message", message=message)
        except Exception as e:  # pylint: disable=broad-exception-caught
            self.logger.error("Error processing message", error=str(e), exc_info=True)

    def _handle_message(self, message: str):
        asyncio.run_coroutine_threadsafe(
            self._handle_message_async(message), self._loop
        )

    def run(self):
        self.logger.info("ProcessorService: Running")

        self._loop = asyncio.new_event_loop()
        self._loop_thread = threading.Thread(target=self._start_event_loop, daemon=True)
        self._loop_thread.start()

        try:
            self.kafka_consumer.consume_messages(self._handle_message)
        finally:
            self._loop.call_soon_threadsafe(self._loop.stop)
            self._loop_thread.join(timeout=5)
            self._loop.close()

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

    async def process_data(self, data: dict):
        for coin in data:
            await self.process_coin(coin, data)

        self.logger.info("ProcessorService: Processed last received data")
