import logging
import time
import uuid

from fastapi import Request
from prometheus_client import Counter, Histogram
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logging import set_request_id

logger = logging.getLogger("app.http")

REQUEST_COUNT = Counter(
    "resume_api_http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status_code"],
)

REQUEST_LATENCY = Histogram(
    "resume_api_http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "path"],
)


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        set_request_id(request_id)
        request.state.request_id = request_id

        start = time.perf_counter()
        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception:
            status_code = 500
            raise
        finally:
            duration = time.perf_counter() - start
            route = request.scope.get("route")
            path_template = getattr(route, "path", request.url.path)

            REQUEST_COUNT.labels(
                method=request.method,
                path=path_template,
                status_code=str(status_code),
            ).inc()
            REQUEST_LATENCY.labels(
                method=request.method,
                path=path_template,
            ).observe(duration)

            logger.info(
                "request_completed",
                extra={
                    "event": "request_completed",
                    "duration_ms": round(duration * 1000, 2),
                    "status_code": status_code,
                    "path": path_template,
                },
            )

        response.headers["X-Request-ID"] = request_id
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Cache-Control"] = "no-store"
        return response
