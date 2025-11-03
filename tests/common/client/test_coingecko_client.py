from unittest import TestCase

from common.client.coingecko_client import CoinGeckoClient
from common.config.settings import Settings


class TestCoinGeckoClient(TestCase):
    def test_ping_endpoint(self):
        client = CoinGeckoClient(
            Settings(),
        )

        assert client.ping() == {'gecko_says': '(V3) To the Moon!'}
