from http import HTTPStatus

from fastapi import APIRouter, HTTPException

from api.api_service import APIService
from common.client.endpoints.base_endpoint import RequestModel
from common.schemas.alert import AlertConditionEnum
from common.schemas.coin import CoinEnum


class NewAlertRequestModel(RequestModel):
    coin: CoinEnum
    amount: float
    email: str
    condition: AlertConditionEnum


def make_alerts_router(
    api_service: APIService,
) -> APIRouter:
    router = APIRouter()

    @router.post(
        "/add",
        summary="Add a new alert for a user",
        description="Add a new alert for a user",
        status_code=HTTPStatus.CREATED,
    )
    async def new_alert(
        request: NewAlertRequestModel,
    ):
        try:
            alert = await api_service.add_alert(
                email=request.email,
                coin=request.coin,
                amount=request.amount,
                condition=request.condition,
            )
            return alert
        except Exception as e:
            raise HTTPException(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                f"Failed to create alert: {e}",
            ) from e

    return router
