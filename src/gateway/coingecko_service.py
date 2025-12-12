from common.config.settings import Settings


class CoinGeckoAPIService:
    def __init__(
        self,
        settings: Settings,
    ):
        self.settings = settings
        self.must_stop = False

    def signal_to_stop_execution(self):
        self.must_stop = True

    def process_data(self):
        try:
            pass
        except Exception:  # pylint: disable=broad-except
            pass

    def execute(self):
        if self.must_stop:
            pass
