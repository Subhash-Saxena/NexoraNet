"""Comprehensive test suite for Step 14 Threat Hunting & Investigation Workspace."""


import pytest
from app.db.session import SessionLocal
from app.main import app
from app.models.enums import (
    HuntConfidence,
    HuntDifficulty,
    HuntEvidenceRelevance,
    HuntEvidenceType,
    HuntFindingType,
    HuntHypothesisStatus,
    HuntStatus,
)
from app.models.threat_hunting import (
    HuntDataset,
)
from app.models.user import User
from app.services.threat_hunting import (
    HuntDatasetService,
    HuntInvestigationService,
    HuntQueryEngine,
    HuntScenarioService,
    HuntScoringService,
    ThreatHuntService,
)
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
def test_user(db_session):
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
# 1. Query Engine Unit Tests & Security Guardrails
# ---------------------------------------------------------------------------
def test_query_engine_text_parsing():
    """Verify parsing simple query strings into structured condition objects."""
    q_str = 'protocol == "DNS" AND destination_port == 53'
    conditions = HuntQueryEngine.parse_text_query(q_str)
    assert len(conditions) == 2
    assert conditions[0]["field"] == "protocol"
    assert conditions[0]["operator"] == "=="
    assert conditions[0]["value"] == "DNS"
    assert conditions[1]["field"] == "destination_port"
    assert conditions[1]["operator"] == "=="
    assert conditions[1]["value"] == 53


def test_query_engine_field_whitelist_rejection():
    """Verify rejection of unwhitelisted and malicious injection fields."""
    with pytest.raises(ValueError, match="Field 'drop_table' is not queryable"):
        HuntQueryEngine.get_column("drop_table")

    with pytest.raises(ValueError, match="Invalid field"):
        HuntQueryEngine.build_filter_clause({"field": "malicious_injection;--", "operator": "==", "value": "test"})


def test_query_engine_execution(db_session):
    """Verify parameterized query execution across HuntEvent records."""
    # Find or verify a seeded dataset
    ds = db_session.query(HuntDataset).first()
    assert ds is not None

    res = HuntQueryEngine.execute_hunt_query(
        db=db_session,
        dataset_id=ds.id,
        conditions=[{"field": "protocol", "operator": "is_not_null", "value": None}],
        limit=10,
    )
    assert "events" in res
    assert "took_ms" in res
    assert res["took_ms"] >= 0
    assert "explanation" in res


# ---------------------------------------------------------------------------
# 2. Dataset Service Tests
# ---------------------------------------------------------------------------
def test_dataset_listing_and_analytics(db_session):
    """Verify dataset enumeration and aggregated telemetry metrics."""
    datasets = HuntDatasetService.list_datasets(db_session)
    assert len(datasets) >= 1

    ds = datasets[0]
    analytics = HuntDatasetService.get_dataset_analytics(db_session, ds.id)
    assert analytics["dataset_id"] == ds.id
    assert "protocols" in analytics
    assert "top_source_ips" in analytics
    assert "time_range" in analytics


# ---------------------------------------------------------------------------
# 3. Hunt Lifecycle & Sequential ID Tests
# ---------------------------------------------------------------------------
def test_hunt_lifecycle_and_id_generation(db_session, test_user):
    """Verify sequential ID generation, start, pause, and completion transitions."""
    hunt_id_str = ThreatHuntService.generate_hunt_id(db_session)
    assert hunt_id_str.startswith("HUNT-")

    hunt = ThreatHuntService.create_hunt(
        db=db_session,
        user_id=test_user.id,
        title="Test Lifecycle Hunt",
        description="Testing hunt status transitions",
        objective="Verify state machine integrity",
        difficulty=HuntDifficulty.BEGINNER.value,
    )
    assert hunt.status == HuntStatus.READY.value
    assert hunt.hunt_id.startswith("HUNT-")

    # Start hunt
    started = ThreatHuntService.start_hunt(db_session, hunt.id)
    assert started.status == HuntStatus.RUNNING.value
    assert started.started_at is not None

    # Pause hunt
    paused = ThreatHuntService.pause_hunt(db_session, hunt.id)
    assert paused.status == HuntStatus.PAUSED.value

    # Complete hunt
    completed = ThreatHuntService.complete_hunt(
        db_session,
        hunt.id,
        conclusion="Host demonstrated clear exfiltration pattern.",
        conclusion_disposition="SUPPORTED",
    )
    assert completed.status == HuntStatus.COMPLETED.value
    assert completed.completed_at is not None
    assert completed.conclusion_disposition == "SUPPORTED"


# ---------------------------------------------------------------------------
# 4. Timeline & Entity Relationship Graph Tests
# ---------------------------------------------------------------------------
def test_hunt_timeline_and_graph(db_session, test_user):
    """Verify timeline bucketing and bounded entity graph generation."""
    ds = db_session.query(HuntDataset).filter(HuntDataset.event_count > 0).first()
    assert ds is not None

    hunt = ThreatHuntService.create_hunt(
        db=db_session,
        user_id=test_user.id,
        title="Timeline & Graph Test Hunt",
        description="Verifying graph generator",
        objective="Check bounded graph traversal",
        dataset_id=ds.id,
    )

    timeline = ThreatHuntService.build_hunt_timeline(db_session, hunt, interval="minute")
    assert "buckets" in timeline
    assert "total_events" in timeline

    graph = ThreatHuntService.build_entity_graph(db_session, hunt, max_depth=2, max_nodes=25)
    assert "nodes" in graph
    assert "edges" in graph
    assert len(graph["nodes"]) <= 25


def test_hunt_pivoting(db_session, test_user):
    """Verify entity correlation across events, alerts, and indicators."""
    hunt = ThreatHuntService.create_hunt(
        db=db_session,
        user_id=test_user.id,
        title="Pivot Test Hunt",
        description="Verifying pivot correlation",
        objective="Check IP pivot results",
    )
    pivot_res = ThreatHuntService.pivot_entity(db_session, hunt, "IP", "192.168.1.105")
    assert pivot_res["entity_type"] == "IP"
    assert pivot_res["entity_value"] == "192.168.1.105"
    assert "suggested_questions" in pivot_res
    assert len(pivot_res["suggested_questions"]) >= 2


# ---------------------------------------------------------------------------
# 5. Scientific Investigation Workflow (Hypothesis, Evidence, Findings, Notes)
# ---------------------------------------------------------------------------
def test_investigation_workflow(db_session, test_user):
    """Verify hypotheses, evidence collection, findings, and journal notes."""
    hunt = ThreatHuntService.create_hunt(
        db=db_session,
        user_id=test_user.id,
        title="Investigation Workflow Hunt",
        description="Validating investigation workflow",
        objective="Test hypotheses and evidence linking",
    )

    # 1. Hypotheses
    hyp = HuntInvestigationService.create_hypothesis(
        db=db_session,
        hunt_id=hunt.id,
        title="Suspicious DNS Tunneling in Subnet",
        description="Testing if high query volumes represent tunneling.",
        confidence=HuntConfidence.HIGH.value,
    )
    assert hyp.id is not None
    assert hyp.status == HuntHypothesisStatus.OPEN.value

    updated_hyp = HuntInvestigationService.update_hypothesis(
        db=db_session,
        hypothesis_id=hyp.id,
        status=HuntHypothesisStatus.SUPPORTED.value,
        analyst_reasoning="Confirmed base64-encoded TXT records.",
    )
    assert updated_hyp.status == HuntHypothesisStatus.SUPPORTED.value

    # 2. Evidence
    ev = HuntInvestigationService.add_evidence(
        db=db_session,
        hunt_id=hunt.id,
        evidence_type=HuntEvidenceType.DNS_EVENT.value,
        source_id="EVT-001",
        description="High entropy DNS query observed.",
        hypothesis_id=hyp.id,
        relevance=HuntEvidenceRelevance.SUPPORTING.value,
        analyst_note="Decodes to secret payload chunk.",
    )
    assert ev.id is not None
    assert ev.hypothesis_id == hyp.id

    evidence_list = HuntInvestigationService.list_evidence(db_session, hunt.id)
    assert len(evidence_list) == 1

    # 3. Findings
    finding = HuntInvestigationService.create_finding(
        db=db_session,
        hunt_id=hunt.id,
        title="Unrestricted Outbound UDP/53",
        description="Perimeter firewall allows direct queries to arbitrary external nameservers.",
        finding_type=HuntFindingType.DETECTION_GAP.value,
        confidence=HuntConfidence.HIGH.value,
        mitigation_recommendation="Implement firewall rule allowing outbound port 53 exclusively from internal resolvers.",
    )
    assert finding.id is not None
    findings_list = HuntInvestigationService.list_findings(db_session, hunt.id)
    assert len(findings_list) == 1

    # 4. Notes
    note = HuntInvestigationService.add_note(
        db=db_session,
        hunt_id=hunt.id,
        user_id=test_user.id,
        author_name=test_user.username,
        content="Pivoted on destination IP 198.51.100.53; matched external test sinkhole.",
    )
    assert note.id is not None
    notes_list = HuntInvestigationService.list_notes(db_session, hunt.id)
    assert len(notes_list) == 1


# ---------------------------------------------------------------------------
# 6. Scoring Rubric Evaluation Tests
# ---------------------------------------------------------------------------
def test_hunt_scoring_evaluation(db_session, test_user):
    """Verify 5-dimension educational rubric evaluation and grade assignment."""
    hunt = ThreatHuntService.create_hunt(
        db=db_session,
        user_id=test_user.id,
        title="Scoring Test Hunt",
        description="Testing scoring evaluation",
        objective="Achieve passing grade with structured workflow",
        initial_pivot_type="DOMAIN",
        initial_pivot_value="corp-sync.test",
    )

    # Formulate hypotheses
    h1 = HuntInvestigationService.create_hypothesis(
        db_session, hunt.id, "Active DNS exfiltration", "Testing DNS anomalies"
    )
    HuntInvestigationService.update_hypothesis(
        db_session, h1.id, status="SUPPORTED", analyst_reasoning="Confirmed encoded TXT chunks."
    )
    h2 = HuntInvestigationService.create_hypothesis(
        db_session, hunt.id, "Benign vendor traffic", "Testing authorization"
    )
    HuntInvestigationService.update_hypothesis(
        db_session, h2.id, status="NOT_SUPPORTED", analyst_reasoning="Unregistered domain."
    )

    # Add evidence
    for idx in range(4):
        HuntInvestigationService.add_evidence(
            db=db_session,
            hunt_id=hunt.id,
            evidence_type=HuntEvidenceType.EVENT.value,
            source_id=f"EVT-SCORE-{idx}",
            description=f"Evidence artifact #{idx}",
            hypothesis_id=h1.id,
            relevance="SUPPORTING" if idx < 3 else "CONTRADICTING",
            analyst_note="Corroborated via packet inspection.",
        )

    # Add findings and notes
    HuntInvestigationService.create_finding(
        db=db_session,
        hunt_id=hunt.id,
        title="DNS Tunneling Egress",
        description="Covert channel detected.",
        finding_type="ANOMALY",
        mitigation_recommendation="Block outbound UDP/53 at firewall.",
    )
    for n_idx in range(3):
        HuntInvestigationService.add_note(
            db=db_session,
            hunt_id=hunt.id,
            user_id=test_user.id,
            author_name="Analyst",
            content=f"Detailed analytical note #{n_idx} documenting pivot behavior.",
        )

    # Log query history
    for q in ['protocol == "DNS"', 'domain contains "corp-sync.test"', 'source_ip == "192.168.1.105"']:
        ThreatHuntService.log_query(db_session, hunt.id, q)

    # Complete hunt
    ThreatHuntService.complete_hunt(
        db_session,
        hunt.id,
        conclusion="Host 192.168.1.105 successfully established a covert DNS tunneling channel exfiltrating sensitive chunks to corp-sync.test.",
        conclusion_disposition="SUPPORTED",
    )

    eval_result = HuntScoringService.evaluate_hunt(db_session, hunt)
    assert eval_result["total_score"] >= 80.0
    assert eval_result["grade"] in ("A", "B")
    assert "evidence_quality" in eval_result["breakdown"]
    assert "hypothesis_testing" in eval_result["breakdown"]


# ---------------------------------------------------------------------------
# 7. Training Scenarios Catalog & Launch Tests
# ---------------------------------------------------------------------------
def test_scenarios_catalog_and_launch(db_session, test_user):
    """Verify listing 8 scenarios and launching a pre-configured hunt."""
    scenarios = HuntScenarioService.list_scenarios()
    assert len(scenarios) == 8

    # Filter by difficulty
    beginner_scenarios = HuntScenarioService.list_scenarios(difficulty="BEGINNER")
    assert len(beginner_scenarios) >= 3

    # Launch scenario
    slug = "dns-exfiltration-tunneling"
    hunt = HuntScenarioService.launch_scenario(db_session, test_user.id, slug)
    assert hunt is not None
    assert hunt.scenario_slug == slug
    assert hunt.initial_pivot_value == "corp-sync.test"


# ---------------------------------------------------------------------------
# 8. REST API Endpoints Integration Tests
# ---------------------------------------------------------------------------
def test_api_overview(client):
    """Verify GET /api/v1/threat-hunting/overview."""
    res = client.get("/api/v1/threat-hunting/overview")
    assert res.status_code == status.HTTP_200_OK
    data = res.json()
    assert "total_hunts" in data
    assert "total_datasets" in data
    assert "total_scenarios" in data
    assert data["total_scenarios"] == 8


def test_api_datasets_and_analytics(client):
    """Verify GET /api/v1/threat-hunting/datasets and detail."""
    res = client.get("/api/v1/threat-hunting/datasets")
    assert res.status_code == status.HTTP_200_OK
    datasets = res.json()
    assert len(datasets) >= 1

    ds_id = datasets[0]["id"]
    detail_res = client.get(f"/api/v1/threat-hunting/datasets/{ds_id}")
    assert detail_res.status_code == status.HTTP_200_OK
    detail_data = detail_res.json()
    assert detail_data["dataset_id"] == ds_id


def test_api_scenarios_and_launch(client):
    """Verify GET /api/v1/threat-hunting/scenarios and POST launch."""
    res = client.get("/api/v1/threat-hunting/scenarios")
    assert res.status_code == status.HTTP_200_OK
    assert len(res.json()) == 8

    launch_res = client.post("/api/v1/threat-hunting/scenarios/c2-beaconing-investigation/launch")
    assert launch_res.status_code == status.HTTP_201_CREATED
    data = launch_res.json()
    assert data["scenario_slug"] == "c2-beaconing-investigation"
    assert data["hunt_id"].startswith("HUNT-")


def test_api_hunt_query_and_investigation_lifecycle(client):
    """Verify complete investigation API workflow."""
    # 1. Create Hunt
    create_res = client.post(
        "/api/v1/threat-hunting/hunts",
        json={
            "title": "API Test Hunt",
            "description": "API investigation test",
            "objective": "Verify endpoints",
            "difficulty": "BEGINNER",
        },
    )
    assert create_res.status_code == status.HTTP_201_CREATED
    hunt_data = create_res.json()
    hunt_id = hunt_data["id"]

    # 2. Start Hunt
    start_res = client.post(f"/api/v1/threat-hunting/hunts/{hunt_id}/start")
    assert start_res.status_code == status.HTTP_200_OK
    assert start_res.json()["status"] == "RUNNING"

    # 3. Execute Query
    query_res = client.post(
        f"/api/v1/threat-hunting/hunts/{hunt_id}/query",
        json={"search_text": "DNS", "limit": 10},
    )
    assert query_res.status_code == status.HTTP_200_OK
    assert "events" in query_res.json()

    # 4. Formulate Hypothesis
    hyp_res = client.post(
        f"/api/v1/threat-hunting/hunts/{hunt_id}/hypotheses",
        json={
            "title": "Adversary beaconing active",
            "description": "HTTPS jitter polling detected",
            "confidence": "HIGH",
        },
    )
    assert hyp_res.status_code == status.HTTP_201_CREATED
    hyp_id = hyp_res.json()["id"]

    # 5. Add Evidence
    ev_res = client.post(
        f"/api/v1/threat-hunting/hunts/{hunt_id}/evidence",
        json={
            "hypothesis_id": hyp_id,
            "evidence_type": "EVENT",
            "source_id": "EVT-TEST-001",
            "description": "Repeated outbound beaconing",
            "relevance": "SUPPORTING",
            "analyst_note": "Delta variance under 3 seconds",
        },
    )
    assert ev_res.status_code == status.HTTP_201_CREATED

    # 6. Add Finding
    finding_res = client.post(
        f"/api/v1/threat-hunting/hunts/{hunt_id}/findings",
        json={
            "title": "C2 Channel Established",
            "description": "Host communicating with external malicious server.",
            "finding_type": "ANOMALY",
            "confidence": "HIGH",
            "mitigation_recommendation": "Isolate host and block domain.",
        },
    )
    assert finding_res.status_code == status.HTTP_201_CREATED

    # 7. Add Note
    note_res = client.post(
        f"/api/v1/threat-hunting/hunts/{hunt_id}/notes",
        json={"content": "Analyzed jitter frequency across TLS packets."},
    )
    assert note_res.status_code == status.HTTP_201_CREATED

    # 8. Submit Conclusion
    conc_res = client.post(
        f"/api/v1/threat-hunting/hunts/{hunt_id}/conclusion",
        json={
            "conclusion": "Telemetry confirms periodic beaconing to C2 infrastructure. Host requires immediate remediation.",
            "conclusion_disposition": "SUPPORTED",
        },
    )
    assert conc_res.status_code == status.HTTP_200_OK
    score_data = conc_res.json()
    assert "total_score" in score_data
    assert "grade" in score_data
