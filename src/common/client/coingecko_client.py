import requests
import logging
from typing import Any, Dict, Optional

from common.client.endpoints.base_endpoint import BaseCoinGeckoEndpoint
from common.client.endpoints.ping import PingEndpoint
from common.client.exceptions import CoinGeckoMissingAPIKeyError, CoinGeckoMissingBaseURLError, CoinGeckoAPIError
from common.config.settings import Settings

logger = logging.getLogger("CoinGeckoClient")

class CoinGeckoClient:
    def __init__(
            self,
            settings: Settings,
            session: Optional[requests.Session] = None
    ):
        if not settings.COINGECKO_API_KEY:
            raise CoinGeckoMissingAPIKeyError("A valid API key is needed for CoinGecko")

        if not settings.COINGECKO_BASE_URL:
            raise CoinGeckoMissingBaseURLError("A valid base URL is needed for making requests to CoinGecko")

        self.api_key = settings.COINGECKO_API_KEY
        self.timeout = settings.COINGECKO_TIMEOUT or 10
        self.base_url = settings.COINGECKO_BASE_URL
        self.session = session
        self.ping_endpoint = PingEndpoint()

    def _headers(self) -> Dict[str, str]:
        return {
            "Accept": "application/json",
            "x-cg-demo-api-key": self.api_key
        }

    def _request(self, endpoint: BaseCoinGeckoEndpoint) -> Dict[str, Any]:
        url = f"{self.base_url}{endpoint.endpoint_url}"
        headers = self._headers()
        method = endpoint.method
        logger.info(f"Sending request {method} {url}")

        try:
            response = self.session.request(
                method=method,
                url = url,
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            raise CoinGeckoAPIError("CoinGecko timeout exceeded")
        except requests.exceptions.HTTPError:
            raise CoinGeckoAPIError(f"HTTP error {response.status_code}: {response.text}")
        except requests.exceptions.RequestException as e:
            raise CoinGeckoAPIError(f"Network error: {e}")
        except ValueError:
            raise CoinGeckoAPIError("Invalid response")

    def ping(self):
        return self._request(self.ping_endpoint)
