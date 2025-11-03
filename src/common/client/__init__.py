from common.client.coingecko_client import CoinGeckoClient
from common.config.settings import Settings
import requests

if __name__ == '__main__':
    client = CoinGeckoClient(
        Settings(),
        requests.Session()
    )
    print(client.ping())

