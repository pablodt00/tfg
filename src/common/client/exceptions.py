class CoinGeckoAPIError(Exception):
    """General exception received from CoinGecko API"""
    pass

class CoinGeckoMissingAPIKeyError(ValueError):
    """Exception when an API Key is not defined for the client"""
    pass

class CoinGeckoMissingBaseURLError(ValueError):
    """Exception when the base URL is not defined for the client"""
    pass