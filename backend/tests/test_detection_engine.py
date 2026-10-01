"""Comprehensive test suite for the Step 11 Network Detection Engine."""

import json
import tempfile
from pathlib import Path

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
from app.models.enums import AlertStatus, DetectionRunStatus
from app.models.pcap import Capture, ParsedPacket
from app.services.detection.detection_engine import DetectionEngine
from app.services.detection.feature_service import FeatureExtractionService
from app.services.pcap_parser_service import pcap_parser_service
from fastapi import status
from fastapi.testclient import TestClient
from scapy.all import ARP, DNS, DNSQR, ICMP, IP, TCP, UDP, Ether, wrpcap


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
def synthetic_detection_pcap():
    """Create a temporary synthetic PCAP with attack/anomaly telemetry patterns."""
    with tempfile.NamedTemporaryFile(suffix=".pcap", delete=False) as tmp:
        tmp_path = Path(tmp.name)

    pkts = []
    base_t = 1700100000.0

    # 1. ARP Conflict (Same IP 192.168.1.1 with 2 MACs)
    a1 = Ether(src="02:00:00:00:00:01") / ARP(op=2, hwsrc="02:00:00:00:00:01", psrc="192.168.1.1", pdst="192.168.1.50")
    a1.time = base_t
    a2 = Ether(src="02:00:00:00:00:99") / ARP(op=2, hwsrc="02:00:00:00:00:99", psrc="192.168.1.1", pdst="192.168.1.50")
    a2.time = base_t + 1.0
    pkts.extend([a1, a2])

    # 2. Repeated TCP SYN Connection Attempts (7 SYNs to port 80 without ACK)
    for i in range(7):
        syn_pkt = Ether() / IP(src="10.0.0.100", dst="10.0.0.50") / TCP(sport=50000 + i, dport=80, flags="S", seq=1000 + i)
        syn_pkt.time = base_t + 5.0 + (i * 0.5)
        pkts.append(syn_pkt)

    # 3. DNS NXDOMAIN responses (5 NXDOMAIN queries)
    for i in range(5):
        q = Ether() / IP(src="8.8.8.8", dst="10.0.0.100") / UDP(sport=53, dport=53000 + i) / DNS(
            id=0x2000 + i,
            qr=1,
            rcode=3,
            qd=DNSQR(qname=f"random-nonexistent-{i}.example.org"),
        )
        q.time = base_t + 10.0 + (i * 0.2)
        pkts.append(q)

    # 4. Unusual Non-Standard Port (Traffic to port 4444)
    rev_pkt = Ether() / IP(src="10.0.0.100", dst="192.168.1.200") / TCP(sport=54321, dport=4444, flags="PA")
    rev_pkt.time = base_t + 15.0
    pkts.append(rev_pkt)

    # 5. ICMP burst (10 echo requests)
    for i in range(10):
        icmp_pkt = Ether() / IP(src="10.0.0.100", dst="10.0.0.1") / ICMP(type=8, id=0x4321, seq=i)
        icmp_pkt.time = base_t + 20.0 + (i * 0.1)
        pkts.append(icmp_pkt)

    # 6. Recon probe to multiple destinations (10.0.0.100 -> 10.0.0.1, 10.0.0.2, 10.0.0.3, 10.0.0.4)
    for idx, target_ip in enumerate(["10.0.0.1", "10.0.0.2", "10.0.0.3", "10.0.0.4", "10.0.0.5"]):
        probe = Ether() / IP(src="10.0.0.100", dst=target_ip) / TCP(sport=61000 + idx, dport=443, flags="S")
        probe.time = base_t + 25.0 + idx
        pkts.append(probe)

    wrpcap(str(tmp_path), pkts)
    yield tmp_path

    if tmp_path.exists():
        tmp_path.unlink()


def test_feature_extraction_service(db_session, synthetic_detection_pcap):
    """Test normalization and flow aggregation over parsed packets."""
    capture = Capture(
        name="Detection Test Capture",
        filename="detection_test.pcap",
        storage_path=str(synthetic_detection_pcap),
        format="pcap",
        status="UPLOADED",
    )
    db_session.add(capture)
    db_session.commit()
    db_session.refresh(capture)

    # Parse with Step 10 parser
    pcap_parser_service.parse_and_index_capture(db_session, capture)

    packets = db_session.query(ParsedPacket).filter(ParsedPacket.capture_id == capture.id).all()
    assert len(packets) > 10

    svc = FeatureExtractionService()
    events, flows, hosts = svc.extract_features(packets)

    assert len(events) == len(packets)
    assert len(flows) > 0
    assert "10.0.0.100" in hosts

    hp = hosts["10.0.0.100"]
    assert hp.syn_count >= 7
    assert len(hp.icmp_requests) >= 10
    assert len(hp.distinct_destinations) >= 4

    # Cleanup
    db_session.delete(capture)
    db_session.commit()


def test_all_15_detection_rules_seeded(db_session):
    """Verify that all 15 built-in detection rules exist in the database."""
    rules = db_session.query(DetectionRule).all()
    rule_ids = {r.rule_id for r in rules}

    expected_rules = [
        "NET-TCP-001",
        "NET-TCP-002",
        "NET-TCP-003",
        "NET-CONN-001",
        "NET-CONN-002",
        "NET-DNS-001",
        "NET-DNS-002",
        "NET-DNS-003",
        "NET-ARP-001",
        "NET-ICMP-001",
        "NET-PORT-001",
        "NET-TRAFFIC-001",
        "NET-TRAFFIC-002",
        "NET-HTTP-001",
        "NET-RECON-001",
    ]

    for expected in expected_rules:
        assert expected in rule_ids, f"Rule {expected} should be seeded in the database."


def test_detection_engine_evaluates_patterns(db_session, synthetic_detection_pcap):
    """Test that detection engine generates expected alerts for synthesized patterns."""
    capture = Capture(
        name="Pattern Eval Capture",
        filename="eval.pcap",
        storage_path=str(synthetic_detection_pcap),
        format="pcap",
        status="UPLOADED",
    )
    db_session.add(capture)
    db_session.commit()
    db_session.refresh(capture)

    pcap_parser_service.parse_and_index_capture(db_session, capture)
    packets = db_session.query(ParsedPacket).filter(ParsedPacket.capture_id == capture.id).all()
    rules = db_session.query(DetectionRule).filter(DetectionRule.status == "ENABLED").all()

    engine = DetectionEngine()
    matches = engine.evaluate(packets=packets, rules=rules, capture_id=capture.id)

    matched_rule_codes = {m.rule.rule_id for m in matches}

    # Verify key detections were triggered
    assert "NET-TCP-001" in matched_rule_codes  # Repeated SYNs
    assert "NET-ARP-001" in matched_rule_codes  # Conflicting MACs
    assert "NET-DNS-001" in matched_rule_codes  # NXDOMAIN spike
    assert "NET-PORT-001" in matched_rule_codes  # Port 4444
    assert "NET-ICMP-001" in matched_rule_codes  # ICMP burst
    assert "NET-RECON-001" in matched_rule_codes  # Multi-destination

    # Check evidence generation
    for m in matches:
        assert len(m.evidence_items) > 0
        assert m.explanation
        assert len(m.investigation_steps) > 0

    # Cleanup
    db_session.delete(capture)
    db_session.commit()


def test_alert_deduplication(db_session):
    """Test that multiple occurrences with same dedup_key are collapsed into 1 alert."""
    engine = DetectionEngine()

    # Create dummy parsed packets with 15 TCP SYN packets from same src to same dst:80
    pkts = []
    base_t = 1700100000.0
    for i in range(15):
        p = ParsedPacket(
            id=100 + i,
            capture_id=999,
            packet_number=i + 1,
            timestamp=base_t + i,
            relative_time=float(i),
            protocol="TCP",
            transport_protocol="TCP",
            source_ip="192.168.1.10",
            destination_ip="192.168.1.1",
            source_port=40000 + i,
            destination_port=80,
            tcp_flags=json.dumps(["SYN"]),
            info=f"{40000+i} -> 80 [SYN]",
        )
        pkts.append(p)

    rule = db_session.query(DetectionRule).filter(DetectionRule.rule_id == "NET-TCP-001").first()
    matches = engine.evaluate(packets=pkts, rules=[rule], capture_id=999)

    # Must be exactly 1 deduplicated alert
    assert len(matches) == 1
    assert matches[0].packet_count == 15
    assert len(matches[0].evidence_items) > 0


def test_api_detection_stats(client):
    """Test GET /api/v1/detection/stats."""
    resp = client.get("/api/v1/detection/stats")
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert "total_runs" in data
    assert "total_alerts" in data
    assert "active_alerts" in data
    assert "alerts_by_severity" in data
    assert "alerts_by_category" in data


def test_api_rules_list_and_get(client):
    """Test listing and fetching detection rules via API."""
    resp = client.get("/api/v1/detection/rules")
    assert resp.status_code == status.HTTP_200_OK
    rules = resp.json()
    assert len(rules) >= 15

    # Filter by category
    resp_tcp = client.get("/api/v1/detection/rules?category=TCP")
    assert resp_tcp.status_code == status.HTTP_200_OK
    tcp_rules = resp_tcp.json()
    assert all(r["category"] == "TCP" for r in tcp_rules)

    # Get single rule
    resp_single = client.get("/api/v1/detection/rules/NET-TCP-001")
    assert resp_single.status_code == status.HTTP_200_OK
    r_detail = resp_single.json()
    assert r_detail["rule_id"] == "NET-TCP-001"
    assert "mitre_attack_id" in r_detail


def test_api_rule_test_dry_run(client, db_session, synthetic_detection_pcap):
    """Test POST /api/v1/detection/rules/test dry-run simulation."""
    capture = Capture(
        name="Dry Run Test",
        filename="dry_run.pcap",
        storage_path=str(synthetic_detection_pcap),
        format="pcap",
        status="UPLOADED",
    )
    db_session.add(capture)
    db_session.commit()
    db_session.refresh(capture)

    pcap_parser_service.parse_and_index_capture(db_session, capture)

    payload = {
        "rule_id": "NET-TCP-001",
        "capture_id": capture.id,
    }
    resp = client.post("/api/v1/detection/rules/test", json=payload)
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert data["matches_found"] >= 1
    assert "execution_time_ms" in data

    # Verify no persistent alerts were added
    count = db_session.query(DetectionAlert).filter(DetectionAlert.capture_id == capture.id).count()
    assert count == 0

    # Cleanup
    db_session.delete(capture)
    db_session.commit()


def test_api_detection_run_and_alert_triage(client, db_session, synthetic_detection_pcap):
    """Test full workflow: Run detection -> Get Alerts -> Update Status -> Add Note."""
    # Ensure fresh state
    db_session.query(AlertNote).delete()
    db_session.query(AlertStatusHistory).delete()
    db_session.query(AlertEvidence).delete()
    db_session.query(DetectionAlert).delete()
    db_session.query(DetectionRun).delete()
    db_session.commit()

    capture = Capture(
        name="Triage Test Capture",
        filename="triage.pcap",
        storage_path=str(synthetic_detection_pcap),
        format="pcap",
        status="UPLOADED",
    )
    db_session.add(capture)
    db_session.commit()
    db_session.refresh(capture)

    pcap_parser_service.parse_and_index_capture(db_session, capture)

    # 1. Trigger detection run
    run_resp = client.post(
        "/api/v1/detection/runs",
        json={"source_type": "PCAP", "capture_id": capture.id},
    )
    assert run_resp.status_code == status.HTTP_201_CREATED
    run_data = run_resp.json()
    assert run_data["status"] == DetectionRunStatus.COMPLETED
    assert run_data["alerts_generated"] > 0
    run_id = run_data["id"]

    # 2. List alerts for this run
    alerts_resp = client.get(f"/api/v1/detection/alerts?run_id={run_id}")
    assert alerts_resp.status_code == status.HTTP_200_OK
    alerts = alerts_resp.json()
    assert len(alerts) > 0
    first_alert = alerts[0]
    alert_id = first_alert["id"]

    # 3. Get alert details with evidence
    detail_resp = client.get(f"/api/v1/detection/alerts/{alert_id}")
    assert detail_resp.status_code == status.HTTP_200_OK
    detail = detail_resp.json()
    assert len(detail["evidence"]) > 0
    assert detail["status"] == AlertStatus.NEW

    # 4. Triage alert: transition to INVESTIGATING
    patch_resp = client.patch(
        f"/api/v1/detection/alerts/{alert_id}/status",
        json={"status": AlertStatus.INVESTIGATING, "reason": "Analyst began review of SYN packet trace."},
    )
    assert patch_resp.status_code == status.HTTP_200_OK
    updated_alert = patch_resp.json()
    assert updated_alert["status"] == AlertStatus.INVESTIGATING
    assert len(updated_alert["status_history"]) >= 1

    # 5. Add analyst investigation note
    note_resp = client.post(
        f"/api/v1/detection/alerts/{alert_id}/notes",
        json={"note": "Confirmed packets originate from automated scanner test tool. Non-critical."},
    )
    assert note_resp.status_code == status.HTTP_201_CREATED
    note_data = note_resp.json()
    assert note_data["note"] == "Confirmed packets originate from automated scanner test tool. Non-critical."

    # 6. Verify alert reflects note
    refetched = client.get(f"/api/v1/detection/alerts/{alert_id}").json()
    assert len(refetched["notes"]) == 1

    # Cleanup
    db_session.query(AlertNote).delete()
    db_session.query(AlertStatusHistory).delete()
    db_session.query(AlertEvidence).delete()
    db_session.query(DetectionAlert).delete()
    db_session.query(DetectionRun).delete()
    db_session.delete(capture)
    db_session.commit()
