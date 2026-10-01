"""Threat Hunt session lifecycle, timeline aggregation, entity graphing, and pivoting service."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.detection import DetectionAlert
from app.models.enums import HuntStatus
from app.models.threat_hunting import (
    HuntEvent,
    ThreatHunt,
)
from app.models.threat_intel import Indicator


class ThreatHuntService:
    """Core orchestrator for threat hunting sessions and analytical graph/timeline construction."""

    @classmethod
    def generate_hunt_id(cls, db: Session) -> str:
        """Generate human-readable sequential hunt identifier e.g. HUNT-2026-0001."""
        year = datetime.now(timezone.utc).year
        prefix = f"HUNT-{year}-"
        stmt = select(ThreatHunt.hunt_id).where(ThreatHunt.hunt_id.like(f"{prefix}%"))
        existing_ids = list(db.scalars(stmt).all())
        max_seq = 0
        for hid in existing_ids:
            suffix = hid.split("-")[-1]
            if suffix.isdigit():
                max_seq = max(max_seq, int(suffix))
        return f"{prefix}{max_seq + 1:04d}"

    @classmethod
    def list_hunts(
        cls,
        db: Session,
        user_id: int | None = None,
        status: str | None = None,
        difficulty: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[ThreatHunt]:
        """List threat hunt sessions with optional filtering."""
        stmt = select(ThreatHunt)
        if user_id is not None:
            stmt = stmt.where(ThreatHunt.user_id == user_id)
        if status:
            stmt = stmt.where(ThreatHunt.status == status)
        if difficulty:
            stmt = stmt.where(ThreatHunt.difficulty == difficulty)
        stmt = stmt.order_by(ThreatHunt.created_at.desc()).offset(offset).limit(limit)
        return list(db.scalars(stmt).all())

    @classmethod
    def get_hunt(cls, db: Session, hunt_id: int) -> ThreatHunt | None:
        """Fetch hunt session by integer ID."""
        return db.get(ThreatHunt, hunt_id)

    @classmethod
    def get_hunt_by_code(cls, db: Session, hunt_code: str) -> ThreatHunt | None:
        """Fetch hunt session by unique code e.g. HUNT-2026-0001."""
        stmt = select(ThreatHunt).where(ThreatHunt.hunt_id == hunt_code)
        return db.scalar(stmt)

    @classmethod
    def create_hunt(
        cls,
        db: Session,
        user_id: int,
        title: str,
        description: str,
        objective: str,
        dataset_id: int | None = None,
        difficulty: str = "BEGINNER",
        scenario_slug: str | None = None,
        initial_pivot_type: str | None = None,
        initial_pivot_value: str | None = None,
    ) -> ThreatHunt:
        """Create and initialize a threat hunt campaign."""
        code = cls.generate_hunt_id(db)
        hunt = ThreatHunt(
            hunt_id=code,
            title=title,
            description=description,
            objective=objective,
            status=HuntStatus.READY.value,
            difficulty=difficulty,
            dataset_id=dataset_id,
            user_id=user_id,
            scenario_slug=scenario_slug,
            initial_pivot_type=initial_pivot_type,
            initial_pivot_value=initial_pivot_value,
            query_history=json.dumps([]),
        )
        db.add(hunt)
        db.commit()
        db.refresh(hunt)
        return hunt

    @classmethod
    def start_hunt(cls, db: Session, hunt_id: int) -> ThreatHunt | None:
        """Start or resume a threat hunt."""
        hunt = db.get(ThreatHunt, hunt_id)
        if not hunt:
            return None
        hunt.status = HuntStatus.RUNNING.value
        if not hunt.started_at:
            hunt.started_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(hunt)
        return hunt

    @classmethod
    def pause_hunt(cls, db: Session, hunt_id: int) -> ThreatHunt | None:
        """Pause an active threat hunt."""
        hunt = db.get(ThreatHunt, hunt_id)
        if not hunt:
            return None
        hunt.status = HuntStatus.PAUSED.value
        db.commit()
        db.refresh(hunt)
        return hunt

    @classmethod
    def complete_hunt(
        cls,
        db: Session,
        hunt_id: int,
        conclusion: str,
        conclusion_disposition: str,
    ) -> ThreatHunt | None:
        """Complete a threat hunt session with final analytical disposition."""
        hunt = db.get(ThreatHunt, hunt_id)
        if not hunt:
            return None
        hunt.status = HuntStatus.COMPLETED.value
        hunt.conclusion = conclusion
        hunt.conclusion_disposition = conclusion_disposition
        hunt.completed_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(hunt)
        return hunt

    @classmethod
    def log_query(cls, db: Session, hunt_id: int, query_repr: str) -> None:
        """Append executed query to hunt query history."""
        hunt = db.get(ThreatHunt, hunt_id)
        if not hunt:
            return
        history = []
        if hunt.query_history:
            try:
                history = json.loads(hunt.query_history)
            except (json.JSONDecodeError, TypeError, ValueError):
                history = []
        history.append({
            "query": query_repr,
            "executed_at": datetime.now(timezone.utc).isoformat(),
        })
        hunt.query_history = json.dumps(history[-50:])  # keep last 50
        db.commit()

    @classmethod
    def build_hunt_timeline(
        cls,
        db: Session,
        hunt: ThreatHunt,
        interval: str = "minute",
    ) -> dict[str, Any]:
        """Aggregate events into chronological buckets and highlight key milestones."""
        if not hunt.dataset_id:
            return {"buckets": [], "total_events": 0, "interval": interval}

        events = list(
            db.scalars(
                select(HuntEvent)
                .where(HuntEvent.dataset_id == hunt.dataset_id)
                .order_by(HuntEvent.timestamp.asc())
            ).all()
        )

        buckets = defaultdict(lambda: {"count": 0, "alerts": 0, "iocs": 0, "types": Counter()})

        for evt in events:
            ts = evt.timestamp
            if interval == "hour":
                bucket_key = ts.strftime("%Y-%m-%d %H:00")
            elif interval == "day":
                bucket_key = ts.strftime("%Y-%m-%d")
            else:
                # Default 5-minute bucket for clean aggregation
                minute_rounded = (ts.minute // 5) * 5
                bucket_key = ts.strftime(f"%Y-%m-%d %H:{minute_rounded:02d}")

            b = buckets[bucket_key]
            b["count"] += 1
            if evt.alert_id or evt.event_type in ("DETECTION_ALERT", "SOC_ALERT"):
                b["alerts"] += 1
            if evt.ioc_id or evt.event_type == "IOC_OBSERVATION":
                b["iocs"] += 1
            b["types"][evt.event_type] += 1

        timeline_buckets = [
            {
                "time_slot": k,
                "event_count": v["count"],
                "alert_count": v["alerts"],
                "ioc_count": v["iocs"],
                "breakdown": dict(v["types"]),
            }
            for k, v in sorted(buckets.items())
        ]

        # Milestone events (alerts and IOC observations)
        milestones = []
        for evt in events:
            if evt.alert_id or evt.ioc_id or evt.severity in ("HIGH", "CRITICAL"):
                milestones.append({
                    "event_id": evt.event_id,
                    "timestamp": evt.timestamp.isoformat(),
                    "event_type": evt.event_type,
                    "summary": evt.summary,
                    "severity": evt.severity or "INFO",
                    "source_ip": evt.source_ip,
                    "destination_ip": evt.destination_ip,
                })

        return {
            "total_events": len(events),
            "interval": interval,
            "buckets": timeline_buckets,
            "milestones": milestones[:25],
        }

    @classmethod
    def build_entity_graph(
        cls,
        db: Session,
        hunt: ThreatHunt,
        focus_entity: str | None = None,
        max_depth: int = 2,
        max_nodes: int = 50,
    ) -> dict[str, Any]:
        """Construct bounded entity relationship graph around hunt telemetry."""
        if not hunt.dataset_id:
            return {"nodes": [], "edges": []}

        # Gather relevant events
        stmt = select(HuntEvent).where(HuntEvent.dataset_id == hunt.dataset_id)
        if focus_entity:
            st = f"%{focus_entity}%"
            stmt = stmt.where(
                (HuntEvent.source_ip.ilike(st))
                | (HuntEvent.destination_ip.ilike(st))
                | (HuntEvent.domain.ilike(st))
            )
        stmt = stmt.limit(100)
        events = list(db.scalars(stmt).all())

        nodes: dict[str, dict[str, Any]] = {}
        edges: list[dict[str, Any]] = []
        seen_edges: set[str] = set()

        def add_node(node_id: str, label: str, node_type: str, severity: str = "INFO", extra: dict | None = None):
            if len(nodes) < max_nodes and node_id not in nodes:
                nodes[node_id] = {
                    "id": node_id,
                    "label": label,
                    "type": node_type,
                    "severity": severity,
                    "metadata": extra or {},
                }

        def add_edge(src: str, dst: str, rel: str, label: str):
            edge_key = f"{src}->{dst}:{rel}"
            if edge_key not in seen_edges and src in nodes and dst in nodes:
                seen_edges.add(edge_key)
                edges.append({
                    "source": src,
                    "target": dst,
                    "relationship": rel,
                    "label": label,
                })

        for evt in events:
            # Source IP node
            if evt.source_ip:
                s_id = f"ip:{evt.source_ip}"
                add_node(s_id, evt.source_ip, "IP")

            # Destination IP node
            if evt.destination_ip:
                d_id = f"ip:{evt.destination_ip}"
                d_sev = evt.severity if evt.severity in ("HIGH", "CRITICAL") else "INFO"
                add_node(d_id, evt.destination_ip, "IP", severity=d_sev)

            # Domain node
            if evt.domain:
                dom_id = f"domain:{evt.domain}"
                add_node(dom_id, evt.domain, "DOMAIN", severity="SUSPICIOUS" if "bad" in evt.domain or "c2" in evt.domain else "INFO")

            # Connect Source IP -> Destination IP
            if evt.source_ip and evt.destination_ip:
                s_id = f"ip:{evt.source_ip}"
                d_id = f"ip:{evt.destination_ip}"
                proto = evt.protocol or "IP"
                port = f":{evt.destination_port}" if evt.destination_port else ""
                add_edge(s_id, d_id, "CONTACTED", f"{proto}{port}")

            # Connect Destination IP -> Domain
            if evt.destination_ip and evt.domain:
                d_id = f"ip:{evt.destination_ip}"
                dom_id = f"domain:{evt.domain}"
                add_edge(dom_id, d_id, "RESOLVES_TO", "DNS")

            # Connect Alert
            if evt.alert_id:
                al_id = f"alert:{evt.alert_id}"
                add_node(al_id, f"Alert #{evt.alert_id}", "ALERT", severity=evt.severity or "HIGH")
                if evt.source_ip:
                    add_edge(f"ip:{evt.source_ip}", al_id, "TRIGGERED", "Source")
                if evt.destination_ip:
                    add_edge(al_id, f"ip:{evt.destination_ip}", "TARGETED", "Target")

            # Connect IOC
            if evt.ioc_id:
                ioc_id = f"ioc:{evt.ioc_id}"
                add_node(ioc_id, f"IOC #{evt.ioc_id}", "IOC", severity="CRITICAL")
                if evt.domain:
                    add_edge(f"domain:{evt.domain}", ioc_id, "MATCHES_IOC", "Domain")
                elif evt.destination_ip:
                    add_edge(f"ip:{evt.destination_ip}", ioc_id, "MATCHES_IOC", "IP")

            if len(nodes) >= max_nodes:
                break

        return {
            "nodes": list(nodes.values()),
            "edges": edges,
            "focus": focus_entity,
        }

    @classmethod
    def pivot_entity(
        cls,
        db: Session,
        hunt: ThreatHunt,
        entity_type: str,
        entity_value: str,
    ) -> dict[str, Any]:
        """Find all telemetry, alerts, and threat intel correlated with an entity."""
        val = entity_value.strip()
        events_stmt = select(HuntEvent)
        if hunt.dataset_id:
            events_stmt = events_stmt.where(HuntEvent.dataset_id == hunt.dataset_id)

        if entity_type.upper() == "IP":
            events_stmt = events_stmt.where(
                (HuntEvent.source_ip == val) | (HuntEvent.destination_ip == val)
            )
        elif entity_type.upper() == "DOMAIN":
            events_stmt = events_stmt.where(HuntEvent.domain.ilike(f"%{val}%"))
        elif entity_type.upper() == "PORT":
            try:
                p = int(val)
                events_stmt = events_stmt.where(
                    (HuntEvent.source_port == p) | (HuntEvent.destination_port == p)
                )
            except ValueError:
                pass
        else:
            events_stmt = events_stmt.where(
                (HuntEvent.summary.ilike(f"%{val}%")) | (HuntEvent.action.ilike(f"%{val}%"))
            )

        events = list(db.scalars(events_stmt.limit(50)).all())

        # Correlated indicators
        ioc_stmt = select(Indicator).where(Indicator.value.ilike(f"%{val}%"))
        matched_iocs = list(db.scalars(ioc_stmt).all())

        # Correlated alerts
        alert_stmt = select(DetectionAlert).where(
            (DetectionAlert.source_ip == val) | (DetectionAlert.destination_ip == val)
        )
        matched_alerts = list(db.scalars(alert_stmt).all())

        # Suggested investigation questions based on pivot type
        questions = []
        if entity_type.upper() == "IP":
            questions = [
                f"Is {val} an internal host or external server?",
                f"What protocol and ports does {val} communicate on most frequently?",
                f"Did {val} resolve through DNS or was it contacted directly by raw IP?",
                f"Are there multiple endpoints in the environment talking to {val}?",
            ]
        elif entity_type.upper() == "DOMAIN":
            questions = [
                f"When was {val} first queried in the environment?",
                f"What IP addresses does {val} resolve to?",
                "Are DNS request frequencies periodic (beaconing) or sporadic?",
                f"Does {val} match any known threat intelligence indicators?",
            ]
        else:
            questions = [
                f"How prevalent is {val} across the dataset?",
                "What user activity or process initiated this connection?",
            ]

        return {
            "entity_type": entity_type,
            "entity_value": entity_value,
            "matched_events_count": len(events),
            "matched_events": [
                {
                    "event_id": e.event_id,
                    "timestamp": e.timestamp.isoformat(),
                    "event_type": e.event_type,
                    "protocol": e.protocol,
                    "source_ip": e.source_ip,
                    "destination_ip": e.destination_ip,
                    "summary": e.summary,
                }
                for e in events
            ],
            "matched_iocs": [
                {
                    "id": i.id,
                    "indicator_id": i.indicator_id,
                    "type": i.indicator_type,
                    "value": i.value,
                    "severity": i.severity,
                    "classification": i.classification,
                }
                for i in matched_iocs
            ],
            "matched_alerts": [
                {
                    "id": a.id,
                    "alert_id": a.alert_id,
                    "title": a.title,
                    "severity": a.severity,
                    "created_at": a.created_at.isoformat(),
                }
                for a in matched_alerts
            ],
            "suggested_questions": questions,
        }
