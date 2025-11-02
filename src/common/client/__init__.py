from common.client.coingecko_client import CoinGeckoClient

if __name__ == '__main__':
    client = CoinGeckoClient(None)
    print(client.ping())

