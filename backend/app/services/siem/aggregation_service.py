"""SIEM Aggregation Service for NexoraNet Step 15.

Provides bounded analytical aggregation metrics, entity rankings, and time-series
histograms for dashboard visualizations and SOC trend analysis.
"""

from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from app.models.enums import SecurityEventCategory, SecurityEventSeverity
from app.models.siem import SecurityEvent, SecurityLogDataset


class SiemAggregationService:
    """Computes bounded statistical summaries and time series histograms."""

    @classmethod
    def get_dashboard_metrics(
        cls,
        db: Session,
        dataset_id: int | None = None,
        time_preset: str | None = None,
    ) -> dict[str, Any]:
        """Compute top-level summary metrics for the SIEM dashboard."""
        filters = []
        if dataset_id:
            filters.append(SecurityEvent.dataset_id == dataset_id)

        now = datetime.now(timezone.utc)
        if time_preset and time_preset.lower() != "all":
            preset = time_preset.lower()
            delta_map = {
                "5m": timedelta(minutes=5),
                "15m": timedelta(minutes=15),
                "1h": timedelta(hours=1),
                "6h": timedelta(hours=6),
                "24h": timedelta(hours=24),
                "7d": timedelta(days=7),
            }
            if preset in delta_map:
                filters.append(SecurityEvent.timestamp >= now - delta_map[preset])
            elif preset == "dataset" and dataset_id:
                ds = db.execute(
                    select(SecurityLogDataset).where(SecurityLogDataset.id == dataset_id)
                ).scalar_one_or_none()
                if ds and ds.start_time and ds.end_time:
                    filters.append(SecurityEvent.timestamp >= ds.start_time)
                    filters.append(SecurityEvent.timestamp <= ds.end_time)

        # 1. Total Events
        total_stmt = select(func.count(SecurityEvent.id))
        if filters:
            total_stmt = total_stmt.where(and_(*filters))
        total_events = db.execute(total_stmt).scalar_one()

        # 2. Counts by Severity
        sev_stmt = (
            select(SecurityEvent.severity, func.count(SecurityEvent.id))
            .group_by(SecurityEvent.severity)
        )
        if filters:
            sev_stmt = sev_stmt.where(and_(*filters))
        by_severity = {row[0]: row[1] for row in db.execute(sev_stmt).all()}

        # 3. Counts by Source Type
        src_stmt = (
            select(SecurityEvent.source_type, func.count(SecurityEvent.id))
            .group_by(SecurityEvent.source_type)
            .order_by(func.count(SecurityEvent.id).desc())
            .limit(10)
        )
        if filters:
            src_stmt = src_stmt.where(and_(*filters))
        by_source_type = {row[0]: row[1] for row in db.execute(src_stmt).all()}

        # 4. Counts by Event Category
        cat_stmt = (
            select(SecurityEvent.event_category, func.count(SecurityEvent.id))
            .group_by(SecurityEvent.event_category)
            .order_by(func.count(SecurityEvent.id).desc())
            .limit(10)
        )
        if filters:
            cat_stmt = cat_stmt.where(and_(*filters))
        by_category = {row[0]: row[1] for row in db.execute(cat_stmt).all()}

        # 5. Key Counter Indicators
        # Authentication Failures
        auth_fail_stmt = select(func.count(SecurityEvent.id)).where(
            SecurityEvent.action == "LOGIN_FAILURE"
        )
        if filters:
            auth_fail_stmt = auth_fail_stmt.where(and_(*filters))
        auth_failures = db.execute(auth_fail_stmt).scalar_one()

        # Firewall Blocks
        fw_block_stmt = select(func.count(SecurityEvent.id)).where(
            SecurityEvent.action == "CONNECTION_BLOCKED"
        )
        if filters:
            fw_block_stmt = fw_block_stmt.where(and_(*filters))
        firewall_blocks = db.execute(fw_block_stmt).scalar_one()

        # DNS Queries
        dns_query_stmt = select(func.count(SecurityEvent.id)).where(
            SecurityEvent.event_category == SecurityEventCategory.DNS.value
        )
        if filters:
            dns_query_stmt = dns_query_stmt.where(and_(*filters))
        dns_queries = db.execute(dns_query_stmt).scalar_one()

        # High/Critical Events Count
        high_sev_count = (
            by_severity.get(SecurityEventSeverity.HIGH.value, 0)
            + by_severity.get(SecurityEventSeverity.CRITICAL.value, 0)
        )

        # 6. Top Entities (Rankings)
        top_source_ips = cls._get_top_ranked(db, SecurityEvent.source_ip, filters, 8)
        top_dest_ports = cls._get_top_ranked(db, SecurityEvent.destination_port, filters, 8)
        top_hosts = cls._get_top_ranked(db, SecurityEvent.host, filters, 8)
        top_users = cls._get_top_ranked(db, SecurityEvent.username, filters, 8)
        top_domains = cls._get_top_ranked(db, SecurityEvent.domain, filters, 8)

        # 7. Time series histogram (10-15 buckets)
        timeline = cls.get_time_series_histogram(db, dataset_id, filters)

        return {
            "total_events": total_events,
            "auth_failures": auth_failures,
            "firewall_blocks": firewall_blocks,
            "dns_queries": dns_queries,
            "high_severity_count": high_sev_count,
            "by_severity": by_severity,
            "by_source_type": by_source_type,
            "by_category": by_category,
            "top_source_ips": top_source_ips,
            "top_dest_ports": top_dest_ports,
            "top_hosts": top_hosts,
            "top_users": top_users,
            "top_domains": top_domains,
            "timeline": timeline,
        }

    @classmethod
    def _get_top_ranked(
        cls, db: Session, column: Any, filters: list[Any], limit: int = 10
    ) -> list[dict[str, Any]]:
        """Get top frequency values for a specific event column."""
        stmt = (
            select(column, func.count(SecurityEvent.id).label("count"))
            .where(column.isnot(None))
            .where(column != "")
        )
        if filters:
            stmt = stmt.where(and_(*filters))
        stmt = stmt.group_by(column).order_by(func.count(SecurityEvent.id).desc()).limit(limit)

        results = []
        for val, cnt in db.execute(stmt).all():
            results.append({"name": str(val), "count": cnt})
        return results

    @classmethod
    def get_time_series_histogram(
        cls,
        db: Session,
        dataset_id: int | None = None,
        base_filters: list[Any] | None = None,
        bucket_count: int = 12,
    ) -> list[dict[str, Any]]:
        """Construct chronological time series histogram buckets."""
        filters = list(base_filters or [])
        if dataset_id and not any("dataset_id" in str(f) for f in filters):
            filters.append(SecurityEvent.dataset_id == dataset_id)

        # Determine time span
        min_ts_stmt = select(func.min(SecurityEvent.timestamp), func.max(SecurityEvent.timestamp))
        if filters:
            min_ts_stmt = min_ts_stmt.where(and_(*filters))
        min_ts, max_ts = db.execute(min_ts_stmt).one()

        if not min_ts or not max_ts:
            return []

        if min_ts.tzinfo is None:
            min_ts = min_ts.replace(tzinfo=timezone.utc)
        if max_ts.tzinfo is None:
            max_ts = max_ts.replace(tzinfo=timezone.utc)

        duration = (max_ts - min_ts).total_seconds()
        if duration <= 0:
            duration = 3600  # Default 1 hr if instantaneous

        bucket_seconds = max(duration / bucket_count, 60)  # at least 1 min
        buckets = []

        for i in range(bucket_count):
            b_start = min_ts + timedelta(seconds=i * bucket_seconds)
            b_end = min_ts + timedelta(seconds=(i + 1) * bucket_seconds)

            b_filters = [
                SecurityEvent.timestamp >= b_start,
                SecurityEvent.timestamp < b_end,
            ]
            if filters:
                b_filters.extend(filters)

            # Query bucket totals
            t_stmt = select(func.count(SecurityEvent.id)).where(and_(*b_filters))
            tot = db.execute(t_stmt).scalar_one()

            # Auth failures
            af_stmt = select(func.count(SecurityEvent.id)).where(
                and_(*b_filters, SecurityEvent.action == "LOGIN_FAILURE")
            )
            af = db.execute(af_stmt).scalar_one()

            # Firewall blocks
            fw_stmt = select(func.count(SecurityEvent.id)).where(
                and_(*b_filters, SecurityEvent.action == "CONNECTION_BLOCKED")
            )
            fw = db.execute(fw_stmt).scalar_one()

            # DNS
            dns_stmt = select(func.count(SecurityEvent.id)).where(
                and_(*b_filters, SecurityEvent.event_category == SecurityEventCategory.DNS.value)
            )
            dns = db.execute(dns_stmt).scalar_one()

            buckets.append(
                {
                    "bucket": b_start.strftime("%H:%M:%S"),
                    "timestamp": b_start.isoformat(),
                    "total": tot,
                    "auth_failures": af,
                    "firewall_blocks": fw,
                    "dns_queries": dns,
                }
            )

        return buckets
