"""SIEM Correlation Engine for NexoraNet Step 15.

Evaluates deterministic, explainable correlation rules across normalized security
events to synthesize high-confidence CorrelationAlerts without executing user code.
"""

import json
import uuid
from datetime import datetime, timezone
from typing import Any, ClassVar

from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session

from app.models.enums import (
    CorrelationAlertStatus,
    LogCorrelationRuleStatus,
    SecurityEventCategory,
    SecurityEventSeverity,
)
from app.models.siem import (
    CorrelationAlert,
    LogCorrelationRule,
    SecurityEvent,
)


class SiemCorrelationEngine:
    """Executes structured correlation rules and synthesizes correlation alerts."""

    # Default educational rules for seeding
    DEFAULT_RULES: ClassVar[list[dict[str, Any]]] = [
        {
            "stable_id": "RULE-AUTH-001",
            "name": "Repeated Authentication Failures (Brute Force Detection)",
            "description": "Detects multiple consecutive login failures from the same source IP within a short time window.",
            "category": SecurityEventCategory.AUTHENTICATION.value,
            "severity": SecurityEventSeverity.MEDIUM.value,
            "confidence": "HIGH",
            "time_window_seconds": 300,
            "logic": json.dumps({
                "type": "THRESHOLD",
                "filter": {"action": "LOGIN_FAILURE"},
                "group_by": "source_ip",
                "threshold": 3,
            }),
            "explanation": "Three or more login failures from the same source IP within 5 minutes indicates possible password guessing or brute-force activity.",
        },
        {
            "stable_id": "RULE-AUTH-002",
            "name": "Authentication Failure Followed by Successful Login",
            "description": "Detects multiple failed logins from an IP followed by a successful login, suggesting successful compromise or forgotten credentials.",
            "category": SecurityEventCategory.AUTHENTICATION.value,
            "severity": SecurityEventSeverity.HIGH.value,
            "confidence": "HIGH",
            "time_window_seconds": 300,
            "logic": json.dumps({
                "type": "SEQUENCE",
                "step1": {"action": "LOGIN_FAILURE", "threshold": 2},
                "step2": {"action": "LOGIN"},
                "group_by": "source_ip",
            }),
            "explanation": "Multiple login failures followed immediately by a successful authentication from the same address may indicate an attacker successfully guessed a credential.",
        },
        {
            "stable_id": "RULE-AUTH-003",
            "name": "Multiple Account Lockouts Observed",
            "description": "Detects repeated account lockout events across systems indicating widespread credential exhaustion.",
            "category": SecurityEventCategory.ACCOUNT.value,
            "severity": SecurityEventSeverity.HIGH.value,
            "confidence": "HIGH",
            "time_window_seconds": 600,
            "logic": json.dumps({
                "type": "THRESHOLD",
                "filter": {"action": "ACCOUNT_DISABLED"},
                "group_by": "host",
                "threshold": 2,
            }),
            "explanation": "Multiple account lockouts in short succession indicates automated password spray or policy-triggered containment.",
        },
        {
            "stable_id": "RULE-NET-001",
            "name": "Repeated Firewall Drops / Port Sweep",
            "description": "Detects high-frequency blocked connection attempts from a single source address.",
            "category": SecurityEventCategory.FIREWALL.value,
            "severity": SecurityEventSeverity.LOW.value,
            "confidence": "HIGH",
            "time_window_seconds": 300,
            "logic": json.dumps({
                "type": "THRESHOLD",
                "filter": {"action": "CONNECTION_BLOCKED"},
                "group_by": "source_ip",
                "threshold": 5,
            }),
            "explanation": "Repeated firewall blocks from a single IP indicate port scanning, unauthorized service access attempts, or misconfigured network appliances.",
        },
        {
            "stable_id": "RULE-NET-002",
            "name": "DNS Anomaly / NXDOMAIN Burst",
            "description": "Detects multiple DNS failures or NXDOMAIN resolutions suggesting DGA or domain recon.",
            "category": SecurityEventCategory.DNS.value,
            "severity": SecurityEventSeverity.MEDIUM.value,
            "confidence": "MEDIUM",
            "time_window_seconds": 300,
            "logic": json.dumps({
                "type": "THRESHOLD",
                "filter": {"event_category": "DNS", "status": "NXDOMAIN"},
                "group_by": "source_ip",
                "threshold": 3,
            }),
            "explanation": "A burst of NXDOMAIN DNS queries often signals domain generation algorithms (DGA) or scanning for non-existent staging domains.",
        },
        {
            "stable_id": "RULE-NET-003",
            "name": "DNS Resolution Followed by Outbound Connection",
            "description": "Correlates a DNS query with a subsequent outbound connection to the resolved destination host.",
            "category": SecurityEventCategory.NETWORK.value,
            "severity": SecurityEventSeverity.MEDIUM.value,
            "confidence": "HIGH",
            "time_window_seconds": 180,
            "logic": json.dumps({
                "type": "SEQUENCE",
                "step1": {"event_category": "DNS"},
                "step2": {"event_category": "NETWORK", "action": "CONNECTION"},
                "group_by": "source_ip",
            }),
            "explanation": "A host resolved an external domain and immediately initiated an outbound connection, establishing end-to-end communication trace.",
        },
        {
            "stable_id": "RULE-WEB-001",
            "name": "Repeated HTTP Error Responses (Web Probing)",
            "description": "Detects anomalous bursts of HTTP 4xx or 5xx status codes against a web application.",
            "category": SecurityEventCategory.WEB.value,
            "severity": SecurityEventSeverity.LOW.value,
            "confidence": "HIGH",
            "time_window_seconds": 300,
            "logic": json.dumps({
                "type": "THRESHOLD",
                "filter": {"event_category": "WEB", "status": "FAILURE"},
                "group_by": "source_ip",
                "threshold": 5,
            }),
            "explanation": "High volumes of HTTP client or server errors from a single IP point to web content enumeration, directory fuzzing, or vulnerability probing.",
        },
        {
            "stable_id": "RULE-HOST-001",
            "name": "Suspicious Process Execution & Script Execution",
            "description": "Detects anomalous process spawning or PowerShell encoded command execution.",
            "category": SecurityEventCategory.PROCESS.value,
            "severity": SecurityEventSeverity.HIGH.value,
            "confidence": "HIGH",
            "time_window_seconds": 300,
            "logic": json.dumps({
                "type": "SUSPICIOUS_PROCESS",
                "process_names": ["powershell.exe", "cmd.exe", "whoami.exe", "vssadmin.exe", "certutil.exe"],
            }),
            "explanation": "Command line execution of sensitive administrative or reconnaissance binaries indicates possible hands-on-keyboard adversary activity.",
        },
        {
            "stable_id": "RULE-CORR-001",
            "name": "Multi-Source Host Threat Activity Burst",
            "description": "Detects co-occurring security events across both network and authentication boundaries on a single host.",
            "category": SecurityEventCategory.SECURITY.value,
            "severity": SecurityEventSeverity.CRITICAL.value,
            "confidence": "HIGH",
            "time_window_seconds": 300,
            "logic": json.dumps({
                "type": "MULTI_CATEGORY",
                "categories": ["AUTHENTICATION", "NETWORK", "FIREWALL"],
                "group_by": "source_ip",
            }),
            "explanation": "An endpoint exhibiting authentication anomalies alongside firewall drops represents a multi-vector security incident.",
        },
    ]

    @classmethod
    def seed_default_rules(cls, db: Session) -> list[LogCorrelationRule]:
        """Ensure standard educational correlation rules exist in database."""
        created_rules = []
        for r_def in cls.DEFAULT_RULES:
            existing = db.execute(
                select(LogCorrelationRule).where(LogCorrelationRule.stable_id == r_def["stable_id"])
            ).scalar_one_or_none()
            if not existing:
                rule = LogCorrelationRule(
                    stable_id=r_def["stable_id"],
                    name=r_def["name"],
                    description=r_def["description"],
                    category=r_def["category"],
                    severity=r_def["severity"],
                    confidence=r_def["confidence"],
                    status=LogCorrelationRuleStatus.ENABLED.value,
                    version="1.0.0",
                    logic=r_def["logic"],
                    time_window_seconds=r_def["time_window_seconds"],
                    explanation=r_def["explanation"],
                )
                db.add(rule)
                created_rules.append(rule)
        db.commit()
        return created_rules

    @classmethod
    def run_correlation(
        cls, db: Session, dataset_id: int | None = None
    ) -> list[CorrelationAlert]:
        """Run all active correlation rules against target dataset(s) and create alerts."""
        rules = db.execute(
            select(LogCorrelationRule).where(
                LogCorrelationRule.status == LogCorrelationRuleStatus.ENABLED.value
            )
        ).scalars().all()

        generated_alerts: list[CorrelationAlert] = []
        for rule in rules:
            alerts = cls._evaluate_rule(db, rule, dataset_id=dataset_id)
            generated_alerts.extend(alerts)

        return generated_alerts

    @classmethod
    def _evaluate_rule(
        cls, db: Session, rule: LogCorrelationRule, dataset_id: int | None = None
    ) -> list[CorrelationAlert]:
        """Evaluate a single rule logic specification."""
        try:
            logic_data = json.loads(rule.logic)
        except (json.JSONDecodeError, TypeError):
            return []

        rule_type = logic_data.get("type", "THRESHOLD")
        matched_alerts = []

        if rule_type == "THRESHOLD":
            matched_alerts = cls._eval_threshold_rule(db, rule, logic_data, dataset_id)
        elif rule_type == "SEQUENCE":
            matched_alerts = cls._eval_sequence_rule(db, rule, logic_data, dataset_id)
        elif rule_type == "SUSPICIOUS_PROCESS":
            matched_alerts = cls._eval_process_rule(db, rule, logic_data, dataset_id)
        elif rule_type == "MULTI_CATEGORY":
            matched_alerts = cls._eval_multi_category_rule(db, rule, logic_data, dataset_id)

        return matched_alerts

    @classmethod
    def _eval_threshold_rule(
        cls,
        db: Session,
        rule: LogCorrelationRule,
        logic: dict[str, Any],
        dataset_id: int | None,
    ) -> list[CorrelationAlert]:
        """Evaluate threshold rule (e.g. >= N events with same group_by key)."""
        filt = logic.get("filter", {})
        group_key = logic.get("group_by", "source_ip")
        threshold = logic.get("threshold", 3)

        col_map = {
            "source_ip": SecurityEvent.source_ip,
            "username": SecurityEvent.username,
            "host": SecurityEvent.host,
            "domain": SecurityEvent.domain,
        }
        group_col = col_map.get(group_key, SecurityEvent.source_ip)

        stmt = (
            select(group_col, SecurityEvent.dataset_id, func.count(SecurityEvent.id))
            .where(group_col.isnot(None))
            .where(group_col != "")
        )
        if dataset_id:
            stmt = stmt.where(SecurityEvent.dataset_id == dataset_id)

        # Apply event filter
        if "action" in filt:
            stmt = stmt.where(SecurityEvent.action == filt["action"])
        if "event_category" in filt:
            stmt = stmt.where(SecurityEvent.event_category == filt["event_category"])
        if "status" in filt:
            stmt = stmt.where(SecurityEvent.status == filt["status"])

        stmt = stmt.group_by(group_col, SecurityEvent.dataset_id).having(
            func.count(SecurityEvent.id) >= threshold
        )

        results = db.execute(stmt).all()
        alerts = []

        for entity_val, ds_id, count in results:
            # Check if alert already exists for this rule and entity to prevent duplicate spam
            existing = db.execute(
                select(CorrelationAlert).where(
                    and_(
                        CorrelationAlert.rule_id == rule.id,
                        CorrelationAlert.dataset_id == ds_id,
                        CorrelationAlert.source_context.ilike(f"%{entity_val}%"),
                    )
                )
            ).first()
            if existing:
                continue

            # Fetch matching event IDs
            ev_stmt = (
                select(SecurityEvent.id, SecurityEvent.event_id, SecurityEvent.timestamp)
                .where(
                    and_(
                        SecurityEvent.dataset_id == ds_id,
                        group_col == entity_val,
                    )
                )
                .order_by(SecurityEvent.timestamp.desc())
                .limit(count)
            )
            ev_rows = db.execute(ev_stmt).all()
            matched_ids = [row[1] for row in ev_rows]
            last_ts = ev_rows[0][2] if ev_rows else datetime.now(timezone.utc)

            alert_code = f"CORR-{uuid.uuid4().hex[:10].upper()}"
            alert = CorrelationAlert(
                alert_id=alert_code,
                rule_id=rule.id,
                dataset_id=ds_id,
                timestamp=last_ts,
                title=f"{rule.name} ({group_key}: {entity_val})",
                category=rule.category,
                severity=rule.severity,
                confidence=rule.confidence,
                status=CorrelationAlertStatus.NEW.value,
                event_count=count,
                source_context=json.dumps({group_key: entity_val}),
                evidence_summary=f"Detected {count} matching events for {group_key} '{entity_val}' exceeding threshold of {threshold}.",
                matched_event_ids=json.dumps(matched_ids),
            )
            db.add(alert)
            alerts.append(alert)

        db.commit()
        return alerts

    @classmethod
    def _eval_sequence_rule(
        cls,
        db: Session,
        rule: LogCorrelationRule,
        logic: dict[str, Any],
        dataset_id: int | None,
    ) -> list[CorrelationAlert]:
        """Evaluate sequence rule (e.g. step 1 failures followed by step 2 success)."""
        step1 = logic.get("step1", {})
        step2 = logic.get("step2", {})
        group_key = logic.get("group_by", "source_ip")

        # Find candidates matching step1
        s1_stmt = (
            select(SecurityEvent.source_ip, SecurityEvent.dataset_id, func.count(SecurityEvent.id))
            .where(SecurityEvent.source_ip.isnot(None))
            .where(SecurityEvent.source_ip != "")
        )
        if dataset_id:
            s1_stmt = s1_stmt.where(SecurityEvent.dataset_id == dataset_id)
        if "action" in step1:
            s1_stmt = s1_stmt.where(SecurityEvent.action == step1["action"])
        if "event_category" in step1:
            s1_stmt = s1_stmt.where(SecurityEvent.event_category == step1["event_category"])

        s1_stmt = s1_stmt.group_by(SecurityEvent.source_ip, SecurityEvent.dataset_id).having(
            func.count(SecurityEvent.id) >= step1.get("threshold", 1)
        )
        candidates = db.execute(s1_stmt).all()

        alerts = []
        for src_ip, ds_id, s1_count in candidates:
            # Check if same source has step2 event
            s2_stmt = select(SecurityEvent).where(
                and_(
                    SecurityEvent.dataset_id == ds_id,
                    SecurityEvent.source_ip == src_ip,
                )
            )
            if "action" in step2:
                s2_stmt = s2_stmt.where(SecurityEvent.action == step2["action"])
            if "event_category" in step2:
                s2_stmt = s2_stmt.where(SecurityEvent.event_category == step2["event_category"])

            step2_events = db.execute(s2_stmt.limit(5)).scalars().all()
            if step2_events:
                # Sequence match!
                existing = db.execute(
                    select(CorrelationAlert).where(
                        and_(
                            CorrelationAlert.rule_id == rule.id,
                            CorrelationAlert.dataset_id == ds_id,
                            CorrelationAlert.source_context.ilike(f"%{src_ip}%"),
                        )
                    )
                ).first()
                if not existing:
                    alert_code = f"CORR-{uuid.uuid4().hex[:10].upper()}"
                    alert = CorrelationAlert(
                        alert_id=alert_code,
                        rule_id=rule.id,
                        dataset_id=ds_id,
                        timestamp=step2_events[0].timestamp,
                        title=f"{rule.name} ({group_key}: {src_ip})",
                        category=rule.category,
                        severity=rule.severity,
                        confidence=rule.confidence,
                        status=CorrelationAlertStatus.NEW.value,
                        event_count=s1_count + len(step2_events),
                        source_context=json.dumps({"source_ip": src_ip}),
                        evidence_summary=f"Observed {s1_count} preliminary events followed by {len(step2_events)} subsequent events from {src_ip}.",
                        matched_event_ids=json.dumps([e.event_id for e in step2_events]),
                    )
                    db.add(alert)
                    alerts.append(alert)

        db.commit()
        return alerts

    @classmethod
    def _eval_process_rule(
        cls,
        db: Session,
        rule: LogCorrelationRule,
        logic: dict[str, Any],
        dataset_id: int | None,
    ) -> list[CorrelationAlert]:
        """Detect suspicious processes matching list."""
        proc_names = logic.get("process_names", [])
        if not proc_names:
            return []

        stmt = select(SecurityEvent).where(
            SecurityEvent.event_category == SecurityEventCategory.PROCESS.value
        )
        if dataset_id:
            stmt = stmt.where(SecurityEvent.dataset_id == dataset_id)

        # Match names
        name_clauses = [SecurityEvent.process_name.ilike(f"%{p}%") for p in proc_names]
        stmt = stmt.where(or_(*name_clauses)).limit(20)

        events = db.execute(stmt).scalars().all()
        alerts = []

        by_host: dict[str, list[SecurityEvent]] = {}
        for ev in events:
            h = ev.host or ev.source_ip or "unknown_host"
            by_host.setdefault(h, []).append(ev)

        for host, ev_list in by_host.items():
            ds_id = ev_list[0].dataset_id
            existing = db.execute(
                select(CorrelationAlert).where(
                    and_(
                        CorrelationAlert.rule_id == rule.id,
                        CorrelationAlert.dataset_id == ds_id,
                        CorrelationAlert.source_context.ilike(f"%{host}%"),
                    )
                )
            ).first()
            if not existing:
                alert_code = f"CORR-{uuid.uuid4().hex[:10].upper()}"
                alert = CorrelationAlert(
                    alert_id=alert_code,
                    rule_id=rule.id,
                    dataset_id=ds_id,
                    timestamp=ev_list[0].timestamp,
                    title=f"{rule.name} (Host: {host})",
                    category=rule.category,
                    severity=rule.severity,
                    confidence=rule.confidence,
                    status=CorrelationAlertStatus.NEW.value,
                    event_count=len(ev_list),
                    source_context=json.dumps({"host": host, "process": ev_list[0].process_name}),
                    evidence_summary=f"Detected {len(ev_list)} suspicious process executions on {host} ({ev_list[0].process_name}).",
                    matched_event_ids=json.dumps([e.event_id for e in ev_list]),
                )
                db.add(alert)
                alerts.append(alert)

        db.commit()
        return alerts

    @classmethod
    def _eval_multi_category_rule(
        cls,
        db: Session,
        rule: LogCorrelationRule,
        logic: dict[str, Any],
        dataset_id: int | None,
    ) -> list[CorrelationAlert]:
        """Correlate events across multiple categories from same source."""
        cats = logic.get("categories", ["AUTHENTICATION", "NETWORK"])
        stmt = (
            select(
                SecurityEvent.source_ip,
                SecurityEvent.dataset_id,
                func.count(func.distinct(SecurityEvent.event_category)),
            )
            .where(SecurityEvent.source_ip.isnot(None))
            .where(SecurityEvent.source_ip != "")
            .where(SecurityEvent.event_category.in_(cats))
        )
        if dataset_id:
            stmt = stmt.where(SecurityEvent.dataset_id == dataset_id)

        stmt = stmt.group_by(SecurityEvent.source_ip, SecurityEvent.dataset_id).having(
            func.count(func.distinct(SecurityEvent.event_category)) >= len(cats)
        )

        matches = db.execute(stmt).all()
        alerts = []

        for src_ip, ds_id, _ in matches:
            existing = db.execute(
                select(CorrelationAlert).where(
                    and_(
                        CorrelationAlert.rule_id == rule.id,
                        CorrelationAlert.dataset_id == ds_id,
                        CorrelationAlert.source_context.ilike(f"%{src_ip}%"),
                    )
                )
            ).first()
            if not existing:
                ev_stmt = (
                    select(SecurityEvent)
                    .where(
                        and_(
                            SecurityEvent.dataset_id == ds_id,
                            SecurityEvent.source_ip == src_ip,
                            SecurityEvent.event_category.in_(cats),
                        )
                    )
                    .order_by(SecurityEvent.timestamp.desc())
                    .limit(10)
                )
                sample_evs = db.execute(ev_stmt).scalars().all()

                alert_code = f"CORR-{uuid.uuid4().hex[:10].upper()}"
                alert = CorrelationAlert(
                    alert_id=alert_code,
                    rule_id=rule.id,
                    dataset_id=ds_id,
                    timestamp=sample_evs[0].timestamp if sample_evs else datetime.now(timezone.utc),
                    title=f"{rule.name} (Source: {src_ip})",
                    category=rule.category,
                    severity=rule.severity,
                    confidence=rule.confidence,
                    status=CorrelationAlertStatus.NEW.value,
                    event_count=len(sample_evs),
                    source_context=json.dumps({"source_ip": src_ip}),
                    evidence_summary=f"Detected coordinated events across {len(cats)} categories ({', '.join(cats)}) from source {src_ip}.",
                    matched_event_ids=json.dumps([e.event_id for e in sample_evs]),
                )
                db.add(alert)
                alerts.append(alert)

        db.commit()
        return alerts
