from prometheus_client import Counter

coingecko_api_requests = Counter(
    "coingecko_api_requests",
    "Total number of requests made to the CoinGecko API",
)
