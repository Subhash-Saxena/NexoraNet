"""Dataset management and telemetry normalization service for threat hunting.

Supports offline ingestion from PCAP, Detection Alerts, SOC Alerts, and Threat Intel.
"""

from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.detection import DetectionAlert
from app.models.enums import HuntDatasetType, HuntEventType
from app.models.pcap import Capture, ParsedPacket
from app.models.soc import InvestigationAlert
from app.models.threat_hunting import HuntDataset, HuntEvent
from app.models.threat_intel import Indicator, IndicatorObservation


class HuntDatasetService:
    """Manages threat hunting datasets and telemetry ingestion pipelines."""

    @classmethod
    def list_datasets(
        cls,
        db: Session,
        dataset_type: str | None = None,
        status: str | None = None,
    ) -> list[HuntDataset]:
        """List available hunting datasets."""
        stmt = select(HuntDataset)
        if dataset_type:
            stmt = stmt.where(HuntDataset.dataset_type == dataset_type)
        if status:
            stmt = stmt.where(HuntDataset.status == status)
        stmt = stmt.order_by(HuntDataset.created_at.desc())
        return list(db.scalars(stmt).all())

    @classmethod
    def get_dataset(cls, db: Session, dataset_id: int) -> HuntDataset | None:
        """Fetch a dataset by internal integer ID."""
        return db.get(HuntDataset, dataset_id)

    @classmethod
    def get_dataset_by_code(cls, db: Session, dataset_code: str) -> HuntDataset | None:
        """Fetch a dataset by unique string code (e.g. DS-SYNTH-001)."""
        stmt = select(HuntDataset).where(HuntDataset.dataset_id == dataset_code)
        return db.scalar(stmt)

    @classmethod
    def create_dataset(
        cls,
        db: Session,
        dataset_id: str,
        name: str,
        description: str,
        dataset_type: str = HuntDatasetType.PCAP.value,
        source: str = "SYSTEM",
        metadata: dict[str, Any] | None = None,
    ) -> HuntDataset:
        """Create a new telemetry dataset."""
        dataset = HuntDataset(
            dataset_id=dataset_id,
            name=name,
            description=description,
            dataset_type=dataset_type,
            source=source,
            event_count=0,
            status="READY",
            metadata_json=json.dumps(metadata) if metadata else None,
        )
        db.add(dataset)
        db.commit()
        db.refresh(dataset)
        return dataset

    @classmethod
    def get_dataset_analytics(cls, db: Session, dataset_id: int) -> dict[str, Any]:
        """Aggregate protocol distribution, top IPs, domains, and event types for a dataset."""
        dataset = cls.get_dataset(db, dataset_id)
        if not dataset:
            return {}

        events = list(
            db.scalars(select(HuntEvent).where(HuntEvent.dataset_id == dataset_id)).all()
        )

        protocols = Counter([e.protocol for e in events if e.protocol])
        event_types = Counter([e.event_type for e in events if e.event_type])
        top_src_ips = Counter([e.source_ip for e in events if e.source_ip]).most_common(10)
        top_dst_ips = Counter([e.destination_ip for e in events if e.destination_ip]).most_common(10)
        top_domains = Counter([e.domain for e in events if e.domain]).most_common(10)

        timestamps = [e.timestamp for e in events if e.timestamp]
        earliest = min(timestamps).isoformat() if timestamps else None
        latest = max(timestamps).isoformat() if timestamps else None

        return {
            "dataset_id": dataset.id,
            "code": dataset.dataset_id,
            "name": dataset.name,
            "total_events": len(events),
            "time_range": {"start": earliest, "end": latest},
            "protocols": dict(protocols),
            "event_types": dict(event_types),
            "top_source_ips": [{"ip": ip, "count": count} for ip, count in top_src_ips],
            "top_destination_ips": [{"ip": ip, "count": count} for ip, count in top_dst_ips],
            "top_domains": [{"domain": dom, "count": count} for dom, count in top_domains],
        }

    @classmethod
    def sync_from_pcap(cls, db: Session, capture_id: int, dataset_id: int) -> int:
        """Ingest ParsedPacket records from a PCAP capture into HuntEvent records."""
        capture = db.get(Capture, capture_id)
        dataset = db.get(HuntDataset, dataset_id)
        if not capture or not dataset:
            return 0

        packets = list(
            db.scalars(
                select(ParsedPacket)
                .where(ParsedPacket.capture_id == capture_id)
                .order_by(ParsedPacket.packet_number)
            ).all()
        )

        created_count = 0
        for pkt in packets:
            event_code = f"EVT-PKT-{capture.id}-{pkt.packet_number:05d}"
            if db.scalar(select(HuntEvent.id).where(HuntEvent.event_id == event_code)):
                continue

            # Determine event type
            proto = (pkt.protocol or "").upper()
            if proto == "DNS":
                evt_type = HuntEventType.DNS_QUERY.value
            elif proto in ("HTTP", "HTTPS"):
                evt_type = HuntEventType.HTTP_REQUEST.value
            elif proto == "TCP":
                evt_type = HuntEventType.TCP_EVENT.value
            elif proto == "UDP":
                evt_type = HuntEventType.UDP_EVENT.value
            elif proto == "ICMP":
                evt_type = HuntEventType.ICMP_EVENT.value
            elif proto == "ARP":
                evt_type = HuntEventType.ARP_EVENT.value
            else:
                evt_type = HuntEventType.NETWORK_CONNECTION.value

            pkt_len = pkt.captured_length or pkt.original_length or 0
            if isinstance(pkt.timestamp, (int, float)):
                try:
                    pkt_ts = datetime.fromtimestamp(pkt.timestamp, tz=timezone.utc)
                except (ValueError, TypeError, OSError):
                    pkt_ts = datetime.now(timezone.utc)
            else:
                pkt_ts = datetime.now(timezone.utc)

            summary = f"[{proto}] {pkt.source_ip or 'unknown'}:{pkt.source_port or 0} -> {pkt.destination_ip or 'unknown'}:{pkt.destination_port or 0} ({pkt_len} bytes) - {pkt.info}"

            event = HuntEvent(
                event_id=event_code,
                dataset_id=dataset.id,
                event_type=evt_type,
                timestamp=pkt_ts,
                source_ip=pkt.source_ip,
                destination_ip=pkt.destination_ip,
                source_port=pkt.source_port,
                destination_port=pkt.destination_port,
                protocol=proto,
                pcap_capture_id=capture.id,
                pcap_packet_number=pkt.packet_number,
                summary=summary[:500],
                payload_preview=pkt.layer_details,
            )
            db.add(event)
            created_count += 1

        dataset.event_count += created_count
        db.commit()
        return created_count

    @classmethod
    def sync_from_detection_alerts(cls, db: Session, dataset_id: int) -> int:
        """Ingest DetectionAlert records into HuntEvent records."""
        dataset = db.get(HuntDataset, dataset_id)
        if not dataset:
            return 0

        alerts = list(db.scalars(select(DetectionAlert)).all())
        created_count = 0
        for alert in alerts:
            event_code = f"EVT-DET-{alert.id:05d}"
            if db.scalar(select(HuntEvent.id).where(HuntEvent.event_id == event_code)):
                continue

            event = HuntEvent(
                event_id=event_code,
                dataset_id=dataset.id,
                event_type=HuntEventType.DETECTION_ALERT.value,
                timestamp=alert.created_at,
                source_ip=alert.source_ip,
                destination_ip=alert.destination_ip,
                source_port=alert.source_port,
                destination_port=alert.destination_port,
                protocol=alert.protocol or "TCP",
                alert_id=alert.id,
                severity=alert.severity,
                action="ALERT",
                status=alert.status,
                summary=f"Detection Alert: {alert.title} - {alert.description[:120]}",
                metadata_json=json.dumps({"mitre_tactic": alert.mitre_tactic, "mitre_technique": alert.mitre_technique}),
            )
            db.add(event)
            created_count += 1

        dataset.event_count += created_count
        db.commit()
        return created_count

    @classmethod
    def sync_from_soc_alerts(cls, db: Session, dataset_id: int) -> int:
        """Ingest SOC InvestigationAlert records into HuntEvent records."""
        dataset = db.get(HuntDataset, dataset_id)
        if not dataset:
            return 0

        soc_alerts = list(db.scalars(select(InvestigationAlert)).all())
        created_count = 0
        for sa in soc_alerts:
            event_code = f"EVT-SOC-{sa.id:05d}"
            if db.scalar(select(HuntEvent.id).where(HuntEvent.event_id == event_code)):
                continue

            event = HuntEvent(
                event_id=event_code,
                dataset_id=dataset.id,
                event_type=HuntEventType.SOC_ALERT.value,
                timestamp=sa.created_at,
                soc_alert_id=sa.id,
                summary=f"SOC Investigation Alert: Relationship={sa.relationship}",
            )
            db.add(event)
            created_count += 1

        dataset.event_count += created_count
        db.commit()
        return created_count

    @classmethod
    def sync_from_threat_intel(cls, db: Session, dataset_id: int) -> int:
        """Ingest Threat Intel Indicator observations into HuntEvent records."""
        dataset = db.get(HuntDataset, dataset_id)
        if not dataset:
            return 0

        obs_list = list(db.scalars(select(IndicatorObservation)).all())
        created_count = 0
        for obs in obs_list:
            event_code = f"EVT-IOC-{obs.id:05d}"
            if db.scalar(select(HuntEvent.id).where(HuntEvent.event_id == event_code)):
                continue

            indicator = db.get(Indicator, obs.indicator_id)
            domain = indicator.value if indicator and indicator.indicator_type == "DOMAIN" else None
            src_ip = None
            dst_ip = indicator.value if indicator and indicator.indicator_type == "IP" else None

            if obs.context_data:
                try:
                    ctx = json.loads(obs.context_data)
                except (json.JSONDecodeError, TypeError, ValueError):
                    ctx = {}
                if isinstance(ctx, dict):
                    src_ip = ctx.get("source_ip") or src_ip
                    dst_ip = ctx.get("destination_ip") or dst_ip
                    domain = ctx.get("domain") or domain

            event = HuntEvent(
                event_id=event_code,
                dataset_id=dataset.id,
                event_type=HuntEventType.IOC_OBSERVATION.value,
                timestamp=obs.observed_at or obs.created_at,
                source_ip=src_ip,
                destination_ip=dst_ip,
                domain=domain,
                ioc_id=obs.indicator_id,
                severity=indicator.severity if indicator else "MEDIUM",
                summary=f"IOC Observed: {indicator.value if indicator else 'Indicator'} in {obs.observation_type}",
            )
            db.add(event)
            created_count += 1

        dataset.event_count += created_count
        db.commit()
        return created_count
