"""Host inventory, summary metrics, and overview service for synthetic endpoints."""

from typing import Any

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.endpoint_security import (
    EndpointEvent,
    EndpointHost,
    EndpointInvestigation,
)


class HostService:
    """Provides querying and aggregation logic for synthetic training hosts."""

    @staticmethod
    def list_hosts(
        db: Session,
        platform: str | None = None,
        status: str | None = None,
        environment: str | None = None,
        risk_level: str | None = None,
        search: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[EndpointHost], int]:
        """List synthetic hosts with filtering, text search, and pagination."""
        stmt = select(EndpointHost)

        if platform:
            stmt = stmt.where(EndpointHost.platform == platform.upper())
        if status:
            stmt = stmt.where(EndpointHost.status == status.upper())
        if environment:
            stmt = stmt.where(EndpointHost.environment == environment.upper())
        if risk_level:
            stmt = stmt.where(EndpointHost.risk_level == risk_level.upper())
        if search:
            pattern = f"%{search.strip()}%"
            stmt = stmt.where(
                or_(
                    EndpointHost.hostname.ilike(pattern),
                    EndpointHost.display_name.ilike(pattern),
                    EndpointHost.stable_id.ilike(pattern),
                    EndpointHost.ip_address.ilike(pattern),
                    EndpointHost.description.ilike(pattern),
                )
            )

        # Count total
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = db.scalar(count_stmt) or 0

        # Paginate
        stmt = stmt.order_by(EndpointHost.hostname.asc()).offset(skip).limit(limit)
        hosts = list(db.scalars(stmt).all())
        return hosts, total

    @staticmethod
    def get_host_by_id_or_stable_id(db: Session, identifier: str | int) -> EndpointHost | None:
        """Fetch a single host by integer ID or stable string ID (e.g. HOST-WIN-001) or hostname."""
        if isinstance(identifier, int) or (isinstance(identifier, str) and identifier.isdigit()):
            host = db.get(EndpointHost, int(identifier))
            if host:
                return host

        id_str = str(identifier).strip()
        stmt = select(EndpointHost).where(
            or_(
                EndpointHost.stable_id == id_str,
                EndpointHost.hostname.ilike(id_str),
            )
        )
        return db.scalars(stmt).first()

    @staticmethod
    def get_host_overview(db: Session, host: EndpointHost) -> dict[str, Any]:
        """Compile a multi-dimensional summary of a host's synthetic telemetry."""
        # 1. Event category counts
        cat_counts_stmt = (
            select(EndpointEvent.event_category, func.count(EndpointEvent.id))
            .where(EndpointEvent.host_id == host.id)
            .group_by(EndpointEvent.event_category)
        )
        cat_counts = dict(db.execute(cat_counts_stmt).all())

        # 2. Distinct users observed
        users_stmt = (
            select(EndpointEvent.username)
            .distinct()
            .where(
                EndpointEvent.host_id == host.id,
                EndpointEvent.username.is_not(None),
            )
        )
        users = [u for u in db.scalars(users_stmt).all() if u]

        # 3. Distinct processes
        proc_stmt = (
            select(EndpointEvent.process_name)
            .distinct()
            .where(
                EndpointEvent.host_id == host.id,
                EndpointEvent.process_name.is_not(None),
            )
        )
        processes = [p for p in db.scalars(proc_stmt).all() if p]

        # 4. Distinct services
        services_stmt = (
            select(EndpointEvent.service_name)
            .distinct()
            .where(
                EndpointEvent.host_id == host.id,
                EndpointEvent.service_name.is_not(None),
            )
        )
        services = [s for s in db.scalars(services_stmt).all() if s]

        # 5. Distinct network connection destinations
        net_dsts_stmt = (
            select(EndpointEvent.destination_ip)
            .distinct()
            .where(
                EndpointEvent.host_id == host.id,
                EndpointEvent.destination_ip.is_not(None),
            )
        )
        dest_ips = [ip for ip in db.scalars(net_dsts_stmt).all() if ip]

        # 6. Distinct DNS domains queried
        dns_stmt = (
            select(EndpointEvent.domain)
            .distinct()
            .where(
                EndpointEvent.host_id == host.id,
                EndpointEvent.domain.is_not(None),
            )
        )
        domains = [d for d in db.scalars(dns_stmt).all() if d]

        # 7. Distinct file hashes
        hashes_stmt = (
            select(EndpointEvent.file_hash)
            .distinct()
            .where(
                EndpointEvent.host_id == host.id,
                EndpointEvent.file_hash.is_not(None),
            )
        )
        hashes = [h for h in db.scalars(hashes_stmt).all() if h]

        # 8. Active investigations for this host
        inv_stmt = (
            select(EndpointInvestigation)
            .where(EndpointInvestigation.host_id == host.id)
            .order_by(EndpointInvestigation.created_at.desc())
            .limit(5)
        )
        investigations = list(db.scalars(inv_stmt).all())

        # 9. Recent high severity alerts
        alerts_stmt = (
            select(EndpointEvent)
            .where(
                EndpointEvent.host_id == host.id,
                EndpointEvent.severity.in_(["HIGH", "CRITICAL"]),
            )
            .order_by(EndpointEvent.timestamp.desc())
            .limit(5)
        )
        recent_alerts = list(db.scalars(alerts_stmt).all())

        return {
            "host": {
                "id": host.id,
                "stable_id": host.stable_id,
                "hostname": host.hostname,
                "display_name": host.display_name,
                "platform": host.platform,
                "platform_version": host.platform_version,
                "architecture": host.architecture,
                "environment": host.environment,
                "status": host.status,
                "risk_level": host.risk_level,
                "ip_address": host.ip_address,
                "mac_address": host.mac_address,
                "os_build": host.os_build,
                "description": host.description,
                "last_activity_at": host.last_activity_at.isoformat() if host.last_activity_at else None,
                "is_synthetic": host.is_synthetic,
            },
            "metrics": {
                "total_events": sum(cat_counts.values()),
                "users_count": len(users),
                "processes_count": len(processes),
                "services_count": len(services),
                "network_connections_count": cat_counts.get("NETWORK", 0),
                "dns_queries_count": cat_counts.get("DNS", 0),
                "file_events_count": cat_counts.get("FILE", 0),
                "auth_events_count": cat_counts.get("AUTHENTICATION", 0),
                "security_events_count": (
                    cat_counts.get("SECURITY", 0)
                    + cat_counts.get("PRIVILEGE", 0)
                    + cat_counts.get("PERSISTENCE", 0)
                ),
                "active_investigations_count": len(investigations),
            },
            "observed_entities": {
                "users": users[:10],
                "top_processes": processes[:10],
                "services": services[:10],
                "destination_ips": dest_ips[:10],
                "domains": domains[:10],
                "file_hashes": hashes[:10],
            },
            "category_breakdown": cat_counts,
            "recent_alerts": [
                {
                    "id": a.id,
                    "event_id": a.event_id,
                    "timestamp": a.timestamp.isoformat() if a.timestamp else None,
                    "event_type": a.event_type,
                    "event_category": a.event_category,
                    "severity": a.severity,
                    "process_name": a.process_name,
                    "username": a.username,
                    "action": a.action,
                    "result": a.result,
                    "raw_reference": a.raw_event_reference,
                }
                for a in recent_alerts
            ],
            "investigations": [
                {
                    "id": inv.id,
                    "stable_id": inv.stable_id,
                    "title": inv.title,
                    "status": inv.status,
                    "priority": inv.priority,
                    "created_at": inv.created_at.isoformat() if inv.created_at else None,
                }
                for inv in investigations
            ],
        }

    @staticmethod
    def get_endpoint_stats(db: Session) -> dict[str, Any]:
        """Compute platform-wide synthetic endpoint telemetry dashboard metrics."""
        total_hosts = db.scalar(select(func.count(EndpointHost.id))) or 0
        total_events = db.scalar(select(func.count(EndpointEvent.id))) or 0
        active_inv = db.scalar(
            select(func.count(EndpointInvestigation.id)).where(
                EndpointInvestigation.status.in_(["OPEN", "INVESTIGATING"])
            )
        ) or 0
        high_alerts = db.scalar(
            select(func.count(EndpointEvent.id)).where(
                EndpointEvent.severity.in_(["HIGH", "CRITICAL"])
            )
        ) or 0

        # Category distribution
        cat_counts = dict(
            db.execute(
                select(EndpointEvent.event_category, func.count(EndpointEvent.id)).group_by(
                    EndpointEvent.event_category
                )
            ).all()
        )

        # Severity distribution
        sev_counts = dict(
            db.execute(
                select(EndpointEvent.severity, func.count(EndpointEvent.id)).group_by(
                    EndpointEvent.severity
                )
            ).all()
        )

        # Risk distribution
        risk_counts = dict(
            db.execute(
                select(EndpointHost.risk_level, func.count(EndpointHost.id)).group_by(
                    EndpointHost.risk_level
                )
            ).all()
        )

        # Platform distribution
        plat_counts = dict(
            db.execute(
                select(EndpointHost.platform, func.count(EndpointHost.id)).group_by(
                    EndpointHost.platform
                )
            ).all()
        )

        # Top active hosts
        top_hosts_stmt = (
            select(
                EndpointHost.id,
                EndpointHost.stable_id,
                EndpointHost.hostname,
                EndpointHost.display_name,
                EndpointHost.platform,
                EndpointHost.risk_level,
                EndpointHost.status,
                func.count(EndpointEvent.id).label("event_count"),
            )
            .join(EndpointEvent, EndpointEvent.host_id == EndpointHost.id, isouter=True)
            .group_by(EndpointHost.id)
            .order_by(func.count(EndpointEvent.id).desc())
            .limit(5)
        )
        top_hosts = [
            {
                "id": row.id,
                "stable_id": row.stable_id,
                "hostname": row.hostname,
                "display_name": row.display_name,
                "platform": row.platform,
                "risk_level": row.risk_level,
                "status": row.status,
                "event_count": row.event_count,
            }
            for row in db.execute(top_hosts_stmt).all()
        ]

        return {
            "total_hosts": total_hosts,
            "total_events": total_events,
            "active_investigations": active_inv,
            "high_severity_alerts": high_alerts,
            "category_distribution": cat_counts,
            "severity_distribution": sev_counts,
            "risk_distribution": risk_counts,
            "platform_distribution": plat_counts,
            "top_active_hosts": top_hosts,
        }
