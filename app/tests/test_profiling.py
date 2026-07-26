"""Unit tests for query scalability profiler and latency budget middleware."""

import pytest
from django_bolt.testing import TestClient

from app.api import api
from app.models import User
from app.profiling import (
    QueryScalabilityProfiler,
    UnscalableQueryError,
    assert_scalable_query,
)


@pytest.mark.django_db(transaction=True)
async def test_query_scalability_profiler_indexed_query():
    """Verify that querying by primary key is recognized as a scalable indexed query."""
    user = await User.objects.acreate(username="profiler_user", email="profiler@example.com")

    queryset = User.objects.filter(id=user.id)
    report = await QueryScalabilityProfiler.analyze_queryset(queryset)

    assert report.is_scalable is True
    assert len(report.detected_issues) == 0


@pytest.mark.django_db(transaction=True)
async def test_assert_scalable_query_unindexed_scan():
    """Verify that assert_scalable_query detects unindexed filter conditions."""
    # Searching by unindexed 'bio' column triggers full table scan detection
    queryset = User.objects.filter(bio="unindexed bio query search")

    with pytest.raises(UnscalableQueryError) as exc_info:
        await assert_scalable_query(queryset)

    assert "Query failed scalability assertion!" in str(exc_info.value)
    assert (
        "Unindexed" in str(exc_info.value)
        or "SCAN TABLE" in str(exc_info.value)
        or "Seq Scan" in str(exc_info.value)
    )


@pytest.mark.django_db(transaction=True)
async def test_assert_scalable_query_allow_seq_scan():
    """Verify allow_seq_scan=True bypasses table scan errors when order_by is cleared."""
    queryset = User.objects.filter(bio="unindexed bio query search").order_by()
    report = await assert_scalable_query(queryset, allow_seq_scan=True)

    assert report.raw_plan is not None


def test_latency_budget_middleware_headers():
    """Verify that LatencyBudgetMiddleware attaches performance telemetry headers."""
    client = TestClient(api)
    response = client.get("/health")

    assert response.status_code == 200
    assert "X-Response-Time-Ms" in response.headers
    assert response.headers.get("X-Latency-Budget-Passed") == "true"
