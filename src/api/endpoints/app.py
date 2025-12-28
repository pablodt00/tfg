from fastapi import FastAPI

from api.api_service import APIService
from api.endpoints import alerts, coins, health


def build_api(
    api_service: APIService,
):
    app = FastAPI(
        redoc_url="/",
        title="TFG API",
    )

    app.openapi_version = "3.0.0"

    app.include_router(
        health.make_health_router(),
        prefix="/health",
        tags=["Health"],
    )

    app.include_router(
        alerts.make_alerts_router(
            api_service=api_service,
        ),
        prefix="/alerts",
        tags=["Alerts"],
    )

    app.include_router(
        coins.make_coins_router(
            api_service=api_service,
        ),
        prefix="/coins",
        tags=["Coins"],
    )

    return app
