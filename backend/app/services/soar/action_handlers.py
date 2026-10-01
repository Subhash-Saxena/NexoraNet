"""Strictly Allowlisted Action Handlers for Educational SOAR Engine.

All actions operate exclusively on synthetic educational records.
Zero shell commands, zero network modification, zero external communication.
Every response action is flagged simulation_only = True.
"""

import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Any

from app.models.detection import DetectionAlert, DetectionRule
from app.models.endpoint_security import EndpointEvent, EndpointHost
from app.models.incident import (
    Incident,
    IncidentEvidence,
    IncidentNote,
    IncidentTimelineEvent,
    ResponseAction,
)
from app.models.playbook import IncidentPlaybook
from app.models.siem import SecurityEvent
from app.models.soc import Case, CaseAlert, SocNotification
from app.models.threat_intel import Indicator
from sqlalchemy.orm import Session


class ActionHandlerRegistry:
    """Dispatches allowlisted automation actions with educational validation."""

    @classmethod
    def execute(
        cls,
        db: Session,
        action_type: str,
        parameters: dict[str, Any],
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """Dispatch action to appropriate handler function."""
        handler = getattr(cls, f"_handle_{action_type.lower()}", None)
        if not handler:
            raise ValueError(f"Action '{action_type}' is not recognized in strict allowlist.")

        return handler(db, parameters, context)

    # -------------------------------------------------------------------------
    # 1. Enrichment Actions
    # -------------------------------------------------------------------------
    @classmethod
    def _handle_enrich_alert(
        cls, db: Session, parameters: dict[str, Any], context: dict[str, Any]
    ) -> dict[str, Any]:
        alert_id = parameters.get("alert_id") or context.get("alert_id") or context.get("source_id")
        enrichment_data: dict[str, Any] = {
            "enriched_at": datetime.now(timezone.utc).isoformat(),
            "synthetic_fidelity": "HIGH",
            "threat_score": 75,
            "target_assets": ["NN-DEV-001", "NN-DC-01"],
            "network_segment": "VLAN-10-DEV",
        }

        # Query local DetectionAlert if available
        if alert_id:
            alert = (
                db.query(DetectionAlert)
                .filter(DetectionAlert.alert_id == str(alert_id))
                .first()
            )
            if alert:
                enrichment_data.update({
                    "rule_name": alert.title,
                    "severity": alert.severity,
                    "src_ip": alert.source_ip,
                    "dst_ip": alert.destination_ip,
                    "protocol": alert.protocol,
                })

        context["alert_enrichment"] = enrichment_data
        return {
            "success": True,
            "input_summary": f"Enriching alert target: {alert_id}",
            "output_summary": f"Alert enriched with asset context: {enrichment_data.get('target_assets')}",
            "context_updates": {"alert_enrichment": enrichment_data},
        }

    @classmethod
    def _handle_enrich_ioc(
        cls, db: Session, parameters: dict[str, Any], context: dict[str, Any]
    ) -> dict[str, Any]:
        ioc_value = parameters.get("ioc_value") or context.get("ioc_value") or context.get("source_id")
        ind = db.query(Indicator).filter(Indicator.value == str(ioc_value)).first()

        ioc_data = {
            "indicator": ioc_value,
            "reputation": ind.reputation_score if ind else 80,
            "confidence": ind.confidence if ind else "HIGH",
            "is_malicious": True,
            "threat_actor": ind.threat_actor or "APT-Simulated-Fox" if ind else "Simulated-Adversary",
            "sightings_count": ind.sightings_count if ind else 5,
        }
        context["ioc_enrichment"] = ioc_data
        return {
            "success": True,
            "input_summary": f"Enriching IOC: {ioc_value}",
            "output_summary": f"Indicator matched local intel: Actor={ioc_data['threat_actor']}, Score={ioc_data['reputation']}",
            "context_updates": {"ioc_enrichment": ioc_data},
        }

    @classmethod
    def _handle_enrich_host(
        cls, db: Session, parameters: dict[str, Any], context: dict[str, Any]
    ) -> dict[str, Any]:
        hostname = parameters.get("hostname") or context.get("hostname") or "NN-DEV-001"
        host = db.query(EndpointHost).filter(EndpointHost.hostname == str(hostname)).first()

        host_info = {
            "hostname": hostname,
            "os": host.platform if host else "WINDOWS",
            "risk_level": host.risk_level if host else "CRITICAL",
            "ip_address": host.ip_address if host else "192.0.2.22",
            "environment": host.environment if host else "WORKSTATION",
        }
        context["host_enrichment"] = host_info
        return {
            "success": True,
            "input_summary": f"Enriching host: {hostname}",
            "output_summary": f"Host inventory validated: {host_info['os']} ({host_info['risk_level']})",
            "context_updates": {"host_enrichment": host_info},
        }

    @classmethod
    def _handle_enrich_user(
        cls, db: Session, parameters: dict[str, Any], context: dict[str, Any]
    ) -> dict[str, Any]:
        username = parameters.get("username") or context.get("username") or "dev.alice"
        user_info = {
            "username": username,
            "department": "Engineering / DevOps",
            "privileged_account": True,
            "recent_failed_logins": 12,
            "last_login_location": "Internal Office (192.0.2.100)",
            "risk_status": "SUSPICIOUS_BRUTE_FORCE",
        }
        context["user_enrichment"] = user_info
        return {
            "success": True,
            "input_summary": f"Enriching user: {username}",
            "output_summary": f"User status: {user_info['risk_status']} ({user_info['recent_failed_logins']} failed attempts)",
            "context_updates": {"user_enrichment": user_info},
        }

    @classmethod
    def _handle_enrich_detection(
        cls, db: Session, parameters: dict[str, Any], context: dict[str, Any]
    ) -> dict[str, Any]:
        rule_name = parameters.get("rule_name") or context.get("rule_name") or "Sysmon Process Injection"
        rule = db.query(DetectionRule).filter(DetectionRule.name == str(rule_name)).first()

        det_info = {
            "rule_name": rule_name,
            "category": rule.category if rule else "HOST_ATTACK",
            "severity": rule.severity if rule else "HIGH",
            "mitre_technique": "T1059.001",
        }
        context["detection_enrichment"] = det_info
        return {
            "success": True,
            "input_summary": f"Enriching detection rule: {rule_name}",
            "output_summary": f"Rule verified: {det_info['category']} ({det_info['mitre_technique']})",
            "context_updates": {"detection_enrichment": det_info},
        }

    # -------------------------------------------------------------------------
    # 2. Investigation Actions
    # -------------------------------------------------------------------------
    @classmethod
    def _handle_collect_alert_evidence(
        cls, db: Session, parameters: dict[str, Any], context: dict[str, Any]
    ) -> dict[str, Any]:
        alert_id = parameters.get("alert_id") or context.get("alert_id") or "ALT-101"
        payload_data = {
            "evidence_type": "ALERT",
            "source": f"DETECTION_{alert_id}",
            "collected_by": "SOAR_AUTOMATION",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        raw_bytes = json.dumps(payload_data, sort_keys=True).encode("utf-8")
        sha256 = hashlib.sha256(raw_bytes).hexdigest()

        evidence_info = {
            "evidence_id": f"EVD-SOAR-{uuid.uuid4().hex[:8].upper()}",
            "title": f"Automated Ingested Alert Evidence: {alert_id}",
            "sha256": sha256,
            "relevance": "SUPPORTING",
        }
        ev_list = context.setdefault("collected_evidence", [])
        ev_list.append(evidence_info)

        return {
            "success": True,
            "input_summary": f"Packaging alert evidence: {alert_id}",
            "output_summary": f"Evidence generated with SHA-256: {sha256[:16]}...",
            "artifacts": {"evidence_id": evidence_info["evidence_id"]},
        }

    @classmethod
    def _handle_collect_related_alerts(
        cls, db: Session, parameters: dict[str, Any], context: dict[str, Any]
    ) -> dict[str, Any]:
        related = [
            {"alert_id": "ALT-2026-0091", "title": "Suspicious PowerShell Invocations", "severity": "HIGH"},
            {"alert_id": "ALT-2026-0092", "title": "Outbound Non-Standard Port Traffic", "severity": "MEDIUM"},
        ]
        context["related_alerts"] = related
        return {
            "success": True,
            "input_summary": "Querying related alerts in 1-hour temporal window",
            "output_summary": f"Found {len(related)} co-occurring alerts on target hosts",
            "context_updates": {"related_alerts_count": len(related)},
        }

    @classmethod
    def _handle_collect_related_iocs(
        cls, db: Session, parameters: dict[str, Any], context: dict[str, Any]
    ) -> dict[str, Any]:
        iocs = [
            {"type": "IP", "value": "198.51.100.45", "confidence": "HIGH"},
            {"type": "DOMAIN", "value": "c2-beacon-sim.test", "confidence": "HIGH"},
        ]
        context["related_iocs"] = iocs
        return {
            "success": True,
            "input_summary": "Searching local threat intelligence database",
            "output_summary": f"Extracted {len(iocs)} correlating indicators of compromise",
            "context_updates": {"related_iocs_count": len(iocs)},
        }

    @classmethod
    def _handle_collect_related_endpoint_events(
        cls, db: Session, parameters: dict[str, Any], context: dict[str, Any]
    ) -> dict[str, Any]:
        events = db.query(EndpointEvent).limit(5).all()
        count = len(events) if events else 3
        return {
            "success": True,
            "input_summary": "Retrieving endpoint process and logon telemetry",
            "output_summary": f"Aggregated {count} host events into investigation corpus",
            "context_updates": {"endpoint_events_count": count},
        }

    @classmethod
    def _handle_collect_related_siem_events(
        cls, db: Session, parameters: dict[str, Any], context: dict[str, Any]
    ) -> dict[str, Any]:
        events = db.query(SecurityEvent).limit(5).all()
        count = len(events) if events else 4
        return {
            "success": True,
            "input_summary": "Correlating SIEM log repository events",
            "output_summary": f"Collected {count} correlating SIEM security log entries",
            "context_updates": {"siem_events_count": count},
        }

    @classmethod
    def _handle_build_timeline(
        cls, db: Session, parameters: dict[str, Any], context: dict[str, Any]
    ) -> dict[str, Any]:
        return {
            "success": True,
            "input_summary": "Synthesizing multi-vector timeline",
            "output_summary": "Constructed 4-stage chronological event sequence with milestones",
            "context_updates": {"timeline_built": True},
        }

    @classmethod
    def _handle_calculate_alert_context(
        cls, db: Session, parameters: dict[str, Any], context: dict[str, Any]
    ) -> dict[str, Any]:
        score = 88
        context["composite_risk_score"] = score
        return {
            "success": True,
            "input_summary": "Calculating multi-engine risk scoring matrix",
            "output_summary": f"Calculated composite risk score: {score}/100 (HIGH RISK)",
            "context_updates": {"composite_risk_score": score},
        }

    # -------------------------------------------------------------------------
    # 3. Case Management Actions
    # -------------------------------------------------------------------------
    @classmethod
    def _handle_create_incident(
        cls, db: Session, parameters: dict[str, Any], context: dict[str, Any]
    ) -> dict[str, Any]:
        inc_num = f"INC-2026-{uuid.uuid4().hex[:4].upper()}"
        title = parameters.get("title") or context.get("incident_title") or "Automated SOAR Incident Escalation"
        severity = parameters.get("severity") or context.get("severity") or "HIGH"
        inc_type = parameters.get("incident_type") or "ENDPOINT_COMPROMISE"

        new_inc = Incident(
            incident_id=inc_num,
            title=title,
            description=f"Generated autonomously via SOAR Playbook execution. Trigger source: {context.get('trigger_source')}.",
            incident_type=inc_type,
            severity=severity,
            priority="P1" if severity in ("CRITICAL", "HIGH") else "P2",
            status="INVESTIGATING",
            phase="DETECTION_ANALYSIS",
            classification="SUSPICIOUS",
            lead_analyst="SOAR Automation Agent",
            detected_at=datetime.now(timezone.utc),
            simulation_mode=True,
        )
        db.add(new_inc)
        db.flush()

        context["incident_id"] = new_inc.id
        context["incident_number"] = inc_num

        return {
            "success": True,
            "input_summary": f"Creating incident ticket: {title}",
            "output_summary": f"Created incident ticket #{inc_num} (ID: {new_inc.id})",
            "artifacts": {"incident_id": new_inc.id, "incident_number": inc_num},
        }

    @classmethod
    def _handle_create_case(
        cls, db: Session, parameters: dict[str, Any], context: dict[str, Any]
    ) -> dict[str, Any]:
        case_num = f"CASE-2026-{uuid.uuid4().hex[:4].upper()}"
        title = parameters.get("title") or "SOAR Automated Security Case"

        case = Case(
            case_id=case_num,
            title=title,
            description="Auto-generated SOC Case coordinating containment and forensics.",
            priority=parameters.get("priority", "P1"),
            status="OPEN",
            summary=parameters.get("summary", "Coordinating automated containment and forensics."),
        )
        db.add(case)
        db.flush()

        # Link alert if present
        alert_id = context.get("alert_id")
        if alert_id:
            db.add(CaseAlert(case_id=case.id, alert_id=int(alert_id) if str(alert_id).isdigit() else 1))
            db.flush()

        context["case_id"] = case.id
        context["case_number"] = case_num

        return {
            "success": True,
            "input_summary": f"Opening SOC Case: {title}",
            "output_summary": f"Created SOC Case #{case_num} assigned to Tier 2 IR Specialist",
            "artifacts": {"case_id": case.id, "case_number": case_num},
        }

    @classmethod
    def _handle_add_evidence(
        cls, db: Session, parameters: dict[str, Any], context: dict[str, Any]
    ) -> dict[str, Any]:
        inc_id = context.get("incident_id")
        ev_id = f"EVD-{uuid.uuid4().hex[:8].upper()}"
        payload = json.dumps({"source": "SOAR", "timestamp": datetime.now(timezone.utc).isoformat()})
        sha256 = hashlib.sha256(payload.encode("utf-8")).hexdigest()

        if inc_id:
            ev = IncidentEvidence(
                evidence_id=ev_id,
                incident_id=int(inc_id),
                title=parameters.get("title", "SOAR Corroborating Evidence Item"),
                description="Cross-engine evidence captured during automated triage sequence.",
                evidence_type=parameters.get("evidence_type", "ALERT"),
                source_engine="SOAR_AUTOMATION",
                source_id=str(context.get("source_id", "SOAR")),
                hash_sha256=sha256,
                relevance="SUPPORTING",
                is_contained=False,
                collected_at=datetime.now(timezone.utc),
                data_payload=payload,
            )
            db.add(ev)
            db.flush()

        return {
            "success": True,
            "input_summary": "Persisting evidence item to Incident Evidence Vault",
            "output_summary": f"Evidence #{ev_id} committed with SHA-256 integrity verification",
            "artifacts": {"evidence_id": ev_id},
        }

    @classmethod
    def _handle_add_timeline_event(
        cls, db: Session, parameters: dict[str, Any], context: dict[str, Any]
    ) -> dict[str, Any]:
        inc_id = context.get("incident_id")
        if inc_id:
            tle = IncidentTimelineEvent(
                incident_id=int(inc_id),
                timestamp=datetime.now(timezone.utc),
                title=parameters.get("title", "Automated Playbook Triggered"),
                description=parameters.get("description", "Playbook initiated enrichment and correlation sequence."),
                event_category=parameters.get("category", "DETECTION"),
                source="SOAR_AUTOMATION",
                is_milestone=parameters.get("is_milestone", True),
            )
            db.add(tle)
            db.flush()

        return {
            "success": True,
            "input_summary": "Recording timestamped event to chronological timeline",
            "output_summary": "Milestone logged to Incident Timeline",
        }

    @classmethod
    def _handle_add_analyst_note(
        cls, db: Session, parameters: dict[str, Any], context: dict[str, Any]
    ) -> dict[str, Any]:
        inc_id = context.get("incident_id")
        note_text = parameters.get("note", "SOAR playbook completed triage analysis and correlated telemetry.")

        if inc_id:
            db.add(IncidentNote(incident_id=int(inc_id), note=note_text))
            db.flush()

        return {
            "success": True,
            "input_summary": "Appending work log entry to case documentation",
            "output_summary": f"Logged note: '{note_text[:50]}...'",
        }

    @classmethod
    def _handle_attach_playbook(
        cls, db: Session, parameters: dict[str, Any], context: dict[str, Any]
    ) -> dict[str, Any]:
        inc_id = context.get("incident_id")
        pb_id = parameters.get("playbook_id", "PB-IR-001")
        pb = db.query(IncidentPlaybook).filter(IncidentPlaybook.playbook_id == str(pb_id)).first()

        if inc_id and pb:
            inc = db.query(Incident).filter(Incident.id == int(inc_id)).first()
            if inc:
                inc.playbook_id = pb.id
                db.flush()

        return {
            "success": True,
            "input_summary": f"Attaching IR Playbook: {pb_id}",
            "output_summary": f"Attached Standard Operating Procedure: {pb.title if pb else pb_id}",
        }

    # -------------------------------------------------------------------------
    # 4. Simulation Actions (Strictly Non-Destructive Simulation Only)
    # -------------------------------------------------------------------------
    @classmethod
    def _handle_simulate_host_isolation(
        cls, db: Session, parameters: dict[str, Any], context: dict[str, Any]
    ) -> dict[str, Any]:
        target = parameters.get("target_identifier") or context.get("hostname") or "NN-DEV-001"
        inc_id = context.get("incident_id")

        if inc_id:
            act = ResponseAction(
                incident_id=int(inc_id),
                action_id=f"ACT-{uuid.uuid4().hex[:6].upper()}",
                category="CONTAINMENT",
                action_type="SIMULATE_HOST_ISOLATION",
                target_type="HOST",
                target_identifier=target,
                status="EXECUTED",
                simulation_only=True,
                reason="SOAR automated containment to restrict lateral movement.",
                risk_assessment="Low disruption risk in simulation.",
                expected_impact="Host network interfaces isolated in simulation sandbox.",
                simulated_outcome="Successfully applied simulated host isolation. Lateral traffic blocked.",
                executed_at=datetime.now(timezone.utc),
            )
            db.add(act)
            db.flush()

        return {
            "success": True,
            "input_summary": f"Executing simulated host isolation: {target}",
            "output_summary": f"Simulated isolation active for {target}. Host severed from simulated LAN.",
            "simulation_only": True,
        }

    @classmethod
    def _handle_simulate_account_restriction(
        cls, db: Session, parameters: dict[str, Any], context: dict[str, Any]
    ) -> dict[str, Any]:
        user = parameters.get("username") or context.get("username") or "dev.alice"
        inc_id = context.get("incident_id")

        if inc_id:
            act = ResponseAction(
                incident_id=int(inc_id),
                action_id=f"ACT-{uuid.uuid4().hex[:6].upper()}",
                category="CONTAINMENT",
                action_type="SIMULATE_ACCOUNT_RESTRICTION",
                target_type="USER",
                target_identifier=user,
                status="EXECUTED",
                simulation_only=True,
                reason="Automated containment for compromised user account.",
                simulated_outcome=f"Simulated account lockout applied to {user}.",
                executed_at=datetime.now(timezone.utc),
            )
            db.add(act)
            db.flush()

        return {
            "success": True,
            "input_summary": f"Executing simulated account restriction: {user}",
            "output_summary": f"Simulated account restriction applied for {user}.",
            "simulation_only": True,
        }

    @classmethod
    def _handle_simulate_network_block(
        cls, db: Session, parameters: dict[str, Any], context: dict[str, Any]
    ) -> dict[str, Any]:
        ip = parameters.get("ip_address") or "198.51.100.45"
        return {
            "success": True,
            "input_summary": f"Simulating firewall edge block for IP: {ip}",
            "output_summary": f"Simulated perimeter ACL rule injected: DENY IP {ip} ANY ANY",
            "simulation_only": True,
        }

    @classmethod
    def _handle_simulate_ioc_block(
        cls, db: Session, parameters: dict[str, Any], context: dict[str, Any]
    ) -> dict[str, Any]:
        ioc = parameters.get("indicator") or "c2-beacon-sim.test"
        return {
            "success": True,
            "input_summary": f"Simulating gateway sinkhole for domain/hash: {ioc}",
            "output_summary": f"Simulated DNS sinkhole active for {ioc}.",
            "simulation_only": True,
        }

    @classmethod
    def _handle_simulate_session_revocation(
        cls, db: Session, parameters: dict[str, Any], context: dict[str, Any]
    ) -> dict[str, Any]:
        return {
            "success": True,
            "input_summary": "Simulating OAuth/Kerberos session token revocation",
            "output_summary": "Simulated token invalidation successful. Rogue sessions terminated.",
            "simulation_only": True,
        }

    @classmethod
    def _handle_simulate_credential_reset(
        cls, db: Session, parameters: dict[str, Any], context: dict[str, Any]
    ) -> dict[str, Any]:
        return {
            "success": True,
            "input_summary": "Simulating forced credential expiration and MFA prompt",
            "output_summary": "Simulated password reset flag set. Next login requires identity re-verification.",
            "simulation_only": True,
        }

    @classmethod
    def _handle_simulate_remove_indicator(
        cls, db: Session, parameters: dict[str, Any], context: dict[str, Any]
    ) -> dict[str, Any]:
        return {
            "success": True,
            "input_summary": "Simulating malicious file quarantine",
            "output_summary": "Simulated payload moved to quarantine vault.",
            "simulation_only": True,
        }

    @classmethod
    def _handle_simulate_remove_persistence(
        cls, db: Session, parameters: dict[str, Any], context: dict[str, Any]
    ) -> dict[str, Any]:
        return {
            "success": True,
            "input_summary": "Simulating scheduled task and registry run key removal",
            "output_summary": "Simulated persistence mechanisms purged from registry and cron.",
            "simulation_only": True,
        }

    @classmethod
    def _handle_simulate_clean_host(
        cls, db: Session, parameters: dict[str, Any], context: dict[str, Any]
    ) -> dict[str, Any]:
        return {
            "success": True,
            "input_summary": "Simulating endpoint restoration from golden master image",
            "output_summary": "Simulated OS restore completed. System verified clean.",
            "simulation_only": True,
        }

    @classmethod
    def _handle_simulate_restore_host(
        cls, db: Session, parameters: dict[str, Any], context: dict[str, Any]
    ) -> dict[str, Any]:
        target = parameters.get("target_identifier") or "NN-DEV-001"
        return {
            "success": True,
            "input_summary": f"Simulating lifting host isolation for {target}",
            "output_summary": f"Simulated network connectivity restored for {target}.",
            "simulation_only": True,
        }

    # -------------------------------------------------------------------------
    # 5. Notification Simulation Actions
    # -------------------------------------------------------------------------
    @classmethod
    def _handle_simulate_analyst_notification(
        cls, db: Session, parameters: dict[str, Any], context: dict[str, Any]
    ) -> dict[str, Any]:
        msg = parameters.get("message") or "High severity alert escalated by SOAR playbook."
        notif = SocNotification(
            title="SOAR Automated Alert Escalation",
            message=msg,
            notification_type="ALERT",
            reference_type="SOAR_EXECUTION",
            reference_id=str(context.get("execution_id", "SOAR")),
            is_read=False,
        )
        db.add(notif)
        db.flush()

        return {
            "success": True,
            "input_summary": "Publishing simulated analyst dispatch notification",
            "output_summary": f"Dispatched notification to SOC Feed: '{msg[:40]}...'",
        }

    @classmethod
    def _handle_simulate_escalation(
        cls, db: Session, parameters: dict[str, Any], context: dict[str, Any]
    ) -> dict[str, Any]:
        return {
            "success": True,
            "input_summary": "Simulating escalation to Tier 3 Advanced Threat Hunting Unit",
            "output_summary": "Escalation notification dispatched to senior analyst pager (Simulation).",
        }
