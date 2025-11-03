from common.client.endpoints.base_endpoint import BaseCoinGeckoEndpoint


class PingEndpoint(BaseCoinGeckoEndpoint):
    def __init__(self):
        super().__init__(endpoint_url="/ping", method="GET")
