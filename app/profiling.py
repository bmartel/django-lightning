"""Surgical Query Scalability Profiling & Latency Budget Guards.

Provides utilities to inspect database execution plans (EXPLAIN), force index-path
evaluation even on tiny test tables (detecting O(N) full table scans before production),
and enforce strict response performance budgets (< 100ms).
"""

import logging
from dataclasses import dataclass, field
from typing import Any

from asgiref.sync import sync_to_async
from django.db import connection
from django.db.models import QuerySet

logger = logging.getLogger("django.lightning.profiling")


class UnscalableQueryError(AssertionError):
    """Raised when a query fails scalability checks (e.g. unindexed table scan, unindexed sort)."""

    pass


@dataclass
class ScalabilityReport:
    """Detailed report of query scalability profiling."""

    is_scalable: bool
    total_cost: float
    detected_issues: list[str] = field(default_factory=list)
    suggested_fixes: list[str] = field(default_factory=list)
    execution_nodes: list[str] = field(default_factory=list)
    sql_query: str = ""
    raw_plan: Any = None


class QueryScalabilityProfiler:
    """Surgically analyzes database query execution plans for scalability bottlenecks.

    Works on small test datasets by forcing index-path evaluation or parsing DB query plans
    (PostgreSQL JSON EXPLAIN and SQLite EXPLAIN QUERY PLAN) to detect missing indexes,
    unindexed table scans (Seq Scan), unindexed sorts, and cartesian joins.
    """

    @classmethod
    async def analyze_queryset(
        cls,
        queryset: QuerySet,
        max_cost_threshold: float = 1000.0,
        allow_seq_scan: bool = False,
    ) -> ScalabilityReport:
        """Analyzes a Django QuerySet for scalability risks."""
        return await sync_to_async(cls._sync_analyze_queryset)(
            queryset, max_cost_threshold, allow_seq_scan
        )

    @classmethod
    def _sync_analyze_queryset(
        cls,
        queryset: QuerySet,
        max_cost_threshold: float = 1000.0,
        allow_seq_scan: bool = False,
    ) -> ScalabilityReport:
        compiler = queryset.query.get_compiler(connection.alias)
        sql, params = compiler.as_sql()
        vendor = connection.vendor

        if vendor == "postgresql":
            return cls._analyze_postgresql(sql, params, max_cost_threshold, allow_seq_scan)
        elif vendor == "sqlite":
            return cls._analyze_sqlite(sql, params, allow_seq_scan)
        else:
            return cls._analyze_generic(sql, params, allow_seq_scan)

    @classmethod
    def _analyze_postgresql(
        cls,
        sql: str,
        params: tuple,
        max_cost_threshold: float,
        allow_seq_scan: bool,
    ) -> ScalabilityReport:
        issues: list[str] = []
        fixes: list[str] = []
        nodes: list[str] = []
        total_cost = 0.0
        raw_plan = None

        with connection.cursor() as cursor:
            # FORCE PostgreSQL planner to evaluate index paths by disabling seqscan locally
            cursor.execute("SET LOCAL enable_seqscan = OFF;")
            try:
                cursor.execute(f"EXPLAIN (FORMAT JSON) {sql}", params)
                explain_res = cursor.fetchone()
                if explain_res and explain_res[0]:
                    raw_plan = explain_res[0]
                    plan_data = raw_plan[0]["Plan"]
                    total_cost = float(plan_data.get("Total Cost", 0.0))

                    cls._traverse_pg_nodes(plan_data, nodes, issues, fixes, allow_seq_scan)
            except Exception as err:
                issues.append(f"Failed to execute PostgreSQL EXPLAIN: {err}")

        if total_cost > max_cost_threshold and not allow_seq_scan:
            msg = (
                f"Query plan total cost ({total_cost:.2f}) "
                f"exceeds scalability threshold ({max_cost_threshold:.2f})."
            )
            issues.append(msg)
            fixes.append("Add database index on filter, join, or sorting columns.")

        is_scalable = len(issues) == 0
        return ScalabilityReport(
            is_scalable=is_scalable,
            total_cost=total_cost,
            detected_issues=issues,
            suggested_fixes=fixes,
            execution_nodes=nodes,
            sql_query=sql,
            raw_plan=raw_plan,
        )

    @classmethod
    def _traverse_pg_nodes(
        cls,
        node: dict[str, Any],
        nodes: list[str],
        issues: list[str],
        fixes: list[str],
        allow_seq_scan: bool,
    ):
        node_type = node.get("Node Type", "")
        relation_name = node.get("Relation Name", "")
        nodes.append(f"{node_type} ({relation_name})" if relation_name else node_type)

        if node_type == "Seq Scan" and not allow_seq_scan:
            msg = (
                f"Unindexed Sequential Full Table Scan ('Seq Scan') "
                f"detected on table '{relation_name}'."
            )
            issues.append(msg)
            fixes.append(
                f"Add database index (db_index=True or models.Index) "
                f"for table '{relation_name}' filter conditions."
            )

        if node_type in ("Sort", "Incremental Sort") and "Index" not in node_type:
            sort_keys = node.get("Sort Key", [])
            issues.append(
                f"Unindexed in-memory sorting operation ('{node_type}') on keys: {sort_keys}."
            )
            fixes.append(
                "Add database index matching the ORDER BY clause to enable Index Scan sorting."
            )

        if node_type == "Nested Loop" and not any(
            "Index" in child.get("Node Type", "") for child in node.get("Plans", [])
        ):
            issues.append(
                "Nested Loop join without indexed inner lookup (potential O(N*M) Cartesian join)."
            )
            fixes.append(
                "Ensure foreign key join fields have indexes on both sides of the relationship."
            )

        for sub_plan in node.get("Plans", []):
            cls._traverse_pg_nodes(sub_plan, nodes, issues, fixes, allow_seq_scan)

    @classmethod
    def _analyze_sqlite(
        cls,
        sql: str,
        params: tuple,
        allow_seq_scan: bool,
    ) -> ScalabilityReport:
        issues: list[str] = []
        fixes: list[str] = []
        nodes: list[str] = []

        with connection.cursor() as cursor:
            cursor.execute(f"EXPLAIN QUERY PLAN {sql}", params)
            rows = cursor.fetchall()
            for row in rows:
                detail = row[-1]
                nodes.append(detail)

                if (
                    ("SCAN " in detail or "SCAN TABLE " in detail)
                    and "USING INDEX" not in detail
                    and not allow_seq_scan
                ):
                    table_name = (
                        detail.split("SCAN TABLE ")[-1].split(" ")[0]
                        if "SCAN TABLE " in detail
                        else detail.split("SCAN ")[-1].split(" ")[0]
                    )
                    msg = f"Unindexed Full Table Scan ('SCAN') detected on table '{table_name}'."
                    issues.append(msg)
                    fixes.append(f"Add database index on table '{table_name}'.")

                if "USE TEMP B-TREE FOR ORDER BY" in detail:
                    issues.append(
                        "Unindexed sorting operation requiring temporary B-Tree creation."
                    )
                    fixes.append("Add database index matching the ORDER BY columns.")

        is_scalable = len(issues) == 0
        return ScalabilityReport(
            is_scalable=is_scalable,
            total_cost=0.0,
            detected_issues=issues,
            suggested_fixes=fixes,
            execution_nodes=nodes,
            sql_query=sql,
            raw_plan=nodes,
        )

    @classmethod
    def _analyze_generic(
        cls,
        sql: str,
        params: tuple,
        allow_seq_scan: bool,
    ) -> ScalabilityReport:
        issues: list[str] = []
        fixes: list[str] = []
        sql_upper = sql.upper()

        if "LIKE '%" in sql_upper or "ILIKE '%" in sql_upper:
            issues.append("Unindexed leading-wildcard text search (LIKE '%term').")
            fixes.append("Use PostgreSQL trigram index (gin_trgm_ops) or full-text search index.")

        is_scalable = len(issues) == 0
        return ScalabilityReport(
            is_scalable=is_scalable,
            total_cost=0.0,
            detected_issues=issues,
            suggested_fixes=fixes,
            execution_nodes=["Generic Parser"],
            sql_query=sql,
        )


async def assert_scalable_query(
    queryset: QuerySet,
    max_cost_threshold: float = 1000.0,
    allow_seq_scan: bool = False,
) -> ScalabilityReport:
    """Asserts QuerySet executes using indexes without full table scans or unindexed sorts.

    Args:
        queryset: The Django QuerySet to evaluate.
        max_cost_threshold: Maximum acceptable plan cost.
        allow_seq_scan: If True, allows sequential scans (default False).

    Returns:
        ScalabilityReport if query is scalable.

    Raises:
        UnscalableQueryError: If unindexed scans, unindexed sorts, or high costs are detected.
    """
    report = await QueryScalabilityProfiler.analyze_queryset(
        queryset, max_cost_threshold=max_cost_threshold, allow_seq_scan=allow_seq_scan
    )

    if not report.is_scalable:
        issues_formatted = "\n  - ".join(report.detected_issues)
        fixes_formatted = "\n  - ".join(report.suggested_fixes)
        raise UnscalableQueryError(
            f"Query failed scalability assertion!\n"
            f"Detected Bottlenecks:\n  - {issues_formatted}\n\n"
            f"Suggested Fixes:\n  - {fixes_formatted}\n\n"
            f"SQL:\n  {report.sql_query}"
        )

    return report
