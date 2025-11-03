class CoinGeckoAPIError(Exception):
    """General exception received from CoinGecko API"""

class CoinGeckoMissingAPIKeyError(ValueError):
    """Exception when an API Key is not defined for the client"""

class CoinGeckoMissingBaseURLError(ValueError):
    """Exception when the base URL is not defined for the client"""
