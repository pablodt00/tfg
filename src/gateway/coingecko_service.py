import structlog
from structlog.typing import FilteringBoundLogger

from common.client.coingecko_client import CoinGeckoClient
from common.client.endpoints.coin_price_by_id import CoinPriceByIdEndpoint
from common.config.settings import Settings

default_logger = structlog.get_logger()


class CoinGeckoAPIService:
    def __init__(
        self,
        settings: Settings,
        logger: FilteringBoundLogger = default_logger,
    ):
        self.settings = settings
        self.logger = logger
        self.must_stop = False

    def signal_to_stop_execution(self):
        self.must_stop = True

    def publish_to_kafka(self):
        pass

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
        except Exception:
            self.logger.exception(
                "CoinGeckoAPIService: Error calling CoinGecko API",
            )

            raise
