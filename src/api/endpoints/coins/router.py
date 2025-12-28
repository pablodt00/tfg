from http import HTTPStatus

from fastapi import APIRouter, HTTPException

from api.api_service import APIService


def make_coins_router(api_service: APIService) -> APIRouter:
    router = APIRouter()

    @router.get(
        "/coins",
        summary="Return a list of coins and values",
        description="Return a list of coins and values",
        status_code=HTTPStatus.OK,
    )
    async def get_coins():
        try:
            return await api_service.get_coins()
        except Exception as e:
            raise HTTPException(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                f"Failed to fetch coins: {e}",
            ) from e

    return router
