import structlog
from pydantic import BaseModel
from structlog.typing import FilteringBoundLogger

from common.client.coingecko_client import CoinGeckoClient
from common.client.endpoints.coin_price_by_id import CoinPriceByIdEndpoint
from common.config.settings import Settings
from common.observability.metrics import coingecko_api_requests
from common.producers.kafka_producer import KafkaProducer

default_logger = structlog.get_logger()


class CoinGeckoAPIService:
    def __init__(
        self,
        settings: Settings,
        kafka_producer: KafkaProducer,
        logger: FilteringBoundLogger = default_logger,
    ):
        self.settings = settings
        self.logger = logger
        self.must_stop = False
        self.producer = kafka_producer

    def signal_to_stop_execution(self):
        self.must_stop = True

    def publish_to_kafka(self, message: BaseModel):
        self.producer.produce_message(message)

    async def execute(self):
        if self.must_stop:
            self.logger.debug(
                "CoinGeckoAPIService: Clean stop",
            )
            return

        self.logger.info(
            "CoinGeckoAPIService: Calling CoinGecko API",
        )
        try:
            async with CoinGeckoClient(settings=self.settings) as client:
                coin_price_data = await client.get_coins_price_py_id(
                    coin_price_data=CoinPriceByIdEndpoint.get_default_request(),
                )
                self.logger.info(
                    "CoinGeckoAPIService: "
                    "Successfully retrieved data from CoinGecko API",
                    data=coin_price_data,
                )

                coingecko_api_requests.inc()

                self.publish_to_kafka(message=coin_price_data)
                self.logger.info(
                    "CoinGeckoAPIService: Published data to Kafka topic",
                )
        except Exception:
            self.logger.exception(
                "CoinGeckoAPIService: Error calling CoinGecko API",
            )

            raise
