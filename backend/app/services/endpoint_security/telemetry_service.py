"""Endpoint Telemetry Service for querying, filtering, and analyzing synthetic host events."""

from datetime import datetime
from typing import Any

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.endpoint_security import EndpointEvent


class TelemetryService:
    """Handles query execution, category specialization, and timeline generation."""

    @staticmethod
    def list_events(
        db: Session,
        host_id: int | None = None,
        event_category: str | None = None,
        event_type: str | None = None,
        username: str | None = None,
        process_name: str | None = None,
        ip: str | None = None,
        domain: str | None = None,
        file_hash: str | None = None,
        severity: str | None = None,
        result: str | None = None,
        time_from: datetime | None = None,
        time_to: datetime | None = None,
        search: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[EndpointEvent], int]:
        """Query synthetic endpoint events with multi-field filtering and pagination."""
        stmt = select(EndpointEvent)

        if host_id:
            stmt = stmt.where(EndpointEvent.host_id == host_id)
        if event_category:
            stmt = stmt.where(EndpointEvent.event_category == event_category.upper())
        if event_type:
            stmt = stmt.where(EndpointEvent.event_type == event_type.upper())
        if username:
            stmt = stmt.where(EndpointEvent.username.ilike(f"%{username.strip()}%"))
        if process_name:
            stmt = stmt.where(EndpointEvent.process_name.ilike(f"%{process_name.strip()}%"))
        if ip:
            clean_ip = ip.strip()
            stmt = stmt.where(
                or_(
                    EndpointEvent.source_ip == clean_ip,
                    EndpointEvent.destination_ip == clean_ip,
                )
            )
        if domain:
            stmt = stmt.where(EndpointEvent.domain.ilike(f"%{domain.strip()}%"))
        if file_hash:
            stmt = stmt.where(EndpointEvent.file_hash == file_hash.strip().lower())
        if severity:
            stmt = stmt.where(EndpointEvent.severity == severity.upper())
        if result:
            stmt = stmt.where(EndpointEvent.result == result.upper())
        if time_from:
            stmt = stmt.where(EndpointEvent.timestamp >= time_from)
        if time_to:
            stmt = stmt.where(EndpointEvent.timestamp <= time_to)
        if search:
            pattern = f"%{search.strip()}%"
            stmt = stmt.where(
                or_(
                    EndpointEvent.command_summary.ilike(pattern),
                    EndpointEvent.file_path.ilike(pattern),
                    EndpointEvent.raw_event_reference.ilike(pattern),
                    EndpointEvent.service_name.ilike(pattern),
                    EndpointEvent.auth_failure_reason.ilike(pattern),
                )
            )

        # Count total
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = db.scalar(count_stmt) or 0

        # Order and paginate
        stmt = stmt.order_by(EndpointEvent.timestamp.desc()).offset(skip).limit(limit)
        events = list(db.scalars(stmt).all())
        return events, total

    @staticmethod
    def get_event_by_id(db: Session, identifier: str | int) -> EndpointEvent | None:
        """Fetch single event by database ID or event_id string (e.g. EE-2026-0001)."""
        if isinstance(identifier, int) or (isinstance(identifier, str) and identifier.isdigit()):
            event = db.get(EndpointEvent, int(identifier))
            if event:
                return event

        stmt = select(EndpointEvent).where(EndpointEvent.event_id == str(identifier).strip())
        return db.scalars(stmt).first()

    @staticmethod
    def get_authentication_events(
        db: Session,
        host_id: int,
        username: str | None = None,
        result: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> dict[str, Any]:
        """Fetch authentication activity with educational pattern detection."""
        stmt = select(EndpointEvent).where(
            EndpointEvent.host_id == host_id,
            EndpointEvent.event_category == "AUTHENTICATION",
        )
        if username:
            stmt = stmt.where(EndpointEvent.username.ilike(f"%{username.strip()}%"))
        if result:
            stmt = stmt.where(EndpointEvent.result == result.upper())

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = db.scalar(count_stmt) or 0

        stmt = stmt.order_by(EndpointEvent.timestamp.asc()).offset(skip).limit(limit)
        events = list(db.scalars(stmt).all())

        # Analyze authentication sequence for suspicious patterns
        failures_count = sum(1 for e in events if e.result == "FAILURE")
        successes_count = sum(1 for e in events if e.result == "SUCCESS")

        pattern_analysis = None
        if failures_count >= 3:
            # Check if failures were followed by success
            last_event = events[-1] if events else None
            if last_event and last_event.result == "SUCCESS":
                pattern_analysis = {
                    "pattern": "MULTIPLE_FAILURES_THEN_SUCCESS",
                    "label": "Pattern requiring investigation",
                    "explanation": (
                        f"Detected {failures_count} authentication failure(s) followed by a successful login. "
                        "Analyst note: This pattern may indicate successful brute-force or credential guessing, "
                        "or a legitimate user mistyping their password. Reconstruct timeline and check subsequent process activity."
                    ),
                    "confidence": "MEDIUM",
                }
            else:
                pattern_analysis = {
                    "pattern": "REPEATED_AUTHENTICATION_FAILURES",
                    "label": "Pattern requiring investigation",
                    "explanation": (
                        f"Detected {failures_count} consecutive authentication failures. "
                        "Inspect originating IP and targeted username for potential brute-force or spray attempts."
                    ),
                    "confidence": "LOW",
                }

        return {
            "total": total,
            "events": events,
            "summary": {
                "total_attempts": total,
                "successful_logins": successes_count,
                "failed_logins": failures_count,
                "pattern_analysis": pattern_analysis,
            },
        }

    @staticmethod
    def get_process_events(
        db: Session,
        host_id: int,
        username: str | None = None,
        integrity_level: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[EndpointEvent], int]:
        """Fetch process creation and termination telemetry."""
        stmt = select(EndpointEvent).where(
            EndpointEvent.host_id == host_id,
            EndpointEvent.event_category == "PROCESS",
        )
        if username:
            stmt = stmt.where(EndpointEvent.username.ilike(f"%{username.strip()}%"))
        if integrity_level:
            stmt = stmt.where(EndpointEvent.integrity_level == integrity_level.upper())

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = db.scalar(count_stmt) or 0

        stmt = stmt.order_by(EndpointEvent.timestamp.desc()).offset(skip).limit(limit)
        return list(db.scalars(stmt).all()), total

    @staticmethod
    def get_network_events(
        db: Session,
        host_id: int,
        process_name: str | None = None,
        destination_ip: str | None = None,
        protocol: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[EndpointEvent], int]:
        """Fetch network connections and listener events."""
        stmt = select(EndpointEvent).where(
            EndpointEvent.host_id == host_id,
            EndpointEvent.event_category == "NETWORK",
        )
        if process_name:
            stmt = stmt.where(EndpointEvent.process_name.ilike(f"%{process_name.strip()}%"))
        if destination_ip:
            stmt = stmt.where(EndpointEvent.destination_ip == destination_ip.strip())
        if protocol:
            stmt = stmt.where(EndpointEvent.protocol == protocol.upper())

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = db.scalar(count_stmt) or 0

        stmt = stmt.order_by(EndpointEvent.timestamp.desc()).offset(skip).limit(limit)
        return list(db.scalars(stmt).all()), total

    @staticmethod
    def get_dns_events(
        db: Session,
        host_id: int,
        domain: str | None = None,
        process_name: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[EndpointEvent], int]:
        """Fetch DNS query telemetry for a host."""
        stmt = select(EndpointEvent).where(
            EndpointEvent.host_id == host_id,
            EndpointEvent.event_category == "DNS",
        )
        if domain:
            stmt = stmt.where(EndpointEvent.domain.ilike(f"%{domain.strip()}%"))
        if process_name:
            stmt = stmt.where(EndpointEvent.process_name.ilike(f"%{process_name.strip()}%"))

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = db.scalar(count_stmt) or 0

        stmt = stmt.order_by(EndpointEvent.timestamp.desc()).offset(skip).limit(limit)
        return list(db.scalars(stmt).all()), total

    @staticmethod
    def get_file_events(
        db: Session,
        host_id: int,
        file_action: str | None = None,
        file_hash: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[EndpointEvent], int]:
        """Fetch file system creation, modification, deletion, and read events."""
        stmt = select(EndpointEvent).where(
            EndpointEvent.host_id == host_id,
            EndpointEvent.event_category == "FILE",
        )
        if file_action:
            stmt = stmt.where(EndpointEvent.file_action == file_action.upper())
        if file_hash:
            stmt = stmt.where(EndpointEvent.file_hash == file_hash.strip().lower())

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = db.scalar(count_stmt) or 0

        stmt = stmt.order_by(EndpointEvent.timestamp.desc()).offset(skip).limit(limit)
        return list(db.scalars(stmt).all()), total

    @staticmethod
    def get_service_events(
        db: Session,
        host_id: int,
        service_action: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[EndpointEvent], int]:
        """Fetch system service state changes and installation telemetry."""
        stmt = select(EndpointEvent).where(
            EndpointEvent.host_id == host_id,
            EndpointEvent.event_category == "SERVICE",
        )
        if service_action:
            stmt = stmt.where(EndpointEvent.service_action == service_action.upper())

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = db.scalar(count_stmt) or 0

        stmt = stmt.order_by(EndpointEvent.timestamp.desc()).offset(skip).limit(limit)
        return list(db.scalars(stmt).all()), total

    @staticmethod
    def get_persistence_events(
        db: Session,
        host_id: int,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[EndpointEvent], int]:
        """Fetch scheduled tasks, startup entries, and persistence indicators."""
        stmt = select(EndpointEvent).where(
            EndpointEvent.host_id == host_id,
            or_(
                EndpointEvent.event_category == "PERSISTENCE",
                EndpointEvent.persistence_type.is_not(None),
                EndpointEvent.event_type.in_(
                    ["SCHEDULED_TASK_CREATED", "SCHEDULED_TASK_MODIFIED"]
                ),
            ),
        )
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = db.scalar(count_stmt) or 0

        stmt = stmt.order_by(EndpointEvent.timestamp.desc()).offset(skip).limit(limit)
        return list(db.scalars(stmt).all()), total

    @staticmethod
    def get_privilege_events(
        db: Session,
        host_id: int,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[EndpointEvent], int]:
        """Fetch privilege changes, elevated processes, and sudo events."""
        stmt = select(EndpointEvent).where(
            EndpointEvent.host_id == host_id,
            or_(
                EndpointEvent.event_category == "PRIVILEGE",
                EndpointEvent.event_type == "PRIVILEGE_CHANGE",
                EndpointEvent.integrity_level.in_(["ELEVATED", "SYSTEM"]),
            ),
        )
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = db.scalar(count_stmt) or 0

        stmt = stmt.order_by(EndpointEvent.timestamp.desc()).offset(skip).limit(limit)
        return list(db.scalars(stmt).all()), total

    @staticmethod
    def get_timeline(
        db: Session,
        host_id: int,
        categories: list[str] | None = None,
        time_from: datetime | None = None,
        time_to: datetime | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[EndpointEvent], int]:
        """Unified chronological timeline of all activities on the endpoint."""
        stmt = select(EndpointEvent).where(EndpointEvent.host_id == host_id)

        if categories:
            clean_cats = [c.upper() for c in categories]
            stmt = stmt.where(EndpointEvent.event_category.in_(clean_cats))
        if time_from:
            stmt = stmt.where(EndpointEvent.timestamp >= time_from)
        if time_to:
            stmt = stmt.where(EndpointEvent.timestamp <= time_to)

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = db.scalar(count_stmt) or 0

        # Timeline is strictly chronological ascending
        stmt = stmt.order_by(EndpointEvent.timestamp.asc()).offset(skip).limit(limit)
        events = list(db.scalars(stmt).all())
        return events, total
