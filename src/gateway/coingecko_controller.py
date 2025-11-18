from gateway.coingecko_base_daemon import CoinGeckoController
from gateway.coingecko_service import CoinGeckoAPIService


class CoinGeckoAPIController(CoinGeckoController):
    def __init__(
        self,
        service: CoinGeckoAPIService,
    ):
        self.service = service
        self.started = False

    def start(self):
        if not self.started:
            self.started = True

    def stop(self):
        self.service.signal_to_stop_execution()

    def execute(self):
        if not self.started:
            pass

        # CALL
