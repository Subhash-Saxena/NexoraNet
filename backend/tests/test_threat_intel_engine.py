"""Comprehensive test suite for Step 13 Threat Intelligence & IOC Investigation."""

import json

import pytest
from app.db.session import SessionLocal
from app.main import app
from app.models.enums import (
    IndicatorClassification,
    IndicatorRelationshipType,
    IndicatorType,
)
from app.models.user import User
from app.services.threat_intel.challenge_service import challenge_service
from app.services.threat_intel.extraction_service import extraction_service
from app.services.threat_intel.import_export_service import import_export_service
from app.services.threat_intel.indicator_service import indicator_service
from app.services.threat_intel.normalization_service import normalization_service
from app.services.threat_intel.watchlist_service import watchlist_service
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
def dev_user(db_session):
    user = db_session.query(User).filter(User.username == "student_dev").first()
    if not user:
        user = User(
            username="student_dev",
            email="student_dev@nexoranet.internal",
            hashed_password="hashed_pw_test",
            display_name="Student Developer",
            is_active=True,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
    return user


# ---------------------------------------------------------------------------
# 1. Normalization & Validation Tests
# ---------------------------------------------------------------------------
def test_normalization_ips():
    """Verify standard and defanged IP normalization."""
    # Standard IPv4
    res = normalization_service.normalize("198.51.100.25")
    assert res["indicator_type"] == IndicatorType.IP_ADDRESS.value
    assert res["normalized_value"] == "198.51.100.25"

    # Defanged IPv4
    res_defanged = normalization_service.normalize("198[.]51[.]100[.]25")
    assert res_defanged["normalized_value"] == "198.51.100.25"

    # Standard IPv6
    res_ipv6 = normalization_service.normalize("2001:0db8:0000:0000:0000:ff00:0042:8329")
    assert res_ipv6["indicator_type"] == IndicatorType.IP_ADDRESS.value
    assert res_ipv6["normalized_value"] == "2001:db8::ff00:42:8329"


def test_normalization_domains():
    """Verify domain canonicalization and defanging removal."""
    # Standard domain
    res = normalization_service.normalize("c2-controller.training.test")
    assert res["indicator_type"] == IndicatorType.DOMAIN.value
    assert res["normalized_value"] == "c2-controller.training.test"

    # Defanged domain with trailing dot and uppercase
    res_defanged = normalization_service.normalize("C2-CONTROLLER[.]TRAINING[.]TEST.")
    assert res_defanged["normalized_value"] == "c2-controller.training.test"


def test_normalization_urls():
    """Verify URL normalization, credential stripping, and defanging removal."""
    res = normalization_service.normalize("hxxp://user:pass@c2-controller.training.test:8080/path/to/beacon?query=1")
    assert res["indicator_type"] == IndicatorType.URL.value
    assert "user:pass" not in res["normalized_value"]
    assert res["normalized_value"].startswith("http://c2-controller.training.test:8080")


def test_normalization_hashes():
    """Verify hash detection and lowercase canonicalization."""
    sha256_val = "A1B2C3D4E5F67890123456789ABCDEF0123456789ABCDEF0123456789ABCDEF0"
    res = normalization_service.normalize(sha256_val)
    assert res["indicator_type"] == IndicatorType.FILE_HASH.value
    assert res["hash_type"] == "SHA256"
    assert res["normalized_value"] == sha256_val.lower()

    md5_val = "d41d8cd98f00b204e9800998ecf8427e"
    res_md5 = normalization_service.normalize(md5_val)
    assert res_md5["hash_type"] == "MD5"
    assert res_md5["normalized_value"] == md5_val


def test_normalization_emails():
    """Verify email normalization and defanging."""
    res = normalization_service.normalize("Attacker[at]Phishing-Campaign[.]training[.]test")
    assert res["indicator_type"] == IndicatorType.EMAIL_ADDRESS.value
    assert res["normalized_value"] == "attacker@phishing-campaign.training.test"


# ---------------------------------------------------------------------------
# 2. IOC Extraction Tests
# ---------------------------------------------------------------------------
def test_extraction_from_text():
    """Verify passive indicator extraction from free-form text."""
    sample_text = (
        "During triage, host contacted hxxp://c2-controller[.]training[.]test:8080/beacon. "
        "The server IP was 198.51.100.25 and malware payload hash was "
        "a1b2c3d4e5f67890123456789abcdef0123456789abcdef0123456789abcdef0. "
        "Alert sent to admin[at]corp[.]test."
    )
    extracted = extraction_service.extract_from_text(sample_text)
    types_found = {item["indicator_type"] for item in extracted}
    assert IndicatorType.IP_ADDRESS.value in types_found
    assert IndicatorType.URL.value in types_found
    assert IndicatorType.FILE_HASH.value in types_found
    assert IndicatorType.EMAIL_ADDRESS.value in types_found


# ---------------------------------------------------------------------------
# 3. Indicator Lifecycle & Enrichment Tests
# ---------------------------------------------------------------------------
def test_indicator_get_or_create_and_auto_enrich(db_session, dev_user):
    """Verify indicator creation auto-enriches against synthetic repository."""
    ind = indicator_service.get_or_create_indicator(
        db=db_session,
        raw_val="198.51.100.25",
        actor=dev_user,
    )
    assert ind.indicator_id.startswith("IOC-")
    assert ind.normalized_value == "198.51.100.25"
    assert ind.classification == "MALICIOUS"
    assert ind.confidence == "HIGH"
    assert ind.severity == "CRITICAL"
    assert ind.mitre_attack_id == "T1071.001"


def test_indicator_unknown_enrichment(db_session, dev_user):
    """Verify indicator not in repository receives UNKNOWN classification (Unknown != Benign)."""
    unknown_ip = "198.51.100.249"
    ind = indicator_service.get_or_create_indicator(
        db=db_session,
        raw_val=unknown_ip,
        actor=dev_user,
    )
    assert ind.normalized_value == unknown_ip
    assert ind.classification == "UNKNOWN"
    assert ind.confidence in ("LOW", "MEDIUM")


def test_indicator_classification_update_and_false_positive(db_session, dev_user):
    """Verify analyst can document false positive classification with required justification."""
    ind = indicator_service.get_or_create_indicator(
        db=db_session,
        raw_val="192.0.2.111",
        actor=dev_user,
    )
    updated = indicator_service.update_classification(
        db=db_session,
        indicator_id=ind.id,
        classification=IndicatorClassification.FALSE_POSITIVE,
        reason="Verified benign internal vulnerability scanner test IP.",
        actor=dev_user,
    )
    assert updated.classification == "FALSE_POSITIVE"
    assert updated.status == "FALSE_POSITIVE"
    assert updated.false_positive_reason is not None

    # Check timeline event recorded
    timeline_events = updated.timeline_events
    classified_events = [e for e in timeline_events if e.event_type == "CLASSIFIED"]
    assert len(classified_events) > 0


# ---------------------------------------------------------------------------
# 4. Watchlist Tests
# ---------------------------------------------------------------------------
def test_watchlist_lifecycle(db_session, dev_user):
    """Verify student can add, list, and remove indicators from watchlist."""
    ind = indicator_service.get_or_create_indicator(
        db=db_session,
        raw_val="203.0.113.10",
        actor=dev_user,
    )

    # Add to watchlist
    item = watchlist_service.add_to_watchlist(
        db=db_session,
        indicator_id=ind.id,
        user=dev_user,
        reason="Suspicious port scanner requires observation.",
    )
    assert item.indicator_id == ind.id
    assert watchlist_service.is_watched(db_session, ind.id, dev_user.id) is True

    # List watchlist
    items = watchlist_service.list_watchlist(db_session, user_id=dev_user.id)
    assert any(i.indicator_id == ind.id for i in items)

    # Remove from watchlist
    removed = watchlist_service.remove_from_watchlist(db_session, item.id, dev_user)
    assert removed is True
    assert watchlist_service.is_watched(db_session, ind.id, dev_user.id) is False


# ---------------------------------------------------------------------------
# 5. Relationships & Graph Tests
# ---------------------------------------------------------------------------
def test_indicator_relationships_and_graph(db_session, dev_user):
    """Verify structural linking between domain and IP, and graph assembly."""
    dom_ind = indicator_service.get_or_create_indicator(
        db=db_session,
        raw_val="test-phish-domain.training.test",
        actor=dev_user,
    )
    ip_ind = indicator_service.get_or_create_indicator(
        db=db_session,
        raw_val="198.51.100.77",
        actor=dev_user,
    )

    rel = indicator_service.add_relationship(
        db=db_session,
        source_id=dom_ind.id,
        target_id=ip_ind.id,
        rel_type=IndicatorRelationshipType.RESOLVES_TO,
        description="Phishing domain resolves to test host.",
    )
    assert rel.id is not None

    graph = indicator_service.get_indicator_graph(db_session, dom_ind.id)
    assert graph["root_indicator_id"] == dom_ind.id
    assert len(graph["nodes"]) >= 2
    assert len(graph["links"]) >= 1


# ---------------------------------------------------------------------------
# 6. Safe Import & Export Tests
# ---------------------------------------------------------------------------
def test_safe_import_json(db_session, dev_user):
    """Verify safe batch import from JSON payload."""
    payload = json.dumps([
        {"value": "198.51.100.101", "type": "IP_ADDRESS", "classification": "SUSPICIOUS"},
        {"value": "scanner-sub.training.test", "type": "DOMAIN"},
    ]).encode("utf-8")

    res = import_export_service.import_indicators(
        db=db_session,
        raw_content=payload,
        file_format="json",
        actor=dev_user,
    )
    assert res["total_records"] == 2
    assert res["imported"] == 2
    assert res["skipped"] == 0


def test_safe_import_csv_injection_sanitization(db_session, dev_user):
    """Verify CSV injection prefixes (=, +, -, @) are sanitized and stripped."""
    csv_payload = (
        b"indicator,type\n"
        b"=198.51.100.102,IP_ADDRESS\n"
        b"+badsite.training.test,DOMAIN\n"
    )

    res = import_export_service.import_indicators(
        db=db_session,
        raw_content=csv_payload,
        file_format="csv",
        actor=dev_user,
    )
    assert res["imported"] == 2


def test_export_csv_and_json(db_session):
    """Verify safe export with CSV formula injection neutralization."""
    csv_content, media_type = import_export_service.export_indicators(db_session, file_format="csv")
    assert media_type == "text/csv"
    assert "indicator_id" in csv_content

    json_content, json_media = import_export_service.export_indicators(db_session, file_format="json")
    assert json_media == "application/json"
    parsed = json.loads(json_content)
    assert "indicators" in parsed


# ---------------------------------------------------------------------------
# 7. Threat Intelligence Challenge & Rubric Evaluation Tests
# ---------------------------------------------------------------------------
def test_challenge_rubric_evaluation(db_session, dev_user):
    """Verify student submission evaluation against the 5-criteria rubric."""
    attempt = challenge_service.evaluate_attempt(
        db=db_session,
        slug="c2-ip-attribution",
        user=dev_user,
        selected_classification="MALICIOUS",
        hypothesis_text="External source reliability is high and synthetic threat feed confirms this C2 IP beaconing.",
        evidence_notes="Workstation communicates on port 8080 every 60s. Correlated with HTTP POST alert in PCAP.",
        conclusion="Recommend adding IP to perimeter watchlist and escalating to Tier 2 for host containment.",
    )
    assert attempt.score >= 70.0
    assert attempt.passed is True

    feedback = json.loads(attempt.feedback)
    assert feedback["total_score"] >= 70.0
    assert "ioc_classification" in feedback["breakdown"]
    assert "evidence_review" in feedback["breakdown"]
    assert "threat_intel_interpretation" in feedback["breakdown"]
    assert "correlation_context" in feedback["breakdown"]
    assert "soc_conclusion" in feedback["breakdown"]


# ---------------------------------------------------------------------------
# 8. API Endpoints Integration Tests
# ---------------------------------------------------------------------------
def test_api_overview(client):
    """Verify GET /api/v1/threat-intel/overview endpoint."""
    response = client.get("/api/v1/threat-intel/overview")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "total_indicators" in data
    assert "by_classification" in data
    assert "by_type" in data
    assert "active_watchlists" in data


def test_api_indicators_list_and_filter(client):
    """Verify GET /api/v1/threat-intel/indicators endpoint with filtering."""
    response = client.get("/api/v1/threat-intel/indicators?classification=MALICIOUS")
    assert response.status_code == status.HTTP_200_OK
    items = response.json()
    assert isinstance(items, list)
    for it in items:
        assert it["classification"] == "MALICIOUS"


def test_api_indicator_detail_and_notes(client):
    """Verify GET /api/v1/threat-intel/indicators/{id} and note addition."""
    # List to find an indicator
    list_res = client.get("/api/v1/threat-intel/indicators?limit=1")
    assert list_res.status_code == status.HTTP_200_OK
    indicators = list_res.json()
    assert len(indicators) > 0
    ind_id = indicators[0]["id"]

    # Get detail
    detail_res = client.get(f"/api/v1/threat-intel/indicators/{ind_id}")
    assert detail_res.status_code == status.HTTP_200_OK
    data = detail_res.json()
    assert data["id"] == ind_id

    # Add Note
    note_res = client.post(
        f"/api/v1/threat-intel/indicators/{ind_id}/notes",
        json={"note": "Investigated during scheduled training lab."},
    )
    assert note_res.status_code == status.HTTP_201_CREATED
    assert note_res.json()["note"] == "Investigated during scheduled training lab."


def test_api_challenges(client):
    """Verify GET /api/v1/threat-intel/challenges and submit attempt."""
    res = client.get("/api/v1/threat-intel/challenges")
    assert res.status_code == status.HTTP_200_OK
    challenges = res.json()
    assert len(challenges) >= 5

    # Get detail
    detail_res = client.get("/api/v1/threat-intel/challenges/c2-ip-attribution")
    assert detail_res.status_code == status.HTTP_200_OK
    assert detail_res.json()["slug"] == "c2-ip-attribution"

    # Submit attempt via API
    sub_res = client.post(
        "/api/v1/threat-intel/challenges/c2-ip-attribution/submit",
        json={
            "selected_classification": "MALICIOUS",
            "hypothesis_text": "Strong intelligence confidence matches known C2 server behavior.",
            "evidence_notes": "Continuous beaconing traffic on port 8080 identified in packet capture.",
            "conclusion": "Block communication at perimeter firewall and alert SOC Tier-2 team.",
        },
    )
    assert sub_res.status_code == status.HTTP_200_OK
    att_data = sub_res.json()
    assert att_data["passed"] is True
    assert att_data["score"] >= 70.0
