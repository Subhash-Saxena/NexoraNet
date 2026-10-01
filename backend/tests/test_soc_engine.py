"""Comprehensive test suite for the Step 12 SOC Dashboard, Alert Triage & Investigations."""

import json

import pytest
from app.db.session import SessionLocal
from app.main import app
from app.models.detection import (
    AlertEvidence,
    AlertNote,
    AlertStatusHistory,
    DetectionAlert,
    DetectionRule,
    DetectionRun,
)
from app.models.enums import AlertStatus, TriageClassification
from app.models.pcap import Capture, ParsedPacket
from app.models.soc import (
    Case,
    CaseAlert,
    CaseInvestigation,
    CaseNote,
    Investigation,
    InvestigationAlert,
    InvestigationEvidence,
    InvestigationFinding,
    InvestigationHypothesis,
    InvestigationNote,
    SocChallengeAttempt,
)
from app.models.user import User
from fastapi import status
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def sample_soc_telemetry(db_session):
    """Seed isolated sample telemetry (capture, parsed packets, rule, alert) for SOC tests."""
    user = db_session.query(User).filter(User.username == "student_dev").first()
    if not user:
        user = db_session.query(User).first()

    capture = Capture(
        name="SOC Test Capture",
        filename="soc_test.pcap",
        storage_path="/tmp/soc_test.pcap",
        format="pcap",
        packet_count=20,
        status="READY",
    )
    db_session.add(capture)
    db_session.flush()

    # Seed parsed packets for network context testing
    for i in range(10):
        pkt = ParsedPacket(
            capture_id=capture.id,
            packet_number=i + 1,
            timestamp=1700200000.0 + i,
            relative_time=float(i),
            protocol="TCP",
            transport_protocol="TCP",
            source_ip="192.168.1.100",
            source_port=40000 + i,
            destination_ip="192.168.1.50",
            destination_port=80,
            captured_length=64,
            info=f"{40000+i} -> 80 [SYN]",
        )
        db_session.add(pkt)

    rule = db_session.query(DetectionRule).first()
    if not rule:
        rule = DetectionRule(
            rule_id="TEST-RULE-001",
            name="Test SOC Detection Rule",
            description="Rule for SOC testing",
            category="TCP",
            severity="HIGH",
            explanation_template="Testing explanation",
            investigation_guide="Step 1: Check SYN flags",
        )
        db_session.add(rule)
        db_session.flush()

    run = DetectionRun(
        user_id=user.id if user else None,
        source_type="PCAP",
        capture_id=capture.id,
        status="COMPLETED",
        rules_matched=1,
        alerts_generated=1,
    )
    db_session.add(run)
    db_session.flush()

    alert = DetectionAlert(
        run_id=run.id,
        rule_id=rule.id,
        capture_id=capture.id,
        user_id=user.id if user else None,
        title="Test TCP SYN Scan Pattern",
        category="TCP",
        severity="HIGH",
        confidence="HIGH",
        status="NEW",
        classification="UNREVIEWED",
        priority="P1",
        source_ip="192.168.1.100",
        source_port=40000,
        destination_ip="192.168.1.50",
        destination_port=80,
        protocol="TCP",
        first_seen_timestamp=1700200000.0,
        last_seen_timestamp=1700200010.0,
        packet_count=10,
        dedup_key="TEST:192.168.1.100:192.168.1.50:80",
        explanation="Test alert explanation for SOC triage validation.",
        investigation_steps=json.dumps(["Verify SYN flags", "Inspect port 80 status"]),
    )
    db_session.add(alert)
    db_session.flush()

    ev = AlertEvidence(
        alert_id=alert.id,
        evidence_type="PACKET",
        packet_number=1,
        timestamp=1700200000.0,
        description="TCP SYN packet initiating handshake",
        evidence_data=json.dumps({"flags": ["SYN"], "seq": 100}),
    )
    db_session.add(ev)
    db_session.commit()

    yield {
        "user": user,
        "capture": capture,
        "rule": rule,
        "run": run,
        "alert": alert,
        "evidence": ev,
    }

    # Cleanup
    db_session.query(SocChallengeAttempt).delete()
    db_session.query(CaseAlert).delete()
    db_session.query(CaseInvestigation).delete()
    db_session.query(CaseNote).delete()
    db_session.query(Case).delete()
    db_session.query(InvestigationNote).delete()
    db_session.query(InvestigationFinding).delete()
    db_session.query(InvestigationHypothesis).delete()
    db_session.query(InvestigationEvidence).delete()
    db_session.query(InvestigationAlert).delete()
    db_session.query(Investigation).delete()
    db_session.query(AlertEvidence).filter(AlertEvidence.alert_id == alert.id).delete()
    db_session.query(AlertNote).filter(AlertNote.alert_id == alert.id).delete()
    db_session.query(AlertStatusHistory).filter(AlertStatusHistory.alert_id == alert.id).delete()
    db_session.query(DetectionAlert).filter(DetectionAlert.id == alert.id).delete()
    db_session.query(DetectionRun).filter(DetectionRun.id == run.id).delete()
    db_session.query(ParsedPacket).filter(ParsedPacket.capture_id == capture.id).delete()
    db_session.query(Capture).filter(Capture.id == capture.id).delete()
    db_session.commit()


def test_soc_module_status_endpoint(client):
    """Verify GET /api/v1/soc returns planned status for backward compatibility."""
    resp = client.get("/api/v1/soc")
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert data["module"] == "soc"
    assert data["status"] == "planned"


def test_soc_overview_and_statistics(client, sample_soc_telemetry):
    """Verify GET /api/v1/soc/overview and /statistics return accurate metrics."""
    resp = client.get("/api/v1/soc/overview")
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert "metrics" in data
    assert data["metrics"]["total_alerts"] >= 1
    assert data["metrics"]["active_rules_count"] >= 1
    assert data["environment_status"] == "Offline Training Environment"
    assert len(data["learning_recommendations"]) >= 1

    resp_stats = client.get("/api/v1/soc/statistics")
    assert resp_stats.status_code == status.HTTP_200_OK
    stats_data = resp_stats.json()
    assert "alerts_by_severity" in stats_data
    assert "alerts_by_priority" in stats_data
    assert "top_sources" in stats_data


def test_soc_activity_feed(client, sample_soc_telemetry):
    """Verify GET /api/v1/soc/activity lists recent activity stream."""
    resp = client.get("/api/v1/soc/activity")
    assert resp.status_code == status.HTTP_200_OK
    items = resp.json()
    assert isinstance(items, list)


def test_soc_alerts_filtering_and_prioritization(client, sample_soc_telemetry):
    """Verify alert listing with search, category filtering, and explainable priority."""
    alert = sample_soc_telemetry["alert"]

    # Filter by category
    resp = client.get("/api/v1/soc/alerts?category=TCP")
    assert resp.status_code == status.HTTP_200_OK
    alerts = resp.json()
    assert len(alerts) >= 1
    first = next(a for a in alerts if a["id"] == alert.id)
    assert first["priority"] in ["P1", "P2", "P3", "P4"]
    assert first["priority_reason"]
    assert first["evidence_count"] >= 1

    # Search filter
    search_resp = client.get("/api/v1/soc/alerts?q=SYN")
    assert search_resp.status_code == status.HTTP_200_OK
    assert any(a["id"] == alert.id for a in search_resp.json())


def test_soc_alert_detail_and_network_context(client, sample_soc_telemetry):
    """Verify GET /api/v1/soc/alerts/{id} returns evidence, network context, and timeline."""
    alert = sample_soc_telemetry["alert"]

    resp = client.get(f"/api/v1/soc/alerts/{alert.id}")
    assert resp.status_code == status.HTTP_200_OK
    detail = resp.json()
    assert detail["id"] == alert.id
    assert len(detail["evidence"]) >= 1
    assert "network_context" in detail
    assert detail["network_context"]["source"]["packet_count"] >= 10
    assert len(detail["timeline"]) >= 1


def test_soc_alert_triage_and_classification(client, sample_soc_telemetry):
    """Verify acknowledging and classifying alerts with audit history."""
    alert = sample_soc_telemetry["alert"]

    # 1. Acknowledge alert
    ack_resp = client.post(
        f"/api/v1/soc/alerts/{alert.id}/acknowledge",
        json={"reason": "Analyst queued alert for packet review."},
    )
    assert ack_resp.status_code == status.HTTP_200_OK
    assert ack_resp.json()["status"] == AlertStatus.ACKNOWLEDGED.value

    # 2. Update classification
    class_resp = client.patch(
        f"/api/v1/soc/alerts/{alert.id}/classification",
        json={
            "classification": TriageClassification.BENIGN.value,
            "reason": "Traffic corresponds to authorized local development test script.",
            "status": AlertStatus.CLOSED.value,
        },
    )
    assert class_resp.status_code == status.HTTP_200_OK
    updated = class_resp.json()
    assert updated["classification"] == TriageClassification.BENIGN.value
    assert updated["status"] == AlertStatus.CLOSED.value


def test_soc_bulk_alert_action(client, sample_soc_telemetry):
    """Verify bulk acknowledgement on alerts."""
    alert = sample_soc_telemetry["alert"]

    resp = client.post(
        "/api/v1/soc/alerts/bulk-action",
        json={
            "alert_ids": [alert.id],
            "action": "ACKNOWLEDGE",
            "reason": "Bulk acknowledgement in lab exercise.",
        },
    )
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["status"] == "SUCCESS"
    assert resp.json()["affected_alerts"] == 1


def test_investigation_full_lifecycle(client, sample_soc_telemetry):
    """Test creating an investigation, adding hypotheses, findings, notes, and report export."""
    alert = sample_soc_telemetry["alert"]

    # 1. Create Investigation
    inv_payload = {
        "title": "Investigating Port 80 SYN Burst",
        "description": "Analyzing multiple connection requests targeting web service.",
        "priority": "P2",
        "alert_ids": [alert.id],
    }
    create_resp = client.post("/api/v1/soc/investigations", json=inv_payload)
    assert create_resp.status_code == status.HTTP_201_CREATED
    inv_data = create_resp.json()
    inv_id = inv_data["id"]
    assert inv_data["investigation_id"].startswith("INV-")
    assert len(inv_data["alerts"]) >= 1

    # 2. Formulate Hypothesis
    hyp_resp = client.post(
        f"/api/v1/soc/investigations/{inv_id}/hypotheses",
        json={
            "hypothesis_text": "Repeated SYN packets indicate automated connectivity checks rather than an exploit attempt.",
            "status": "UNTESTED",
        },
    )
    assert hyp_resp.status_code == status.HTTP_200_OK
    hyp_id = hyp_resp.json()["id"]

    # 3. Update Hypothesis
    patch_hyp = client.patch(
        f"/api/v1/soc/investigations/{inv_id}/hypotheses/{hyp_id}",
        json={
            "status": "SUPPORTED",
            "reasoning": "Packet timestamps show regular retry intervals matching standard client keepalives.",
        },
    )
    assert patch_hyp.status_code == status.HTTP_200_OK
    assert patch_hyp.json()["status"] == "SUPPORTED"

    # 4. Log Finding
    find_resp = client.post(
        f"/api/v1/soc/investigations/{inv_id}/findings",
        json={
            "title": "Handshake Retries Verified",
            "description": "Source attempted 10 handshakes over 10s without ACK completion.",
            "confidence": "HIGH",
        },
    )
    assert find_resp.status_code == status.HTTP_200_OK
    assert find_resp.json()["confidence"] == "HIGH"

    # 5. Add Analyst Note
    note_resp = client.post(
        f"/api/v1/soc/investigations/{inv_id}/notes",
        json={"note": "Wireshark display filter: tcp.flags.syn==1 and tcp.flags.ack==0"},
    )
    assert note_resp.status_code == status.HTTP_200_OK

    # 6. Conclude & Close Investigation
    update_resp = client.patch(
        f"/api/v1/soc/investigations/{inv_id}",
        json={
            "status": "RESOLVED",
            "classification": "BENIGN",
            "conclusion": "Observed activity represents legitimate retry behavior during server restart.",
        },
    )
    assert update_resp.status_code == status.HTTP_200_OK
    assert update_resp.json()["status"] == "RESOLVED"

    # 7. Generate Investigation Report
    report_resp = client.get(f"/api/v1/soc/investigations/{inv_id}/report")
    assert report_resp.status_code == status.HTTP_200_OK
    rep = report_resp.json()
    assert rep["report_type"] == "SOC_INVESTIGATION_REPORT"
    assert rep["summary_metrics"]["total_hypotheses"] == 1
    assert rep["summary_metrics"]["total_findings"] == 1


def test_case_management(client, sample_soc_telemetry):
    """Test case creation and linking investigations."""
    alert = sample_soc_telemetry["alert"]

    # 1. Create Case
    case_resp = client.post(
        "/api/v1/soc/cases",
        json={
            "title": "Q3 Network Telemetry Review",
            "description": "Reviewing all recurring connection anomalies across LAN endpoints.",
            "priority": "P3",
            "alert_ids": [alert.id],
        },
    )
    assert case_resp.status_code == status.HTTP_201_CREATED
    case_data = case_resp.json()
    case_id = case_data["id"]

    # 2. Get Case Detail
    detail_resp = client.get(f"/api/v1/soc/cases/{case_id}")
    assert detail_resp.status_code == status.HTTP_200_OK
    assert detail_resp.json()["case_id"].startswith("CASE-")
    assert len(detail_resp.json()["alerts"]) == 1


def test_detection_coverage_and_challenges(client, sample_soc_telemetry):
    """Verify detection coverage breakdown and challenge listing."""
    cov_resp = client.get("/api/v1/soc/detection-coverage")
    assert cov_resp.status_code == status.HTTP_200_OK
    cov = cov_resp.json()
    assert cov["total_rules"] >= 15
    assert len(cov["categories"]) >= 5

    chal_resp = client.get("/api/v1/soc/challenges")
    assert chal_resp.status_code == status.HTTP_200_OK
    chals = chal_resp.json()
    assert len(chals) >= 5


def test_soc_datasets_and_audit_logs(client, sample_soc_telemetry):
    """Verify dataset listing and audit log retrieval."""
    ds_resp = client.get("/api/v1/soc/datasets")
    assert ds_resp.status_code == status.HTTP_200_OK
    assert len(ds_resp.json()) == 5

    audit_resp = client.get("/api/v1/soc/audit-logs")
    assert audit_resp.status_code == status.HTTP_200_OK
    assert isinstance(audit_resp.json(), list)


def test_security_idor_and_validation(client):
    """Verify non-existent alert/investigation/case requests return 404."""
    assert client.get("/api/v1/soc/alerts/999999").status_code == status.HTTP_404_NOT_FOUND
    assert client.get("/api/v1/soc/investigations/999999").status_code == status.HTTP_404_NOT_FOUND
    assert client.get("/api/v1/soc/cases/999999").status_code == status.HTTP_404_NOT_FOUND
