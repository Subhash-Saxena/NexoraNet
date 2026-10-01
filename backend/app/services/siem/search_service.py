"""SIEM Search Service for NexoraNet Step 15.

Provides safe, whitelist-governed querying of normalized security events with
support for visual conditions, full-text keywords, time ranges, pagination,
saved searches, and search history.
"""

import json
import time
from datetime import datetime, timedelta, timezone
from typing import Any, ClassVar

from sqlalchemy import and_, func, not_, or_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.enums import SecurityEventCategory, SecurityEventSeverity
from app.models.siem import (
    SavedSearch,
    SearchHistory,
    SecurityEvent,
    SecurityLogDataset,
)


class SiemSearchService:
    """Safe AST query builder and search coordinator for SIEM events."""

    # Whitelisted fields for query builder
    ALLOWED_FIELDS: ClassVar[dict[str, Any]] = {
        "event_id": SecurityEvent.event_id,
        "event_type": SecurityEvent.event_type,
        "event_category": SecurityEvent.event_category,
        "source_type": SecurityEvent.source_type,
        "host": SecurityEvent.host,
        "username": SecurityEvent.username,
        "source_ip": SecurityEvent.source_ip,
        "source_port": SecurityEvent.source_port,
        "destination_ip": SecurityEvent.destination_ip,
        "destination_port": SecurityEvent.destination_port,
        "protocol": SecurityEvent.protocol,
        "action": SecurityEvent.action,
        "status": SecurityEvent.status,
        "severity": SecurityEvent.severity,
        "process_name": SecurityEvent.process_name,
        "domain": SecurityEvent.domain,
        "message": SecurityEvent.message,
        "timestamp": SecurityEvent.timestamp,
    }

    ALLOWED_OPERATORS: ClassVar[set[str]] = {
        "=",
        "!=",
        "CONTAINS",
        "STARTS_WITH",
        "ENDS_WITH",
        "IN",
        "NOT_IN",
        ">",
        "<",
        ">=",
        "<=",
    }

    @classmethod
    def execute_search(
        cls,
        db: Session,
        dataset_id: int | None = None,
        conditions: list[dict[str, Any]] | None = None,
        logical_op: str = "AND",
        not_conditions: list[dict[str, Any]] | None = None,
        search_text: str | None = None,
        time_preset: str | None = None,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        quick_filter: str | None = None,
        limit: int = 50,
        offset: int = 0,
        sort_by: str = "timestamp",
        sort_asc: bool = False,
        user_id: int | None = None,
    ) -> dict[str, Any]:
        """Execute structured search query and return matched events and execution metadata."""
        start_clock = time.perf_counter()
        limit = min(max(limit, 1), 100)
        offset = max(offset, 0)

        # Base filter list
        filters = []
        explanation_parts = []

        # 1. Dataset filter
        if dataset_id:
            filters.append(SecurityEvent.dataset_id == dataset_id)
            explanation_parts.append(f"dataset_id = {dataset_id}")

        # 2. Time range filtering
        if time_preset and time_preset.lower() != "all":
            preset = time_preset.lower()
            now = datetime.now(timezone.utc)
            delta_map = {
                "5m": timedelta(minutes=5),
                "15m": timedelta(minutes=15),
                "1h": timedelta(hours=1),
                "6h": timedelta(hours=6),
                "24h": timedelta(hours=24),
                "7d": timedelta(days=7),
            }
            if preset in delta_map:
                t_cutoff = now - delta_map[preset]
                filters.append(SecurityEvent.timestamp >= t_cutoff)
                explanation_parts.append(f"time >= now - {preset}")
            elif preset == "dataset" and dataset_id:
                ds = db.execute(
                    select(SecurityLogDataset).where(SecurityLogDataset.id == dataset_id)
                ).scalar_one_or_none()
                if ds and ds.start_time and ds.end_time:
                    filters.append(SecurityEvent.timestamp >= ds.start_time)
                    filters.append(SecurityEvent.timestamp <= ds.end_time)
                    explanation_parts.append(f"within dataset timeline ({ds.start_time.isoformat()} to {ds.end_time.isoformat()})")

        if start_time:
            filters.append(SecurityEvent.timestamp >= start_time)
            explanation_parts.append(f"time >= {start_time.isoformat()}")
        if end_time:
            filters.append(SecurityEvent.timestamp <= end_time)
            explanation_parts.append(f"time <= {end_time.isoformat()}")

        # 3. Quick filters
        if quick_filter:
            qf = quick_filter.upper()
            if qf == "FAILED_LOGINS":
                filters.append(SecurityEvent.action == "LOGIN_FAILURE")
                explanation_parts.append("quick_filter: FAILED_LOGINS")
            elif qf == "FIREWALL_BLOCKS":
                filters.append(SecurityEvent.action == "CONNECTION_BLOCKED")
                explanation_parts.append("quick_filter: FIREWALL_BLOCKS")
            elif qf == "DNS_ERRORS":
                filters.append(SecurityEvent.event_category == SecurityEventCategory.DNS.value)
                filters.append(SecurityEvent.status.in_(["NXDOMAIN", "SERVFAIL", "REFUSED"]))
                explanation_parts.append("quick_filter: DNS_ERRORS")
            elif qf == "HIGH_SEVERITY":
                filters.append(
                    SecurityEvent.severity.in_(
                        [SecurityEventSeverity.HIGH.value, SecurityEventSeverity.CRITICAL.value]
                    )
                )
                explanation_parts.append("quick_filter: HIGH_SEVERITY")
            elif qf == "AUTHENTICATION":
                filters.append(SecurityEvent.event_category == SecurityEventCategory.AUTHENTICATION.value)
                explanation_parts.append("quick_filter: AUTHENTICATION")
            elif qf == "NETWORK":
                filters.append(
                    SecurityEvent.event_category.in_(
                        [SecurityEventCategory.NETWORK.value, SecurityEventCategory.FIREWALL.value]
                    )
                )
                explanation_parts.append("quick_filter: NETWORK")
            elif qf == "WEB":
                filters.append(SecurityEvent.event_category == SecurityEventCategory.WEB.value)
                explanation_parts.append("quick_filter: WEB")

        # 4. Search text keyword filter
        if search_text and search_text.strip():
            clean_search = search_text.strip().replace("%", "").replace("_", "")
            term = f"%{clean_search}%"
            text_clause = or_(
                SecurityEvent.message.ilike(term),
                SecurityEvent.host.ilike(term),
                SecurityEvent.username.ilike(term),
                SecurityEvent.source_ip.ilike(term),
                SecurityEvent.destination_ip.ilike(term),
                SecurityEvent.domain.ilike(term),
                SecurityEvent.process_name.ilike(term),
            )
            filters.append(text_clause)
            explanation_parts.append(f"text CONTAINS '{clean_search}'")

        # 5. Visual Query Builder Conditions
        if conditions:
            cond_clauses = []
            for cond in conditions:
                clause = cls._build_single_condition(cond)
                if clause is not None:
                    cond_clauses.append(clause)
                    explanation_parts.append(
                        f"{cond.get('field')} {cond.get('operator')} '{cond.get('value')}'"
                    )

            if cond_clauses:
                if logical_op.upper() == "OR":
                    filters.append(or_(*cond_clauses))
                else:
                    filters.append(and_(*cond_clauses))

        # 6. Negated conditions (NOT)
        if not_conditions:
            not_clauses = []
            for n_cond in not_conditions:
                clause = cls._build_single_condition(n_cond)
                if clause is not None:
                    not_clauses.append(clause)
                    explanation_parts.append(
                        f"NOT ({n_cond.get('field')} {n_cond.get('operator')} '{n_cond.get('value')}')"
                    )
            if not_clauses:
                filters.append(not_(or_(*not_clauses)))

        # Build count query
        count_stmt = select(func.count(SecurityEvent.id))
        if filters:
            count_stmt = count_stmt.where(and_(*filters))
        total = db.execute(count_stmt).scalar_one()

        # Build data query
        query_stmt = select(SecurityEvent)
        if filters:
            query_stmt = query_stmt.where(and_(*filters))

        # Sort field
        sort_col = cls.ALLOWED_FIELDS.get(sort_by, SecurityEvent.timestamp)
        if sort_asc:
            query_stmt = query_stmt.order_by(sort_col.asc())
        else:
            query_stmt = query_stmt.order_by(sort_col.desc())

        query_stmt = query_stmt.offset(offset).limit(limit)
        events = db.execute(query_stmt).scalars().all()

        elapsed_ms = round((time.perf_counter() - start_clock) * 1000, 2)
        summary = " AND ".join(explanation_parts) if explanation_parts else "All security events"

        # Record history if user_id is given
        if user_id:
            try:
                hist = SearchHistory(
                    user_id=user_id,
                    query_definition=json.dumps(
                        {
                            "dataset_id": dataset_id,
                            "conditions": conditions or [],
                            "logical_op": logical_op,
                            "search_text": search_text,
                            "quick_filter": quick_filter,
                            "time_preset": time_preset,
                        }
                    ),
                    dataset_id=dataset_id,
                    result_count=total,
                    execution_time_ms=elapsed_ms,
                )
                db.add(hist)
                db.commit()
            except (SQLAlchemyError, json.JSONDecodeError, TypeError, ValueError):
                db.rollback()

        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "execution_time_ms": elapsed_ms,
            "human_readable": summary,
            "events": events,
        }

    @classmethod
    def _build_single_condition(cls, cond: dict[str, Any]) -> Any:
        """Parse single condition safely into a SQLAlchemy expression."""
        field_name = cond.get("field")
        op = cond.get("operator", "=").upper()
        val = cond.get("value")

        if not field_name or field_name not in cls.ALLOWED_FIELDS:
            return None
        if op not in cls.ALLOWED_OPERATORS:
            return None

        col = cls.ALLOWED_FIELDS[field_name]

        # Handle numeric fields
        if field_name in ("source_port", "destination_port"):
            try:
                val_num = int(val)
            except (ValueError, TypeError):
                return None
            if op == "=":
                return col == val_num
            elif op == "!=":
                return col != val_num
            elif op == ">":
                return col > val_num
            elif op == "<":
                return col < val_num
            elif op == ">=":
                return col >= val_num
            elif op == "<=":
                return col <= val_num
            return None

        val_str = str(val).strip() if val is not None else ""

        if op == "=":
            return col.ilike(val_str)
        elif op == "!=":
            return not_(col.ilike(val_str))
        elif op == "CONTAINS":
            clean = val_str.replace("%", "").replace("_", "")
            return col.ilike(f"%{clean}%")
        elif op == "STARTS_WITH":
            clean = val_str.replace("%", "").replace("_", "")
            return col.ilike(f"{clean}%")
        elif op == "ENDS_WITH":
            clean = val_str.replace("%", "").replace("_", "")
            return col.ilike(f"%{clean}")
        elif op == "IN":
            items = [item.strip() for item in val_str.split(",") if item.strip()]
            return col.in_(items) if items else None
        elif op == "NOT_IN":
            items = [item.strip() for item in val_str.split(",") if item.strip()]
            return not_(col.in_(items)) if items else None

        return None

    # Saved Searches CRUD
    @classmethod
    def create_saved_search(
        cls,
        db: Session,
        name: str,
        query_def: dict[str, Any],
        description: str | None = None,
        owner_id: int | None = None,
        is_public: bool = False,
    ) -> SavedSearch:
        """Create and persist a saved search definition."""
        saved = SavedSearch(
            name=name[:255],
            description=description,
            query_definition=json.dumps(query_def),
            owner_id=owner_id,
            is_public=is_public,
        )
        db.add(saved)
        db.commit()
        db.refresh(saved)
        return saved

    @classmethod
    def list_saved_searches(
        cls, db: Session, user_id: int | None = None, limit: int = 50
    ) -> list[SavedSearch]:
        """List saved searches accessible to the user (owned or public)."""
        stmt = select(SavedSearch)
        if user_id:
            stmt = stmt.where(or_(SavedSearch.owner_id == user_id, SavedSearch.is_public.is_(True)))
        else:
            stmt = stmt.where(SavedSearch.is_public.is_(True))
        stmt = stmt.order_by(SavedSearch.created_at.desc()).limit(limit)
        return list(db.execute(stmt).scalars().all())

    @classmethod
    def update_saved_search(
        cls,
        db: Session,
        search_id: int,
        user_id: int | None,
        name: str | None = None,
        description: str | None = None,
        query_def: dict[str, Any] | None = None,
        is_public: bool | None = None,
    ) -> SavedSearch:
        """Update a saved search owned by the user."""
        saved = db.execute(select(SavedSearch).where(SavedSearch.id == search_id)).scalar_one_or_none()
        if not saved:
            raise ValueError(f"Saved search {search_id} not found.")
        if saved.owner_id and saved.owner_id != user_id:
            raise PermissionError("You do not have permission to modify this saved search.")

        if name is not None:
            saved.name = name[:255]
        if description is not None:
            saved.description = description
        if query_def is not None:
            saved.query_definition = json.dumps(query_def)
        if is_public is not None:
            saved.is_public = is_public

        db.commit()
        db.refresh(saved)
        return saved

    @classmethod
    def delete_saved_search(cls, db: Session, search_id: int, user_id: int | None) -> bool:
        """Delete a saved search owned by the user."""
        saved = db.execute(select(SavedSearch).where(SavedSearch.id == search_id)).scalar_one_or_none()
        if not saved:
            return False
        if saved.owner_id and saved.owner_id != user_id:
            raise PermissionError("You do not have permission to delete this saved search.")
        db.delete(saved)
        db.commit()
        return True

    @classmethod
    def get_search_history(
        cls, db: Session, user_id: int | None, limit: int = 20
    ) -> list[SearchHistory]:
        """Fetch search history for user."""
        if not user_id:
            return []
        stmt = (
            select(SearchHistory)
            .where(SearchHistory.user_id == user_id)
            .order_by(SearchHistory.timestamp.desc())
            .limit(limit)
        )
        return list(db.execute(stmt).scalars().all())
