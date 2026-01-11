from http import HTTPStatus

from fastapi import APIRouter, HTTPException

from gateway.coingecko_service import CoinGeckoAPIService


def make_coins_router(coingecko_api_service: CoinGeckoAPIService) -> APIRouter:
    router = APIRouter()

    @router.post(
        "/fetch",
        summary="Makes a call to Coingecko and publishes to Kafka",
        status_code=HTTPStatus.OK,
    )
    async def fetch_coins():
        try:
            await coingecko_api_service.execute()
            return {
                "status": "success",
                "message": "Prices fetched and published to Kafka",
            }
        except Exception as e:
            raise HTTPException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                detail=f"Failed to fetch coins: {e}",
            ) from e

    return router
