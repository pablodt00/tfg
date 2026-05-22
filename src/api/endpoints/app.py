from fastapi import FastAPI
from prometheus_client import make_asgi_app

from api.api_service import APIService
from api.endpoints import alerts, coins, health
from common.observability.middleware import PrometheusMiddleware


def build_api(
    api_service: APIService,
):
    app = FastAPI(
        redoc_url="/",
        title="TFG API",
    )

    app.openapi_version = "3.0.0"

    app.add_middleware(PrometheusMiddleware, service_name="api-daemon")

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

    metrics = make_asgi_app()
    app.mount("/metrics", metrics)

    return app
