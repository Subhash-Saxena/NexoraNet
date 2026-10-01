"""Educational query engine for hunting across security telemetry in NexoraNet.

Provides safe, whitelist-governed query building, parameterization, and execution.
Zero dynamic code execution (no eval/exec), zero raw SQL.
"""

from __future__ import annotations

import re
import time
from typing import Any, ClassVar

from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session

from app.models.threat_hunting import HuntEvent


class HuntQueryEngine:
    """Safe, educational query evaluator for threat hunting investigations."""

    ALLOWED_FIELDS: ClassVar[dict[str, str]] = {
        "source_ip": "str",
        "destination_ip": "str",
        "source_port": "int",
        "destination_port": "int",
        "protocol": "str",
        "domain": "str",
        "url": "str",
        "event_type": "str",
        "severity": "str",
        "action": "str",
        "status": "str",
        "summary": "str",
        "payload_preview": "str",
        "timestamp": "datetime",
    }

    OPERATOR_MAP: ClassVar[dict[str, str]] = {
        "eq": "==",
        "==": "==",
        "=": "==",
        "ne": "!=",
        "!=": "!=",
        "contains": "contains",
        "not_contains": "not_contains",
        "startswith": "startswith",
        "endswith": "endswith",
        "in": "in",
        "not_in": "not_in",
        "gt": ">",
        ">": ">",
        "gte": ">=",
        ">=": ">=",
        "lt": "<",
        "<": "<",
        "lte": "<=",
        "<=": "<=",
        "is_null": "is_null",
        "is_not_null": "is_not_null",
    }

    @classmethod
    def get_column(cls, field_name: str):
        """Map validated field name to SQLAlchemy model attribute."""
        if field_name not in cls.ALLOWED_FIELDS:
            raise ValueError(f"Field '{field_name}' is not queryable. Allowed fields: {list(cls.ALLOWED_FIELDS.keys())}")
        return getattr(HuntEvent, field_name)

    @classmethod
    def parse_text_query(cls, query_str: str) -> list[dict[str, Any]]:
        """Parse simple query string into structured conditions.

        Example:
            'protocol == "DNS" AND destination_port == 53'
        """
        if not query_str or not query_str.strip():
            return []

        # Split on AND / OR conjunctions (defaults to AND logic)
        raw_parts = re.split(r"\s+(?:AND|and)\s+", query_str.strip())
        conditions = []

        pattern = re.compile(
            r"([a-zA-Z_]+)\s*(==|!=|>=|<=|>|<|=|contains|not_contains|startswith|endswith|in|not_in)\s*(.+)",
            re.IGNORECASE,
        )

        for part in raw_parts:
            match = pattern.match(part.strip())
            if match:
                f_name, op, val = match.groups()
                f_name = f_name.strip().lower()
                op = op.strip().lower()
                val = val.strip().strip("'\"")

                if f_name in cls.ALLOWED_FIELDS:
                    # Cast integer fields
                    if cls.ALLOWED_FIELDS[f_name] == "int":
                        try:
                            val = int(val)
                        except ValueError:
                            pass
                    conditions.append({"field": f_name, "operator": op, "value": val})

        return conditions

    @classmethod
    def build_filter_clause(cls, condition: dict[str, Any]):
        """Convert a single condition dictionary into an SQLAlchemy binary expression."""
        field_name = condition.get("field", "").strip().lower()
        operator = condition.get("operator", "==").strip().lower()
        value = condition.get("value")

        if field_name not in cls.ALLOWED_FIELDS:
            raise ValueError(f"Invalid field: '{field_name}'")

        col = cls.get_column(field_name)
        canon_op = cls.OPERATOR_MAP.get(operator)
        if not canon_op:
            raise ValueError(f"Unsupported operator: '{operator}'")

        # Cast type if int
        if cls.ALLOWED_FIELDS[field_name] == "int" and value is not None and not isinstance(value, (list, tuple)):
            try:
                value = int(value)
            except (ValueError, TypeError):
                pass

        if canon_op == "==":
            if isinstance(value, str):
                return col.ilike(value)
            return col == value
        elif canon_op == "!=":
            if isinstance(value, str):
                return col.not_ilike(value)
            return col != value
        elif canon_op == "contains":
            return col.ilike(f"%{value}%")
        elif canon_op == "not_contains":
            return col.not_ilike(f"%{value}%")
        elif canon_op == "startswith":
            return col.ilike(f"{value}%")
        elif canon_op == "endswith":
            return col.ilike(f"%{value}")
        elif canon_op == "in":
            if isinstance(value, str):
                val_list = [v.strip() for v in value.split(",")]
            elif isinstance(value, (list, tuple)):
                val_list = list(value)
            else:
                val_list = [value]
            return col.in_(val_list)
        elif canon_op == "not_in":
            if isinstance(value, str):
                val_list = [v.strip() for v in value.split(",")]
            elif isinstance(value, (list, tuple)):
                val_list = list(value)
            else:
                val_list = [value]
            return col.not_in(val_list)
        elif canon_op == ">":
            return col > value
        elif canon_op == ">=":
            return col >= value
        elif canon_op == "<":
            return col < value
        elif canon_op == "<=":
            return col <= value
        elif canon_op == "is_null":
            return col.is_(None)
        elif canon_op == "is_not_null":
            return col.is_not(None)

        return None

    @classmethod
    def execute_hunt_query(
        cls,
        db: Session,
        dataset_id: int | None = None,
        conditions: list[dict[str, Any]] | None = None,
        query_string: str | None = None,
        search_text: str | None = None,
        conjunction: str = "AND",
        limit: int = 50,
        offset: int = 0,
        sort_by: str = "timestamp",
        sort_desc: bool = True,
    ) -> dict[str, Any]:
        """Execute structured or free-text query with timing and explanation."""
        start_time = time.perf_counter()

        # Normalize limits
        limit = max(1, min(limit, 500))
        offset = max(0, offset)

        clauses = []

        # Scope by dataset if provided
        if dataset_id is not None:
            clauses.append(HuntEvent.dataset_id == dataset_id)

        # Parse text query if provided and conditions not explicit
        parsed_conditions = list(conditions or [])
        if query_string and not parsed_conditions:
            parsed_conditions = cls.parse_text_query(query_string)

        condition_clauses = []
        for cond in parsed_conditions:
            try:
                clause = cls.build_filter_clause(cond)
                if clause is not None:
                    condition_clauses.append(clause)
            except ValueError:
                # Skip invalid conditions gracefully
                continue

        if condition_clauses:
            if conjunction.upper() == "OR":
                clauses.append(or_(*condition_clauses))
            else:
                clauses.append(and_(*condition_clauses))

        # Free text search across common string fields
        if search_text and search_text.strip():
            st = f"%{search_text.strip()}%"
            text_clause = or_(
                HuntEvent.summary.ilike(st),
                HuntEvent.source_ip.ilike(st),
                HuntEvent.destination_ip.ilike(st),
                HuntEvent.domain.ilike(st),
                HuntEvent.protocol.ilike(st),
                HuntEvent.event_type.ilike(st),
                HuntEvent.action.ilike(st),
            )
            clauses.append(text_clause)

        base_stmt = select(HuntEvent)
        if clauses:
            base_stmt = base_stmt.where(and_(*clauses))

        # Count total
        count_stmt = select(HuntEvent.id)
        if clauses:
            count_stmt = count_stmt.where(and_(*clauses))
        total_matched = len(db.scalars(count_stmt).all())

        # Sort order
        sort_col = getattr(HuntEvent, sort_by, HuntEvent.timestamp)
        if sort_desc:
            base_stmt = base_stmt.order_by(sort_col.desc())
        else:
            base_stmt = base_stmt.order_by(sort_col.asc())

        # Pagination
        paged_stmt = base_stmt.offset(offset).limit(limit)
        events = list(db.scalars(paged_stmt).all())

        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

        # Build educational explanation
        explanation_parts = []
        if dataset_id:
            explanation_parts.append(f"Filtered to Dataset ID {dataset_id}")
        if parsed_conditions:
            explanation_parts.append(
                f"Evaluated {len(parsed_conditions)} condition(s) with {conjunction.upper()} logic"
            )
        if search_text:
            explanation_parts.append(f"Keyword search for '{search_text}'")
        explanation_parts.append(f"Retrieved {len(events)} of {total_matched} matching telemetry events in {elapsed_ms}ms")

        return {
            "total": total_matched,
            "limit": limit,
            "offset": offset,
            "events": events,
            "took_ms": elapsed_ms,
            "conditions_used": parsed_conditions,
            "explanation": ". ".join(explanation_parts),
        }
