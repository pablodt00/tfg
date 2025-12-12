import asyncio

import structlog
from structlog.typing import FilteringBoundLogger

from gateway.coingecko_base_daemon import CoinGeckoController
from gateway.coingecko_service import CoinGeckoAPIService

default_logger = structlog.get_logger()


class CoinGeckoAPIController(CoinGeckoController):
    def __init__(
        self,
        # add session_factory here
        service: CoinGeckoAPIService,
        logger: FilteringBoundLogger = default_logger,
    ):
        self.service = service
        self.started = False
        self.logger = logger

    def start(self):
        if not self.started:
            self.started = True

    def stop(self):
        self.service.signal_to_stop_execution()

    def execute(self):
        if not self.started:
            self.logger.error(
                "CoinGeckoAPIController: Controller not initialized",
            )

        try:
            asyncio.run(self.service.execute())
        except RuntimeError as e:
            self.logger.error(
                "CoinGeckoAPIController: Error during service execution",
                error=str(e),
            )
