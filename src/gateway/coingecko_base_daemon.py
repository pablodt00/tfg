import time
from abc import ABC, abstractmethod
from typing import Callable

from common.daemons.base_daemon import BaseDaemon

SLEEP_TIME_BETWEEN_RUNS_SECONDS = 60


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
    ):
        super().__init__()
        self.controller = controller
        self.heartbeat_handler = heartbeat_handler

    def start(self):
        self.controller.start()
        super().start()

    def stop(self, signum, _):
        if self.controller:
            self.controller.stop()

        super().stop(signum, _)

    def heartbeat(self) -> None:
        self.heartbeat_handler()

    def execute(self):
        try:
            self.controller.execute()
        except BaseException as _:  # pylint: disable=broad-exception-caught
            pass

        self.heartbeat()
        time.sleep(SLEEP_TIME_BETWEEN_RUNS_SECONDS)
