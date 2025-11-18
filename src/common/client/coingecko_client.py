import logging
from typing import Dict, Optional

import httpx
import requests
from pydantic import ValidationError

from common.client.endpoints.base_endpoint import (
    BaseEndpoint,
    QueryParamsModel,
    RequestModel,
    ResponseModel,
)
from common.client.endpoints.coin_price_by_id import (
    CoinPriceByIdEndpoint,
    CoinPriceByIdParams,
)
from common.client.endpoints.ping import PingEndpoint
from common.client.exceptions import (
    CoinGeckoAPIError,
    CoinGeckoMissingAPIKeyError,
    CoinGeckoMissingBaseURLError,
)
from common.config.settings import Settings

logger = logging.getLogger("CoinGeckoClient")


class CoinGeckoEndpoints:
    def __init__(self):
        self.ping_endpoint = PingEndpoint()
        self.coin_price_by_id_endpoint = CoinPriceByIdEndpoint()


class CoinGeckoClient:
    def __init__(
        self,
        settings: Settings,
        client: Optional[httpx.AsyncClient] = httpx.AsyncClient(),
    ):
        if not settings.COINGECKO_API_KEY:
            raise CoinGeckoMissingAPIKeyError("A valid API key is needed for CoinGecko")

        if not settings.COINGECKO_BASE_URL:
            raise CoinGeckoMissingBaseURLError(
                "A valid base URL is needed for making requests to CoinGecko"
            )

        self._api_key = settings.COINGECKO_API_KEY
        self._timeout = settings.COINGECKO_TIMEOUT or 10
        self._base_url = settings.COINGECKO_BASE_URL
        self._client = client

        self._endpoints = CoinGeckoEndpoints()

    def _headers(self) -> Dict[str, str]:
        return {"Accept": "application/json", "x-cg-demo-api-key": self._api_key}

    async def _request(
        self,
        endpoint: BaseEndpoint,
        body: Optional[RequestModel],
        query_params: Optional[QueryParamsModel],
    ) -> ResponseModel:
        url = f"{self._base_url}{endpoint.path}"
        if query_params:
            query = endpoint.build_query_params(query_params)
            url = f"{url}?{query}"
        headers = self._headers()
        method = endpoint.method
        request_body = endpoint.build_request_body(body) if body else None
        logger.info("Sending request %s %s", method, url)

        try:
            response = await self._client.request(
                method=method,
                url=url,
                headers=headers,
                timeout=self._timeout,
                json=request_body,
            )

            response.raise_for_status()
            response_data = response.json()
            if endpoint.response_model:
                try:
                    validated_response = endpoint.response_model(**response_data)
                    return validated_response.model_dump()
                except ValidationError as e:
                    raise CoinGeckoAPIError(f"Response validation error: {e}") from e

            return response_data
        except requests.exceptions.Timeout as exc:
            raise CoinGeckoAPIError("CoinGecko timeout exceeded") from exc
        except requests.exceptions.HTTPError as exc:
            raise CoinGeckoAPIError(
                f"HTTP error {response.status_code}: {response.text}"
            ) from exc
        except requests.exceptions.RequestException as exc:
            raise CoinGeckoAPIError(f"Network error: {exc}") from exc
        except ValueError as exc:
            raise CoinGeckoAPIError("Invalid response") from exc

    async def ping(self):
        return await self._request(
            self._endpoints.ping_endpoint, body=None, query_params=None
        )

    async def get_coins_price_py_id(self, coin_price_data: CoinPriceByIdParams):
        response = await self._request(
            self._endpoints.coin_price_by_id_endpoint,
            body=None,
            query_params=coin_price_data,
        )
        return self._endpoints.coin_price_by_id_endpoint.response_model.model_validate(
            response
        )
