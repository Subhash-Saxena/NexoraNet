"""Comprehensive test suite for Step 17: Incident Response, Case Management & MITRE ATT&CK."""

import json
from datetime import datetime, timezone

import pytest
from app.db.session import SessionLocal
from app.main import app
from app.models.detection import DetectionAlert, DetectionRule
from app.models.enums import (
    AlertSeverity,
    AlertStatus,
)
from app.models.mitre import AttackTactic
from app.services.incident_response.seed_service import IncidentResponseSeedService
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

client = TestClient(app)


@pytest.fixture
def db_session():
    """Database session fixture."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def ensure_incident_response_data(db_session: Session):
    """Ensure MITRE catalog, playbooks, and synthetic incidents are seeded."""
    tactic = db_session.execute(select(AttackTactic)).first()
    if not tactic:
        IncidentResponseSeedService.seed_all(db_session)


# ---------------------------------------------------------------------------
# 1. Incident Listing & Filtering Tests
# ---------------------------------------------------------------------------


def test_list_incidents():
    """Verify incidents listing with pagination and filters."""
    resp = client.get("/api/v1/incidents")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 6
    assert len(data["items"]) >= 6

    # Filter by severity
    resp_crit = client.get("/api/v1/incidents?severity=CRITICAL")
    assert resp_crit.status_code == 200
    for inc in resp_crit.json()["items"]:
        assert inc["severity"] == "CRITICAL"

    # Filter by status
    resp_cont = client.get("/api/v1/incidents?status=CONTAINMENT")
    assert resp_cont.status_code == 200
    for inc in resp_cont.json()["items"]:
        assert inc["status"] == "CONTAINMENT"

    # Search filter
    resp_search = client.get("/api/v1/incidents?search=Ransomware")
    assert resp_search.status_code == 200
    assert len(resp_search.json()["items"]) >= 1


def test_incident_metrics():
    """Verify metrics calculation endpoint."""
    resp = client.get("/api/v1/incidents/metrics")
    assert resp.status_code == 200
    metrics = resp.json()
    assert metrics["total_incidents"] >= 6
    assert "active_incidents" in metrics
    assert "by_status" in metrics
    assert "by_severity" in metrics
    assert "by_type" in metrics


# ---------------------------------------------------------------------------
# 2. Incident Creation & Detail Tests
# ---------------------------------------------------------------------------


def test_create_and_get_incident():
    """Verify incident ticket creation and detail retrieval."""
    payload = {
        "title": "Suspected SSH Brute Force against Bastion",
        "description": "High volume of failed SSH login attempts observed on port 22.",
        "incident_type": "CREDENTIAL_ATTACK",
        "severity": "HIGH",
        "priority": "P2",
        "lead_analyst": "SOC Trainee Alex",
    }
    resp = client.post("/api/v1/incidents", json=payload)
    assert resp.status_code == 201
    created = resp.json()
    assert created["incident_id"].startswith("INC-")
    assert created["title"] == payload["title"]
    assert created["status"] == "NEW"
    assert created["phase"] == "DETECTION_ANALYSIS"
    assert created["simulation_mode"] is True

    # Retrieve by stable ID
    resp_get = client.get(f"/api/v1/incidents/{created['incident_id']}")
    assert resp_get.status_code == 200
    detail = resp_get.json()
    assert detail["id"] == created["id"]
    assert len(detail["timeline_events"]) >= 1  # Automatic creation milestone


def test_update_incident_lifecycle():
    """Verify incident status and phase transitions with automated timestamp recording."""
    # Create incident
    resp_create = client.post("/api/v1/incidents", json={
        "title": "Phishing Triage Scenario",
        "description": "Testing status lifecycle progression",
        "incident_type": "PHISHING",
        "severity": "MEDIUM",
    })
    inc_id = resp_create.json()["incident_id"]

    # Transition to CONTAINMENT
    resp_contain = client.patch(f"/api/v1/incidents/{inc_id}", json={
        "status": "CONTAINMENT",
        "classification": "CONFIRMED_INCIDENT",
        "summary": "Analyst confirmed malicious macro attachment.",
    })
    assert resp_contain.status_code == 200
    contained = resp_contain.json()
    assert contained["status"] == "CONTAINMENT"
    assert contained["phase"] == "CONTAINMENT_ERADICATION_RECOVERY"
    assert contained["contained_at"] is not None

    # Transition to CLOSED
    resp_close = client.patch(f"/api/v1/incidents/{inc_id}", json={
        "status": "CLOSED",
        "lessons_learned": "Block macro execution via Group Policy.",
    })
    assert resp_close.status_code == 200
    closed = resp_close.json()
    assert closed["status"] == "CLOSED"
    assert closed["phase"] == "POST_INCIDENT_ACTIVITY"
    assert closed["closed_at"] is not None


# ---------------------------------------------------------------------------
# 3. Alert Escalation to Incident Tests
# ---------------------------------------------------------------------------


def test_escalate_alert_to_incident(db_session: Session):
    """Verify escalating a Detection Alert creates an Incident with linked evidence and timeline."""
    # Ensure detection rule and alert exist
    rule = db_session.execute(select(DetectionRule)).scalars().first()
    if not rule:
        rule = DetectionRule(
            rule_id="RULE-TEST-001",
            name="Suspicious Outbound Port 4444",
            description="Testing alert escalation",
            severity="HIGH",
            category="MALWARE",
        )
        db_session.add(rule)
        db_session.flush()

    alert = db_session.execute(select(DetectionAlert)).scalars().first()
    if not alert:
        from app.models.detection import DetectionRun
        run = DetectionRun(
            status="COMPLETED",
            source_type="PCAP",
        )
        db_session.add(run)
        db_session.flush()

        alert = DetectionAlert(
            run_id=run.id,
            rule_id=rule.id,
            title="Suspicious Outbound Port 4444",
            category="MALWARE",
            severity=AlertSeverity.HIGH,
            confidence="HIGH",
            status=AlertStatus.NEW,
            dedup_key="test_dedup_escalate",
            explanation="Testing alert escalation",
            source_ip="192.168.1.100",
            source_port=54321,
            destination_ip="203.0.113.5",
            destination_port=4444,
            protocol="TCP",
        )
        db_session.add(alert)
        db_session.commit()
        db_session.refresh(alert)

    # Escalate to incident
    resp = client.post("/api/v1/incidents/escalate-alert", json={
        "alert_id": alert.id,
        "title": "Escalated: Meterpreter Shell Alert",
        "severity": "CRITICAL",
    })
    assert resp.status_code == 201
    inc = resp.json()
    assert "Escalated: Meterpreter Shell Alert" in inc["title"]
    assert len(inc["alerts"]) >= 1
    assert inc["alerts"][0]["alert_id"] == alert.id
    assert len(inc["evidence"]) >= 1
    assert inc["evidence"][0]["source_engine"] == "DETECTION_ENGINE"


# ---------------------------------------------------------------------------
# 4. Evidence Management & Chain of Custody Tests
# ---------------------------------------------------------------------------


def test_evidence_management_and_audit():
    """Verify adding evidence, computing SHA-256 integrity hash, and verifying audit chain."""
    inc_resp = client.get("/api/v1/incidents/INC-2026-0001")
    inc_id = inc_resp.json()["incident_id"]

    # Add new evidence item
    ev_payload = {
        "title": "Dumped PowerShell Memory Script Block",
        "description": "Extracted from host memory dump.",
        "evidence_type": "PROCESS_EVENT",
        "source_engine": "ENDPOINT_SECURITY",
        "source_id": "MEM-DUMP-88",
        "data_payload": {"decoded_script": "Invoke-Mimikatz -DumpCreds"},
        "relevance": "SUPPORTING",
    }
    resp_ev = client.post(f"/api/v1/incidents/{inc_id}/evidence", json=ev_payload)
    assert resp_ev.status_code == 201
    evidence = resp_ev.json()
    assert evidence["hash_sha256"] is not None
    assert len(evidence["hash_sha256"]) == 64  # SHA-256 hex string

    # Verify SHA-256 hash endpoint
    resp_verify = client.post(f"/api/v1/incidents/{inc_id}/evidence/{evidence['id']}/verify-hash")
    assert resp_verify.status_code == 200
    assert resp_verify.json()["is_valid"] is True

    # Update evidence metadata
    resp_patch = client.patch(f"/api/v1/incidents/{inc_id}/evidence/{evidence['id']}", json={
        "relevance": "CONTEXT",
        "is_contained": True,
    })
    assert resp_patch.status_code == 200
    assert resp_patch.json()["relevance"] == "CONTEXT"
    assert resp_patch.json()["is_contained"] is True


# ---------------------------------------------------------------------------
# 5. Timeline Management Tests
# ---------------------------------------------------------------------------


def test_timeline_events():
    """Verify timeline event addition and querying."""
    inc_resp = client.get("/api/v1/incidents/INC-2026-0001")
    inc_id = inc_resp.json()["incident_id"]

    # Add custom timeline event
    tl_payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "title": "Firewall Egress Rule Verified",
        "description": "SOC analyst confirmed drop rule active on edge firewall.",
        "event_category": "CONTAINMENT",
        "source": "ANALYST",
        "is_milestone": True,
    }
    resp = client.post(f"/api/v1/incidents/{inc_id}/timeline", json=tl_payload)
    assert resp.status_code == 201
    assert resp.json()["title"] == tl_payload["title"]

    # Query timeline
    resp_list = client.get(f"/api/v1/incidents/{inc_id}/timeline")
    assert resp_list.status_code == 200
    events = resp_list.json()
    assert len(events) >= 1
    # Verify deterministic chronological ordering
    timestamps = [e["timestamp"] for e in events]
    assert timestamps == sorted(timestamps)


# ---------------------------------------------------------------------------
# 6. Hypotheses & Findings Tests
# ---------------------------------------------------------------------------


def test_hypotheses_and_findings():
    """Verify proposing hypotheses, updating conclusions, and recording findings."""
    inc_resp = client.get("/api/v1/incidents/INC-2026-0003")
    inc_id = inc_resp.json()["incident_id"]

    # Propose hypothesis
    resp_hyp = client.post(f"/api/v1/incidents/{inc_id}/hypotheses", json={
        "statement": "Attacker exfiltrated encrypted zip archive through DNS TXT queries.",
        "confidence": "HIGH",
        "rationale": "High entropy observed in DNS query strings.",
    })
    assert resp_hyp.status_code == 201
    hyp = resp_hyp.json()
    assert hyp["status"] == "PROPOSED"

    # Update hypothesis status
    resp_up = client.patch(f"/api/v1/incidents/{inc_id}/hypotheses/{hyp['id']}", json={
        "status": "SUPPORTED",
        "rationale": "Reconstructed TXT payload yielded valid PK zip file header.",
    })
    assert resp_up.status_code == 200
    assert resp_up.json()["status"] == "SUPPORTED"

    # Record finding
    resp_fnd = client.post(f"/api/v1/incidents/{inc_id}/findings", json={
        "title": "Confirmed DNS Tunneling Exfiltration Channel",
        "description": "Adversary encoded proprietary CAD designs into Base32 subdomains of data-sync-cdn.xyz.",
        "severity": "HIGH",
        "confidence": "HIGH",
        "affected_systems": "WS-ENG-12",
        "mitre_technique": "T1071.004",
        "mitre_tactic": "TA0011",
    })
    assert resp_fnd.status_code == 201
    assert resp_fnd.json()["mitre_technique"] == "T1071.004"


# ---------------------------------------------------------------------------
# 7. Response Simulation Safety Tests (Simulation-Only Invariant)
# ---------------------------------------------------------------------------


def test_response_action_simulation_safety():
    """Verify that defensive response actions are strictly simulation-only and reversible."""
    inc_resp = client.get("/api/v1/incidents/INC-2026-0004")
    inc_id = inc_resp.json()["incident_id"]

    # Propose action
    action_payload = {
        "category": "CONTAINMENT",
        "action_type": "SIMULATE_HOST_ISOLATION",
        "target_type": "HOST",
        "target_identifier": "WS-FIN-09 (10.0.4.99)",
        "reason": "Prevent LotL script from dropping ransomware payload.",
        "risk_assessment": "User will lose network access temporarily.",
        "expected_impact": "Isolate from internal LAN while retaining management agent.",
    }
    resp_prop = client.post(f"/api/v1/incidents/{inc_id}/actions", json=action_payload)
    assert resp_prop.status_code == 201
    action = resp_prop.json()
    assert action["status"] == "PROPOSED"
    assert action["simulation_only"] is True  # CRITICAL INVARIANT

    # Execute action
    resp_exec = client.post(f"/api/v1/incidents/{inc_id}/actions/{action['id']}/execute")
    assert resp_exec.status_code == 200
    executed = resp_exec.json()
    assert executed["status"] == "EXECUTED"
    assert executed["simulation_only"] is True
    assert "[SIMULATION]" in executed["simulated_outcome"]
    assert executed["executed_at"] is not None

    # Revert action
    resp_revert = client.post(f"/api/v1/incidents/{inc_id}/actions/{action['id']}/revert")
    assert resp_revert.status_code == 200
    reverted = resp_revert.json()
    assert reverted["status"] == "REVERTED"
    assert reverted["simulation_only"] is True
    assert reverted["reverted_at"] is not None


# ---------------------------------------------------------------------------
# 8. MITRE ATT&CK Catalog & Matrix Coverage Tests
# ---------------------------------------------------------------------------


def test_mitre_catalog_and_coverage():
    """Verify 14 tactics, technique searching, and matrix coverage heat map."""
    # List tactics
    resp_tactics = client.get("/api/v1/mitre/tactics")
    assert resp_tactics.status_code == 200
    tactics = resp_tactics.json()
    assert len(tactics) == 14
    tactic_names = [t["name"] for t in tactics]
    assert "Reconnaissance" in tactic_names
    assert "Initial Access" in tactic_names
    assert "Execution" in tactic_names
    assert "Impact" in tactic_names

    # Search techniques
    resp_techs = client.get("/api/v1/mitre/techniques?search=PowerShell")
    assert resp_techs.status_code == 200
    techs = resp_techs.json()
    assert len(techs) >= 1
    assert any(t["technique_id"] == "T1059.001" for t in techs)

    # Matrix coverage calculation
    resp_cov = client.get("/api/v1/mitre/coverage")
    assert resp_cov.status_code == 200
    cov = resp_cov.json()
    assert cov["total_techniques"] > 0
    assert len(cov["tactics"]) == 14
    assert cov["coverage_percentage"] >= 0.0


def test_mitre_technique_mapping():
    """Verify mapping and unmapping a technique to an incident."""
    inc_resp = client.get("/api/v1/incidents/INC-2026-0004")
    inc_id = inc_resp.json()["incident_id"]

    # Map T1059.001 (PowerShell) to incident
    resp_map = client.post(f"/api/v1/incidents/{inc_id}/mitre/map", json={
        "technique_id_or_code": "T1059.001",
        "mapping_confidence": "OBSERVED_EVIDENCE",
        "evidence_summary": "Base64 encoded script block executed from Word doc.",
        "phase": "EXECUTION",
    })
    assert resp_map.status_code == 201
    mapping = resp_map.json()
    assert mapping["mapping_confidence"] == "OBSERVED_EVIDENCE"
    assert mapping["technique"]["technique_id"] == "T1059.001"

    # Unmap technique
    resp_del = client.delete(f"/api/v1/incidents/{inc_id}/mitre/map/T1059.001")
    assert resp_del.status_code == 204


# ---------------------------------------------------------------------------
# 9. Playbooks Tests
# ---------------------------------------------------------------------------


def test_playbooks():
    """Verify 10 IR Playbooks and incident attachment."""
    resp = client.get("/api/v1/playbooks")
    assert resp.status_code == 200
    playbooks = resp.json()
    assert len(playbooks) == 10
    pb_ids = [p["playbook_id"] for p in playbooks]
    assert "PB-RANSOMWARE" in pb_ids
    assert "PB-CRED-STUFFING" in pb_ids
    assert "PB-DATA-EXFIL" in pb_ids
    assert "PB-WEB-EXPLOIT" in pb_ids

    # Inspect playbook details
    pb = next(p for p in playbooks if p["playbook_id"] == "PB-RANSOMWARE")
    phases = json.loads(pb["phases_definition"])
    assert "CONTAINMENT" in phases
    assert "ERADICATION" in phases

    # Attach to incident
    inc_resp = client.get("/api/v1/incidents/INC-2026-0006")
    inc_id = inc_resp.json()["incident_id"]
    resp_attach = client.post(f"/api/v1/incidents/{inc_id}/playbooks/attach?playbook_id=PB-WEB-EXPLOIT")
    assert resp_attach.status_code == 200
    assert resp_attach.json()["playbook"]["playbook_id"] == "PB-WEB-EXPLOIT"


# ---------------------------------------------------------------------------
# 10. Executive Report Generation Tests
# ---------------------------------------------------------------------------


def test_generate_incident_report():
    """Verify NIST SP 800-61 post-incident executive report generation."""
    resp = client.get("/api/v1/incidents/INC-2026-0001/report")
    assert resp.status_code == 200
    report = resp.json()
    assert report["incident_id"] == "INC-2026-0001"
    assert "markdown_report" in report
    md = report["markdown_report"]
    assert "# INCIDENT REPORT:" in md
    assert "## 1. Executive Summary" in md
    assert "## 3. MITRE ATT&CK Matrix Alignment" in md
    assert "## 4. Key Evidence Collected & Chain of Custody" in md
    assert "## 6. Simulated Response Actions Executed" in md
    assert "Strictly synthetic training data" in md
