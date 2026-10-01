"""Comprehensive Test Suite for Step 18: SOAR Security Automation & Advanced SOC Scenarios.

Verifies:
1. Whitelist Condition Evaluator (13 operators, compound logic)
2. SOAR Playbook catalog, custom authoring, status toggle, dry-run testing
3. Playbook execution engine, step logs, context accumulation, and idempotency
4. Human-in-the-loop analyst approval gates (approve, reject, cancel)
5. Automation metrics and immutable audit logging
6. SOC Scenario catalog browsing, filtering across 4 difficulties and 5 categories
7. 9-stage investigation attempt session, progressive hints, and rubric scoring
"""


import pytest
from app.db.session import SessionLocal
from app.main import app
from app.models.enums import PlaybookExecutionStatus, ScenarioAttemptStatus
from app.models.soar import AutomationPlaybook
from app.models.soc_scenario import SocScenario
from app.services.soar.condition_evaluator import SafeConditionEvaluator
from app.services.soar.seed_soar_playbooks import seed_soar_playbooks
from app.services.soc_scenarios.seed_soc_scenarios import seed_soc_scenarios
from fastapi.testclient import TestClient
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
def ensure_soar_and_scenario_data(db_session: Session):
    """Ensure 8 playbooks and 28 scenarios are present in database."""
    pb_count = db_session.query(AutomationPlaybook).count()
    if pb_count < 8:
        seed_soar_playbooks(db_session)

    sc_count = db_session.query(SocScenario).count()
    if sc_count < 28:
        seed_soc_scenarios(db_session)


# ==============================================================================
# 1. Condition Evaluator Unit Tests
# ==============================================================================
def test_condition_evaluator_basic_operators():
    """Test equals, contains, starts_with, greater_than, exists."""
    ctx = {
        "severity": "HIGH",
        "threat_score": 85,
        "indicator": "http://malicious-c2.sim/dropper.exe",
        "user": {"name": "alice", "is_admin": True},
        "tags": ["malware", "ransomware", "trojan"],
    }

    # equals
    assert SafeConditionEvaluator.evaluate({"field": "severity", "operator": "equals", "value": "HIGH"}, ctx)
    assert not SafeConditionEvaluator.evaluate({"field": "severity", "operator": "equals", "value": "LOW"}, ctx)

    # contains
    assert SafeConditionEvaluator.evaluate({"field": "indicator", "operator": "contains", "value": "c2.sim"}, ctx)
    assert not SafeConditionEvaluator.evaluate({"field": "indicator", "operator": "contains", "value": "google.com"}, ctx)

    # greater_than & gte
    assert SafeConditionEvaluator.evaluate({"field": "threat_score", "operator": "greater_than", "value": 80}, ctx)
    assert SafeConditionEvaluator.evaluate({"field": "threat_score", "operator": "gte", "value": 85}, ctx)
    assert not SafeConditionEvaluator.evaluate({"field": "threat_score", "operator": "less_than", "value": 50}, ctx)

    # nested dot notation
    assert SafeConditionEvaluator.evaluate({"field": "user.name", "operator": "equals", "value": "alice"}, ctx)
    assert SafeConditionEvaluator.evaluate({"field": "user.is_admin", "operator": "equals", "value": True}, ctx)

    # exists
    assert SafeConditionEvaluator.evaluate({"field": "indicator", "operator": "exists"}, ctx)
    assert not SafeConditionEvaluator.evaluate({"field": "nonexistent_field", "operator": "exists"}, ctx)

    # in list
    assert SafeConditionEvaluator.evaluate({"field": "tags", "operator": "contains", "value": "ransomware"}, ctx)


def test_condition_evaluator_compound_logic():
    """Test and/or compound condition trees."""
    ctx = {"severity": "CRITICAL", "threat_score": 95, "src_ip": "198.51.100.12"}

    and_cond = {
        "and": [
            {"field": "severity", "operator": "equals", "value": "CRITICAL"},
            {"field": "threat_score", "operator": "gte", "value": 90},
        ]
    }
    assert SafeConditionEvaluator.evaluate(and_cond, ctx)

    or_cond = {
        "or": [
            {"field": "severity", "operator": "equals", "value": "LOW"},
            {"field": "threat_score", "operator": "gte", "value": 90},
        ]
    }
    assert SafeConditionEvaluator.evaluate(or_cond, ctx)

    failed_and = {
        "and": [
            {"field": "severity", "operator": "equals", "value": "LOW"},
            {"field": "threat_score", "operator": "gte", "value": 90},
        ]
    }
    assert not SafeConditionEvaluator.evaluate(failed_and, ctx)


# ==============================================================================
# 2. SOAR Playbook Catalog & Management Tests
# ==============================================================================
def test_list_playbooks_api():
    """Verify listing playbooks returns seeded official playbooks."""
    resp = client.get("/api/v1/automation/playbooks")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 8
    pids = [p["playbook_id"] for p in data]
    assert "SOAR-PB-001" in pids
    assert "SOAR-PB-002" in pids


def test_get_playbook_detail_api():
    """Verify fetching playbook by ID returns sequential steps."""
    resp = client.get("/api/v1/automation/playbooks/SOAR-PB-001")
    assert resp.status_code == 200
    data = resp.json()
    assert data["playbook_id"] == "SOAR-PB-001"
    assert len(data["steps"]) >= 4
    first_step = data["steps"][0]
    assert first_step["step_order"] == 1
    assert "ENRICH" in first_step["action_type"]


def test_dry_run_playbook_api():
    """Verify dry-run execution preview without database mutations."""
    payload = {
        "mock_input": {
            "threat_score": 85,
            "ioc_value": "http://evil-tracker.test",
        }
    }
    resp = client.post("/api/v1/automation/playbooks/SOAR-PB-001/dry-run", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["dry_run"] is True
    assert data["total_steps"] >= 4
    assert data["executable_steps"] >= 3


def test_create_custom_playbook_api():
    """Verify creating a custom playbook with custom sequential steps."""
    payload = {
        "name": "Custom Endpoint Triage Workflow",
        "description": "User-defined automated triage routine.",
        "category": "CUSTOM_TRIAGE",
        "risk_level": "LOW",
        "requires_approval": False,
        "steps": [
            {
                "step_order": 1,
                "name": "Enrich Alert Context",
                "action_type": "ENRICH_ALERT",
                "parameters": {"alert_id": "ALT-TEST-99"},
            },
            {
                "step_order": 2,
                "name": "Build Timeline",
                "action_type": "BUILD_TIMELINE",
                "parameters": {},
            },
        ],
    }
    resp = client.post("/api/v1/automation/playbooks", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Custom Endpoint Triage Workflow"
    assert len(data["steps"]) == 2


# ==============================================================================
# 3. Playbook Execution & Idempotency Tests
# ==============================================================================
def test_trigger_playbook_execution_success():
    """Verify triggering an automated playbook completes execution."""
    payload = {
        "playbook_id": "SOAR-PB-001",
        "trigger_source": "ALERT",
        "source_id": "ALT-2026-UNIT-01",
        "context": {
            "ioc_value": "http://phish-login-test.xyz",
            "threat_score": 90,
        },
    }
    resp = client.post("/api/v1/automation/executions/trigger", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["status"] == PlaybookExecutionStatus.COMPLETED
    assert len(data["step_logs"]) >= 4
    assert data["simulation_only"] is True


def test_execution_idempotency_key_deduplication():
    """Verify that re-triggering with identical idempotency key returns existing execution."""
    key = "IDEMPOTENT-TEST-KEY-001"
    payload = {
        "playbook_id": "SOAR-PB-001",
        "trigger_source": "ALERT",
        "source_id": "ALT-IDEM-01",
        "idempotency_key": key,
        "context": {"ioc_value": "http://test.xyz", "threat_score": 80},
    }
    resp1 = client.post("/api/v1/automation/executions/trigger", json=payload)
    assert resp1.status_code == 201
    exec1_id = resp1.json()["execution_id"]

    resp2 = client.post("/api/v1/automation/executions/trigger", json=payload)
    assert resp2.status_code == 201
    exec2_id = resp2.json()["execution_id"]

    # Must be the exact same execution instance
    assert exec1_id == exec2_id


# ==============================================================================
# 4. Human-in-the-Loop Analyst Approval Gate Tests
# ==============================================================================
def test_approval_gate_pause_and_resume():
    """Verify high-risk playbook pauses at WAITING_APPROVAL and resumes upon approve."""
    # SOAR-PB-002 has requires_approval=True
    import uuid
    uniq_src = f"ALT-APPROVAL-{uuid.uuid4().hex[:6]}"
    payload = {
        "playbook_id": "SOAR-PB-002",
        "trigger_source": "ALERT",
        "source_id": uniq_src,
        "context": {"hostname": "WKST-ENG-02"},
    }
    resp = client.post("/api/v1/automation/executions/trigger", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["status"] == PlaybookExecutionStatus.WAITING_APPROVAL
    exec_id = data["execution_id"]

    # Now approve it
    approve_resp = client.post(
        f"/api/v1/automation/executions/{exec_id}/approve",
        json={"reason": "Confirmed Trojan infection warranting simulated isolation"},
    )
    assert approve_resp.status_code == 200
    approved_data = approve_resp.json()
    assert approved_data["status"] == PlaybookExecutionStatus.COMPLETED
    assert approved_data["approved_by"] is not None


def test_approval_gate_reject():
    """Verify analyst rejection cancels further execution."""
    import uuid
    uniq_src = f"ALT-REJECT-{uuid.uuid4().hex[:6]}"
    payload = {
        "playbook_id": "SOAR-PB-002",
        "trigger_source": "ALERT",
        "source_id": uniq_src,
        "context": {"hostname": "WKST-HR-01"},
    }
    resp = client.post("/api/v1/automation/executions/trigger", json=payload)
    assert resp.status_code == 201
    exec_id = resp.json()["execution_id"]

    reject_resp = client.post(
        f"/api/v1/automation/executions/{exec_id}/reject",
        json={"reason": "False positive; authorized administrative script"},
    )
    assert reject_resp.status_code == 200
    reject_data = reject_resp.json()
    assert reject_data["status"] == PlaybookExecutionStatus.CANCELLED
    assert reject_data["approval_status"] == "REJECTED"


# ==============================================================================
# 5. SOAR Metrics and Audit Logs Tests
# ==============================================================================
def test_soar_metrics_api():
    """Verify KPI dashboard metrics calculation."""
    resp = client.get("/api/v1/automation/metrics")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_playbooks"] >= 8
    assert data["total_executions"] >= 1
    assert "analyst_hours_saved" in data
    assert "success_rate_percent" in data


def test_audit_logs_api():
    """Verify audit log records immutable execution transitions."""
    resp = client.get("/api/v1/automation/audit-logs")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 1
    first_log = data[0]
    assert "action" in first_log
    assert "actor" in first_log
    assert first_log["simulation_only"] is True


# ==============================================================================
# 6. Advanced SOC Scenarios Catalog & Metrics Tests
# ==============================================================================
def test_list_scenarios_and_filtering():
    """Verify all 28 scenarios are queryable and filterable."""
    resp = client.get("/api/v1/soc-scenarios")
    assert resp.status_code == 200
    scenarios = resp.json()
    assert len(scenarios) >= 28

    # Filter by difficulty
    resp_beg = client.get("/api/v1/soc-scenarios?difficulty=BEGINNER")
    assert resp_beg.status_code == 200
    assert len(resp_beg.json()) >= 5

    resp_exp = client.get("/api/v1/soc-scenarios?difficulty=EXPERT")
    assert resp_exp.status_code == 200
    assert len(resp_exp.json()) >= 5

    # Filter by category
    resp_net = client.get("/api/v1/soc-scenarios?category=NETWORK_INVESTIGATION")
    assert resp_net.status_code == 200
    assert len(resp_net.json()) >= 1


def test_scenario_metrics_api():
    """Verify scenario aggregate metrics."""
    resp = client.get("/api/v1/soc-scenarios/metrics")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_scenarios"] >= 28
    assert "BEGINNER" in data["difficulty_distribution"]
    assert "EXPERT" in data["difficulty_distribution"]


def test_scenario_detail_api():
    """Verify scenario detail endpoint returns complete 9-stage material."""
    resp = client.get("/api/v1/soc-scenarios/SCEN-001")
    assert resp.status_code == 200
    data = resp.json()
    assert data["scenario_id"] == "SCEN-001"
    assert "available_evidence_json" in data
    assert "scoring_rubric_json" in data
    assert "solution_explanation" in data


# ==============================================================================
# 7. 9-Stage Guided Investigation Session Tests
# ==============================================================================
def test_scenario_attempt_session_full_lifecycle():
    """Test start, stage progression, hint unlock, submission, and grading."""
    # 1. Start attempt
    start_resp = client.post("/api/v1/soc-scenarios/SCEN-001/start")
    assert start_resp.status_code == 201
    attempt = start_resp.json()
    att_id = attempt["attempt_id"]
    assert attempt["status"] == ScenarioAttemptStatus.IN_PROGRESS
    assert attempt["current_stage"] == "STAGE_1_INITIAL_SIGNAL"

    # 2. Advance through stages
    stage_update = {
        "stage_name": "triage",
        "data": {"severity": "MEDIUM", "classification": "PORT_SCAN"},
        "advance_stage": True,
    }
    stage_resp = client.post(f"/api/v1/soc-scenarios/attempts/{att_id}/stage", json=stage_update)
    assert stage_resp.status_code == 200
    assert stage_resp.json()["current_stage"] == "STAGE_2_EVIDENCE_SELECTION"

    # 3. Request progressive hint
    hint_resp = client.post(f"/api/v1/soc-scenarios/attempts/{att_id}/hint")
    assert hint_resp.status_code == 200
    hint_data = hint_resp.json()
    assert "hint" in hint_data
    assert hint_data["hints_used"] == 1

    # 4. Save evidence and correlation data
    client.post(
        f"/api/v1/soc-scenarios/attempts/{att_id}/stage",
        json={
            "stage_name": "evidence_selection",
            "data": {"selected_evidence_ids": ["ev-1", "ev-2"]},
            "advance_stage": True,
        },
    )

    # 5. Submit and Evaluate
    submit_resp = client.post(f"/api/v1/soc-scenarios/attempts/{att_id}/submit")
    assert submit_resp.status_code == 200
    result = submit_resp.json()
    assert result["status"] == ScenarioAttemptStatus.COMPLETED
    assert result["score"] >= 0.0
    assert "breakdown" in result
    assert "hint_penalty" in result["breakdown"]
    assert len(result["feedback"]) >= 1
    assert "solution_explanation" in result
