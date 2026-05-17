import time

from starlette.middleware.base import BaseHTTPMiddleware

from common.observability.metrics import (
    http_request_duration_seconds,
    http_requests_in_progress,
    http_requests_total,
)


class PrometheusMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, service_name: str):
        super().__init__(app)
        self.service_name = service_name

    async def dispatch(self, request, call_next):
        method = request.method
        endpoint = request.url.path

        http_requests_in_progress.labels(
            service_name=self.service_name, method=method, endpoint=endpoint
        ).inc()

        start = time.perf_counter()
        try:
            response = await call_next(request)
            status_code = str(response.status_code)
        except Exception:
            status_code = "500"
            raise
        finally:
            duration = time.perf_counter() - start
            http_requests_in_progress.labels(
                service_name=self.service_name, method=method, endpoint=endpoint
            ).dec()
            http_requests_total.labels(
                service_name=self.service_name,
                method=method,
                endpoint=endpoint,
                status_code=status_code,
            ).inc()
            http_request_duration_seconds.labels(
                service_name=self.service_name, method=method, endpoint=endpoint
            ).observe(duration)

        return response

