from common.client.endpoints.base_endpoint import BaseEndpoint, HTTPMethod


class PingEndpoint(BaseEndpoint):
    def __init__(self):
        super().__init__(
            path="/ping",
            method=HTTPMethod.GET,
        )
