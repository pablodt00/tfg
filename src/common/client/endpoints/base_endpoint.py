

class BaseCoinGeckoEndpoint:
    def __init__(
            self,
            endpoint_url: str,
            method: str,
    ):
        self.endpoint_url = endpoint_url
        self.method = method
