# pylint: disable=duplicate-code
from fastapi import FastAPI
from prometheus_client import make_asgi_app

from common.observability.middleware import PrometheusMiddleware
from processor.endpoints import events, health
from processor.processor_service import ProcessorService


def build_processor_daemon(
    processor_service: ProcessorService,
):
    app = FastAPI(
        redoc_url="/",
        title="TFG Processor API",
    )

    app.openapi_version = "3.0.0"

    app.add_middleware(PrometheusMiddleware, service_name="processor-daemon")

    app.include_router(
        health.make_health_router(),
        prefix="/health",
        tags=["Health"],
    )

    app.include_router(
        events.make_events_router(
            processor_service=processor_service,
        ),
        prefix="/event",
        tags=["Events"],
    )

    metrics = make_asgi_app()
    app.mount("/metrics", metrics)

    return app
