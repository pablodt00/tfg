import time
from abc import ABC, abstractmethod
from typing import Callable

import structlog
from structlog.typing import FilteringBoundLogger

from common.daemons.base_daemon import BaseDaemon

SLEEP_TIME_BETWEEN_RUNS_SECONDS = 60

default_logger = structlog.get_logger()


class CoinGeckoController(ABC):
    @abstractmethod
    def start(self):
        raise NotImplementedError

    @abstractmethod
    def stop(self):
        raise NotImplementedError

    @abstractmethod
    def execute(self):
        raise NotImplementedError


class CoinGeckoBaseDaemon(BaseDaemon):
    def __init__(
        self,
        controller: CoinGeckoController,
        heartbeat_handler: Callable[[], None],
        logger: FilteringBoundLogger = default_logger,
    ):
        super().__init__()
        self.controller = controller
        self.heartbeat_handler = heartbeat_handler
        self.logger = logger.bind(controller_class=self.controller.__class__.__name__)

    def start(self):
        self.logger.info("CoinGeckoBaseDaemon: Starting daemon")
        self.controller.start()
        super().start()

    def stop(self, signum, _):
        self.logger.info(
            "CoinGeckoBaseDaemon: Stopping daemon",
            signal_number=signum,
        )
        if self.controller:
            self.logger.info(
                "CoinGeckoBaseDaemon: Signalling controller to stop",
            )
            self.controller.stop()

        super().stop(signum, _)

    def heartbeat(self) -> None:
        self.logger.info(
            "CoinGeckoBaseDaemon: Heartbeat signal sent",
        )
        self.heartbeat_handler()

    def execute(self):
        self.logger.info("CoinGeckoBaseDaemon: Executing task")
        try:
            self.controller.execute()
        except BaseException as _:  # pylint: disable=broad-exception-caught
            self.logger.exception(
                "CoinGeckoBaseDaemon: Error during controller execution",
            )

        self.heartbeat()
        self.logger.info(
            "CoinGeckoBaseDaemon: Sleeping before next execution",
        )
        time.sleep(SLEEP_TIME_BETWEEN_RUNS_SECONDS)
