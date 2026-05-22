# pylint: disable=duplicate-code
from fastapi import FastAPI
from prometheus_client import make_asgi_app

from common.observability.middleware import PrometheusMiddleware
from gateway.coingecko_service import CoinGeckoAPIService
from gateway.endpoints import coins, health


def build_coingecko_api_daemon(
    coingecko_api_service: CoinGeckoAPIService,
):
    app = FastAPI(
        redoc_url="/",
        title="TFG Coingecko API",
    )

    app.openapi_version = "3.0.0"

    app.add_middleware(PrometheusMiddleware, service_name="coingecko-api-daemon")

    app.include_router(
        health.make_health_router(),
        prefix="/health",
        tags=["Health"],
    )

    app.include_router(
        coins.make_coins_router(
            coingecko_api_service=coingecko_api_service,
        ),
        prefix="/coingecko",
        tags=["Coingecko API"],
    )

    metrics = make_asgi_app()
    app.mount("/metrics", metrics)

    return app
