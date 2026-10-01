"""Comprehensive test suite for Step 15 SIEM & Security Log Analysis Engine."""


import pytest
from app.db.session import SessionLocal
from app.main import app
from app.models.enums import SecurityEventCategory, SecurityEventSeverity
from app.models.siem import (
    SecurityEvent,
    SecurityLogDataset,
)
from app.services.siem.dataset_service import SiemDatasetService
from app.services.siem.ingestion_service import LogIngestionService
from app.services.siem.normalization_service import LogNormalizationService
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
def ensure_siem_data(db_session: Session):
    """Ensure SIEM sources, datasets, and rules exist before each test."""
    ds = db_session.execute(select(SecurityLogDataset)).first()
    if not ds:
        SiemDatasetService.seed_all_siem_data(db_session)


def test_list_log_sources():
    """Verify log sources endpoint returns registered synthetic sources."""
    resp = client.get("/api/v1/siem/sources")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 7
    source_types = [s["source_type"] for s in data]
    assert "WINDOWS_SECURITY" in source_types
    assert "FIREWALL" in source_types
    assert "DNS" in source_types
    assert "WEB_SERVER" in source_types


def test_list_datasets():
    """Verify datasets endpoint returns beginner, intermediate, and advanced datasets."""
    resp = client.get("/api/v1/siem/datasets")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 3
    stable_ids = [d["stable_id"] for d in data]
    assert "DS-AUTH-BEG-01" in stable_ids
    assert "DS-NET-INT-01" in stable_ids
    assert "DS-SOC-ADV-01" in stable_ids


def test_log_normalization_windows_xml():
    """Verify normalization of Windows Event XML for logon success and failure."""
    # Event 4624 - Success
    raw_4624 = "<Event><System><EventID>4624</EventID><Computer>DC01.corp.test</Computer></System><EventData><Data Name='TargetUserName'>alice.smith</Data><Data Name='IpAddress'>192.0.2.55</Data></EventData></Event>"
    norm_4624 = LogNormalizationService.normalize(raw_4624, log_format="WINDOWS_EVENT_XML")
    assert norm_4624["event_category"] == SecurityEventCategory.AUTHENTICATION.value
    assert norm_4624["action"] == "LOGIN"
    assert norm_4624["status"] == "SUCCESS"
    assert norm_4624["username"] == "alice.smith"
    assert norm_4624["source_ip"] == "192.0.2.55"

    # Event 4625 - Failure
    raw_4625 = "<Event><System><EventID>4625</EventID><Computer>DC01.corp.test</Computer></System><EventData><Data Name='TargetUserName'>bad_actor</Data><Data Name='IpAddress'>198.51.100.99</Data></EventData></Event>"
    norm_4625 = LogNormalizationService.normalize(raw_4625, log_format="WINDOWS_EVENT_XML")
    assert norm_4625["action"] == "LOGIN_FAILURE"
    assert norm_4625["status"] == "FAILURE"
    assert norm_4625["username"] == "bad_actor"
    assert norm_4625["severity"] == SecurityEventSeverity.LOW.value


def test_log_normalization_syslog_and_cef():
    """Verify normalization of Linux syslog and ArcSight CEF formats."""
    # Syslog SSH failure
    raw_syslog = "Sep 30 14:00:00 server01 sshd[1234]: Failed password for invalid user admin from 192.0.2.105 port 54321 ssh2"
    norm_sys = LogNormalizationService.normalize(raw_syslog, log_format="SYSLOG")
    assert norm_sys["action"] == "LOGIN_FAILURE"
    assert norm_sys["username"] == "admin"
    assert norm_sys["source_ip"] == "192.0.2.105"
    assert norm_sys["source_port"] == 54321

    # CEF Format
    raw_cef = "CEF:0|Cisco|ASA|9.1|106023|Deny Inbound TCP|7|src=198.51.100.22 dst=192.0.2.10 spt=51234 dpt=445 proto=TCP act=DROP"
    norm_cef = LogNormalizationService.normalize(raw_cef, log_format="CEF_LIKE")
    assert norm_cef["source_ip"] == "198.51.100.22"
    assert norm_cef["destination_ip"] == "192.0.2.10"
    assert norm_cef["destination_port"] == 445
    assert norm_cef["severity"] == SecurityEventSeverity.HIGH.value
    assert norm_cef["action"] == "CONNECTION_BLOCKED"


def test_ingestion_service_csv_sanitization(db_session: Session):
    """Verify ingestion service neutralizes CSV spreadsheet formula injection prefixes."""
    ds = db_session.execute(select(SecurityLogDataset)).scalars().first()
    assert ds is not None

    csv_payload = """timestamp,host,username,source_ip,destination_ip,dst_port,protocol,action,message
2026-09-30T10:00:00Z,DC01,=cmd|' /C calc'!A0,192.0.2.1,192.0.2.2,80,TCP,LOGIN,+calc execution attempt
"""
    result = LogIngestionService.ingest_payload(
        db=db_session,
        dataset_id=ds.id,
        content=csv_payload,
        format_hint="CSV",
    )
    assert result["imported_events"] == 1

    # Verify injected formula is prefixed with quote
    ev = db_session.execute(
        select(SecurityEvent).where(SecurityEvent.dataset_id == ds.id).order_by(SecurityEvent.id.desc())
    ).scalars().first()
    assert ev is not None
    assert ev.username.startswith("'=")
    assert ev.message.startswith("'+")


def test_ingestion_limits(db_session: Session):
    """Verify ingestion rejects oversized content exceeding safety limits."""
    ds = db_session.execute(select(SecurityLogDataset)).scalars().first()
    assert ds is not None

    oversized = "A" * (6 * 1024 * 1024)  # 6 MB (limit is 5 MB)
    with pytest.raises(ValueError, match="exceeds maximum allowable limit"):
        LogIngestionService.ingest_payload(
            db=db_session,
            dataset_id=ds.id,
            content=oversized,
            format_hint="JSON",
        )


def test_siem_search_conditions_and_filters():
    """Verify SIEM visual query builder search with conditions and quick filters."""
    # 1. Search login failures
    payload = {
        "conditions": [{"field": "action", "operator": "=", "value": "LOGIN_FAILURE"}],
        "logical_op": "AND",
        "limit": 10,
    }
    resp = client.post("/api/v1/siem/search", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] > 0
    for ev in data["events"]:
        assert ev["action"] == "LOGIN_FAILURE"

    # 2. Quick filter: FIREWALL_BLOCKS
    payload_qf = {
        "quick_filter": "FIREWALL_BLOCKS",
        "limit": 10,
    }
    resp_qf = client.post("/api/v1/siem/search", json=payload_qf)
    assert resp_qf.status_code == 200
    data_qf = resp_qf.json()
    assert data_qf["total"] > 0
    for ev in data_qf["events"]:
        assert ev["action"] == "CONNECTION_BLOCKED"


def test_siem_search_fulltext_and_logic():
    """Verify search keyword queries and logical operations."""
    payload = {
        "search_text": "corp.test",
        "logical_op": "AND",
        "limit": 15,
    }
    resp = client.post("/api/v1/siem/search", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] > 0
    assert "text CONTAINS" in data["human_readable"]


def test_siem_dashboard_aggregations():
    """Verify SIEM overview aggregations and time series buckets."""
    resp = client.get("/api/v1/siem/overview")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_events"] > 0
    assert "by_severity" in data
    assert "by_source_type" in data
    assert "top_source_ips" in data
    assert "timeline" in data
    assert len(data["timeline"]) > 0


def test_correlation_rules_and_alerts():
    """Verify correlation rules listing, testing, and alert retrieval."""
    # List rules
    resp = client.get("/api/v1/siem/rules")
    assert resp.status_code == 200
    rules = resp.json()
    assert len(rules) >= 9

    # List alerts
    resp_alerts = client.get("/api/v1/siem/correlations")
    assert resp_alerts.status_code == 200
    alerts = resp_alerts.json()
    assert len(alerts) > 0
    first_alert = alerts[0]
    assert first_alert["alert_id"].startswith("CORR-")

    # Fetch alert detail
    resp_detail = client.get(f"/api/v1/siem/correlations/{first_alert['id']}")
    assert resp_detail.status_code == 200
    assert resp_detail.json()["alert_id"] == first_alert["alert_id"]


def test_saved_searches_crud():
    """Verify creating, listing, updating, and deleting saved searches."""
    # Create
    create_payload = {
        "name": "Test Saved Search Auth",
        "description": "Custom query for auth failures",
        "query_definition": {"action": "LOGIN_FAILURE"},
        "is_public": True,
    }
    resp = client.post("/api/v1/siem/search/saved", json=create_payload)
    assert resp.status_code == 201
    saved_data = resp.json()
    saved_id = saved_data["id"]

    # List
    list_resp = client.get("/api/v1/siem/search/saved")
    assert list_resp.status_code == 200
    ids = [s["id"] for s in list_resp.json()]
    assert saved_id in ids

    # Update
    update_resp = client.patch(f"/api/v1/siem/search/saved/{saved_id}", json={"name": "Updated Search Name"})
    assert update_resp.status_code == 200
    assert update_resp.json()["name"] == "Updated Search Name"

    # Delete
    del_resp = client.delete(f"/api/v1/siem/search/saved/{saved_id}")
    assert del_resp.status_code == 200


def test_event_details_and_related():
    """Verify fetching event detail with raw log message and related events."""
    # Find an event
    search_resp = client.post("/api/v1/siem/search", json={"limit": 1})
    event_id = search_resp.json()["events"][0]["event_id"]

    # Detail
    detail_resp = client.get(f"/api/v1/siem/events/{event_id}")
    assert detail_resp.status_code == 200
    d = detail_resp.json()
    assert d["event_id"] == event_id

    # Related
    rel_resp = client.get(f"/api/v1/siem/events/{event_id}/related")
    assert rel_resp.status_code == 200
    assert isinstance(rel_resp.json(), list)


def test_siem_to_soc_investigation():
    """Verify escalating a SIEM event to a Step 12 SOC Investigation."""
    search_resp = client.post("/api/v1/siem/search", json={"limit": 1})
    event_id = search_resp.json()["events"][0]["event_id"]

    resp = client.post(f"/api/v1/siem/events/{event_id}/investigate", json={})
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "SUCCESS"
    assert data["investigation_code"].startswith("INV-")
    assert "/soc/investigations/" in data["redirect_url"]


def test_siem_to_threat_hunt():
    """Verify launching a Step 14 Threat Hunt from a SIEM event."""
    search_resp = client.post("/api/v1/siem/search", json={"limit": 1})
    event_id = search_resp.json()["events"][0]["event_id"]

    resp = client.post(
        f"/api/v1/siem/events/{event_id}/start-hunt",
        json={"hypothesis_statement": "Suspected lateral movement originating from this host."},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "SUCCESS"
    assert data["hunt_code"].startswith("HUNT-")
    assert "/threat-hunting/hunts/" in data["redirect_url"]


def test_siem_to_threat_intel_ioc_extraction():
    """Verify extracting candidate IOCs from a SIEM event into Step 13 Threat Intel."""
    search_resp = client.post(
        "/api/v1/siem/search",
        json={"conditions": [{"field": "domain", "operator": "!=", "value": ""}], "limit": 1},
    )
    events = search_resp.json()["events"]
    assert len(events) > 0
    event_id = events[0]["event_id"]

    resp = client.post(f"/api/v1/siem/events/{event_id}/extract-ioc")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "SUCCESS"
    assert len(data["extracted_iocs"]) > 0


def test_siem_labs_and_validation():
    """Verify listing SIEM training labs and validating student query submissions."""
    resp = client.get("/api/v1/siem/labs")
    assert resp.status_code == 200
    labs = resp.json()
    assert len(labs) >= 8

    # Validate Lab 1 submission
    val_payload = {
        "executed_query": {"conditions": [{"field": "action", "operator": "=", "value": "LOGIN_FAILURE"}]},
        "identified_entity": "198.51.100.45",
        "findings_notes": "Observed multiple consecutive failed logins from external IP 198.51.100.45.",
    }
    val_resp = client.post("/api/v1/siem/labs/lab-siem-find-failed-logins/validate", json=val_payload)
    assert val_resp.status_code == 200
    v = val_resp.json()
    assert v["success"] is True
    assert v["score"] >= 70
    assert v["criteria"]["query_executed"] is True
    assert v["criteria"]["entity_identified"] is True
