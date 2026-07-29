"""Custom Middleware for django-lightning applications."""

import logging
import time

from django_bolt import BaseMiddleware, Request, Response

logger = logging.getLogger("django.lightning.middleware")


class LatencyBudgetExceededError(RuntimeError):
    """Raised when an API endpoint exceeds the strict latency budget limit."""

    pass


class LatencyBudgetMiddleware(BaseMiddleware):
    """Enforces strict response latency performance budget (< 100ms) on all API endpoints.

    Tracks wall-clock request processing time, emits prominent logging alerts when
    budget thresholds are exceeded, and attaches telemetry headers to responses.
    """

    # Default paths to exclude from strict latency profiling
    exclude_paths: list[str] = ["/docs*", "/openapi.json", "/mcp*"]

    def __init__(
        self,
        get_response,
        max_latency_ms: float = 100.0,
        strict_mode: bool = False,
    ) -> None:
        super().__init__(get_response)
        self.max_latency_ms = max_latency_ms
        self.strict_mode = strict_mode

    async def process_request(self, request: Request) -> Response:
        start_time = time.perf_counter()

        response = await self.get_response(request)

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        passed = elapsed_ms <= self.max_latency_ms

        response.headers["X-Response-Time-Ms"] = f"{elapsed_ms:.2f}"
        response.headers["X-Latency-Budget-Passed"] = "true" if passed else "false"

        if not passed:
            msg = (
                f"🚨 LATENCY BUDGET EXCEEDED [< {self.max_latency_ms:.0f}ms Target]: "
                f"{request.method} {request.path} took {elapsed_ms:.2f}ms"
            )
            logger.warning(msg)

            if self.strict_mode:
                raise LatencyBudgetExceededError(msg)

        return response


