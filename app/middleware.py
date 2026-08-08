"""Custom Middleware for django-lightning applications."""

import logging
import time
import uuid
from collections import deque
from typing import Any

from django_bolt import BaseMiddleware, Request, Response

logger = logging.getLogger("django.lightning.middleware")


class LatencyBudgetExceededError(RuntimeError):
    """Raised when an API endpoint exceeds the strict latency budget limit."""

    pass


class LatencyMetricsTracker:
    def __init__(self):
        self.total_requests = 0
        self.budget_passed = 0
        self.budget_exceeded = 0
        self.total_latency_ms = 0.0
        self.max_latency_ms = 0.0
        self.min_latency_ms = float("inf")
        # Bounded ring buffer: O(1) append/evict instead of O(n) list.pop(0).
        self.recent_latencies: deque[dict[str, Any]] = deque(maxlen=100)

    def record(self, method: str, path: str, elapsed_ms: float, passed: bool):
        self.total_requests += 1
        self.total_latency_ms += elapsed_ms
        if elapsed_ms > self.max_latency_ms:
            self.max_latency_ms = elapsed_ms
        if elapsed_ms < self.min_latency_ms:
            self.min_latency_ms = elapsed_ms

        if passed:
            self.budget_passed += 1
        else:
            self.budget_exceeded += 1

        self.recent_latencies.append(
            {
                "method": method,
                "path": path,
                "latency_ms": round(elapsed_ms, 2),
                "passed": passed,
                "timestamp": time.time(),
            }
        )

    def get_stats(self) -> dict[str, Any]:
        avg_latency = (
            round(self.total_latency_ms / self.total_requests, 2)
            if self.total_requests > 0
            else 0.0
        )
        return {
            "total_requests": self.total_requests,
            "budget_passed": self.budget_passed,
            "budget_exceeded": self.budget_exceeded,
            "avg_latency_ms": avg_latency,
            "max_latency_ms": round(self.max_latency_ms, 2) if self.max_latency_ms != 0.0 else 0.0,
            "min_latency_ms": round(self.min_latency_ms, 2)
            if self.min_latency_ms != float("inf")
            else 0.0,
            "compliance_rate_pct": (
                round((self.budget_passed / self.total_requests) * 100, 1)
                if self.total_requests > 0
                else 100.0
            ),
            "recent_requests": list(self.recent_latencies)[-10:],
        }


LATENCY_TRACKER = LatencyMetricsTracker()


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
        trace_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex[:16]

        response = await self.get_response(request)

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        passed = elapsed_ms <= self.max_latency_ms

        response.headers["X-Request-ID"] = trace_id
        response.headers["X-Response-Time-Ms"] = f"{elapsed_ms:.2f}"
        response.headers["X-Latency-Budget-Passed"] = "true" if passed else "false"

        LATENCY_TRACKER.record(request.method, request.path, elapsed_ms, passed)

        if not passed:
            msg = (
                f"🚨 LATENCY BUDGET EXCEEDED [< {self.max_latency_ms:.0f}ms Target]: "
                f"{request.method} {request.path} took {elapsed_ms:.2f}ms"
            )
            logger.warning(msg)

            if self.strict_mode:
                raise LatencyBudgetExceededError(msg)

        return response
