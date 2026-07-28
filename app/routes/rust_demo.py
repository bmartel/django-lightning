import msgspec
from django_bolt import BoltAPI

from app.native import aparallel_sum_floats, aparallel_transform_strings, is_rust_available


class RustStatusOut(msgspec.Struct):
    available: bool
    engine: str


class TransformStringsReq(msgspec.Struct):
    items: list[str]


class TransformStringsOut(msgspec.Struct):
    results: list[str]
    count: int
    engine: str


class HeavyMetricsReq(msgspec.Struct):
    values: list[float]


class HeavyMetricsOut(msgspec.Struct):
    sum: float
    count: int
    engine: str


def register_rust_routes(api: BoltAPI):
    @api.get(
        "/api/rust/status",
        response_model=RustStatusOut,
        tags=["Rust Native"],
        summary="Rust native core status check",
    )
    async def rust_status():
        avail = is_rust_available()
        return {
            "available": avail,
            "engine": "PyO3 Native C-Extension (GIL Released)" if avail else "Fallback Python",
        }

    @api.post(
        "/api/rust/transform-strings",
        response_model=TransformStringsOut,
        tags=["Rust Native"],
        summary="High-performance string transform in Rust",
    )
    async def rust_transform_strings(payload: TransformStringsReq):
        res = await aparallel_transform_strings(payload.items)
        return {
            "results": res,
            "count": len(res),
            "engine": "Rayon Parallel Rust" if is_rust_available() else "Python Fallback",
        }

    @api.post(
        "/api/rust/compute-metrics",
        response_model=HeavyMetricsOut,
        tags=["Rust Native"],
        summary="CPU-bound parallel metrics calculation in Rust",
    )
    async def rust_compute_metrics(payload: HeavyMetricsReq):
        total = await aparallel_sum_floats(payload.values)
        return {
            "sum": total,
            "count": len(payload.values),
            "engine": "Rayon Parallel Rust" if is_rust_available() else "Python Fallback",
        }
