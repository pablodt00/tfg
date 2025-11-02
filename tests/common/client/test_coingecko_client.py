from unittest import TestCase

from src.common.client.coingecko_client import CoinGeckoClient


class TestCoinGeckoClient(TestCase):
    def test_ping_endpoint(self):
        client = CoinGeckoClient(
            None,
        )

        client._request(client.ping_endpoint)
