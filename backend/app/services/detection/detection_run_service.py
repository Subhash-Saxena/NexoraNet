"""Execution manager for Detection Runs over PCAP captures or simulation sessions."""

import json
import logging
import time
from datetime import datetime, timezone
from typing import Any

from app.models.detection import (
    AlertEvidence,
    DetectionAlert,
    DetectionRule,
    DetectionRun,
)
from app.models.enums import DetectionRunStatus
from app.models.pcap import Capture, ParsedPacket
from app.services.detection.detection_engine import DetectionEngine
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class DetectionRunService:
    """Orchestrates detection analysis runs, persists generated alerts and evidence."""

    def __init__(self) -> None:
        self.engine = DetectionEngine()

    def create_and_execute_run(
        self,
        db: Session,
        source_type: str = "PCAP",
        capture_id: int | None = None,
        simulation_scenario_id: int | None = None,
        user_id: int | None = None,
        rule_ids: list[str] | None = None,
    ) -> DetectionRun:
        """Create and execute a full detection run synchronously and deterministically."""
        # 1. Initialize run record
        run = DetectionRun(
            user_id=user_id,
            source_type=source_type,
            capture_id=capture_id,
            simulation_scenario_id=simulation_scenario_id,
            status=DetectionRunStatus.RUNNING,
            started_at=datetime.now(timezone.utc),
        )
        db.add(run)
        db.commit()
        db.refresh(run)

        start_time_monotonic = time.perf_counter()

        try:
            # 2. Fetch packets / telemetry
            packets: list[ParsedPacket] = []
            if source_type == "PCAP" and capture_id:
                capture = db.query(Capture).filter(Capture.id == capture_id).first()
                if not capture:
                    raise ValueError(f"Capture with ID {capture_id} does not exist.")
                packets = (
                    db.query(ParsedPacket)
                    .filter(ParsedPacket.capture_id == capture_id)
                    .order_by(ParsedPacket.packet_number.asc())
                    .all()
                )

            # 3. Fetch rules
            rule_query = db.query(DetectionRule).filter(DetectionRule.status == "ENABLED")
            if rule_ids:
                rule_query = rule_query.filter(DetectionRule.rule_id.in_(rule_ids))
            rules = rule_query.all()

            run.rules_evaluated = len(rules)

            # 4. Run detection engine
            matches = self.engine.evaluate(
                packets=packets,
                rules=rules,
                capture_id=capture_id,
                user_id=user_id,
                run_id=run.id,
            )

            # 5. Persist alerts and evidence
            matched_rule_ids = set()
            severity_counts: dict[str, int] = {}
            category_counts: dict[str, int] = {}

            for m in matches:
                matched_rule_ids.add(m.rule.id)
                severity_counts[m.severity] = severity_counts.get(m.severity, 0) + 1
                category_counts[m.category] = category_counts.get(m.category, 0) + 1

                alert = DetectionAlert(
                    run_id=run.id,
                    rule_id=m.rule.id,
                    capture_id=capture_id,
                    user_id=user_id,
                    title=m.title,
                    category=m.category,
                    severity=m.severity,
                    confidence=m.confidence,
                    status="NEW",
                    source_ip=m.source_ip,
                    source_port=m.source_port,
                    destination_ip=m.destination_ip,
                    destination_port=m.destination_port,
                    protocol=m.protocol,
                    first_seen_timestamp=m.first_seen,
                    last_seen_timestamp=m.last_seen,
                    packet_count=m.packet_count,
                    dedup_key=m.dedup_key,
                    explanation=m.explanation,
                    mitre_attack_id=m.rule.mitre_attack_id,
                    mitre_technique=m.rule.mitre_technique,
                    investigation_steps=json.dumps(m.investigation_steps),
                )
                db.add(alert)
                db.flush()  # populate alert.id

                for ev in m.evidence_items:
                    evidence = AlertEvidence(
                        alert_id=alert.id,
                        evidence_type=ev.get("evidence_type", "PACKET"),
                        packet_id=ev.get("packet_id"),
                        packet_number=ev.get("packet_number"),
                        timestamp=ev.get("timestamp"),
                        description=ev.get("description", "Evidence packet"),
                        evidence_data=json.dumps(ev.get("evidence_data", {})),
                    )
                    db.add(evidence)

            # 6. Finalize Run
            end_time_monotonic = time.perf_counter()
            duration_ms = int((end_time_monotonic - start_time_monotonic) * 1000)

            run.rules_matched = len(matched_rule_ids)
            run.alerts_generated = len(matches)
            run.duration_ms = duration_ms
            run.completed_at = datetime.now(timezone.utc)
            run.status = DetectionRunStatus.COMPLETED

            summary_dict = {
                "total_packets_inspected": len(packets),
                "rules_evaluated": len(rules),
                "rules_matched": len(matched_rule_ids),
                "alerts_generated": len(matches),
                "by_severity": severity_counts,
                "by_category": category_counts,
            }
            run.summary = json.dumps(summary_dict)

            db.commit()
            db.refresh(run)
            return run

        except Exception as e:
            logger.exception("Detection run %s failed", run.id)
            db.rollback()
            run.status = DetectionRunStatus.FAILED
            run.error_message = str(e)
            run.completed_at = datetime.now(timezone.utc)
            db.commit()
            return run

    def test_rule(
        self,
        db: Session,
        rule_id: str | None = None,
        conditions: dict[str, Any] | None = None,
        threshold: float | None = None,
        time_window_seconds: int | None = None,
        capture_id: int = 0,
    ) -> dict[str, Any]:
        """Test a rule against a capture without persisting alerts."""
        start_time = time.perf_counter()

        packets = (
            db.query(ParsedPacket)
            .filter(ParsedPacket.capture_id == capture_id)
            .order_by(ParsedPacket.packet_number.asc())
            .all()
        )

        rule = None
        if rule_id:
            rule = db.query(DetectionRule).filter(DetectionRule.rule_id == rule_id).first()

        if not rule:
            # Create transient mock rule
            rule = DetectionRule(
                rule_id=rule_id or "TEST-CUSTOM-001",
                name="Custom Test Rule",
                description="Transient rule for simulation test",
                category="TCP",
                severity="MEDIUM",
                confidence_default="MEDIUM",
                status="ENABLED",
                threshold=threshold or 5.0,
                time_window_seconds=time_window_seconds or 30,
                conditions=json.dumps(conditions or {}),
                explanation_template="Testing rule execution pattern.",
                investigation_guide="1. Validate test evidence.",
            )

        matches = self.engine.evaluate(packets=packets, rules=[rule], capture_id=capture_id)
        exec_ms = int((time.perf_counter() - start_time) * 1000)

        sample_matches = [
            {
                "title": m.title,
                "severity": m.severity,
                "source_ip": m.source_ip,
                "destination_ip": m.destination_ip,
                "packet_count": m.packet_count,
                "evidence_count": len(m.evidence_items),
            }
            for m in matches[:5]
        ]

        return {
            "rule_id": rule.rule_id,
            "matches_found": len(matches),
            "sample_matches": sample_matches,
            "execution_time_ms": exec_ms,
            "message": f"Successfully evaluated against {len(packets)} packets. Found {len(matches)} match(es).",
        }
