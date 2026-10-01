"""End-to-End (E2E) Student Learning & SOC Operations Journey Tests.

Step 22 Final Integration Verification:
Tests the complete realistic student lifecycle across all platform domains:
Auth -> Curriculum -> Lab -> Simulation -> PCAP -> Detection -> SOC Alerts ->
Threat Intel -> Threat Hunting -> SIEM -> Endpoint -> Incident Response ->
MITRE ATT&CK -> SOAR Playbooks -> SOC Scenarios -> CTF Challenges ->
Skill Assessments -> Recommendations -> Portfolio Showcase -> Token Revocation.
"""

import uuid

from fastapi.testclient import TestClient


def test_e2e_student_full_educational_journey(client: TestClient) -> None:
    """Validate full end-to-end journey for a student from registration to portfolio and logout."""
    # -------------------------------------------------------------------------
    # 1. Registration & Authentication
    # -------------------------------------------------------------------------
    uid = uuid.uuid4().hex[:6]
    username = f"cadet_{uid}"
    password = "CadetPassword2026!#"
    email = f"cadet_{uid}@nexoranet.edu"

    reg_res = client.post(
        "/api/v1/auth/register",
        json={"username": username, "email": email, "password": password},
    )
    assert reg_res.status_code == 201
    reg_data = reg_res.json()
    assert "user" in reg_data
    user = reg_data["user"]
    assert user["username"] == username
    user_id = user["id"]

    login_res = client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": password},
    )
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}

    me_res = client.get("/api/v1/auth/me", headers=auth_headers)
    assert me_res.status_code == 200
    assert me_res.json()["id"] == user_id

    # -------------------------------------------------------------------------
    # 2. Learning & Curriculum Progression
    # -------------------------------------------------------------------------
    topics_res = client.get("/api/v1/topics", headers=auth_headers)
    assert topics_res.status_code == 200
    topics = topics_res.json()
    assert len(topics) > 0

    progress_res = client.get("/api/v1/learning/progress", headers=auth_headers)
    assert progress_res.status_code == 200
    init_progress = progress_res.json()
    assert "overall_percentage" in init_progress

    # Start and complete first available lesson
    start_lesson_res = client.post("/api/v1/lessons/1/start", headers=auth_headers)
    assert start_lesson_res.status_code == 200

    complete_lesson_res = client.post("/api/v1/lessons/1/complete", headers=auth_headers)
    assert complete_lesson_res.status_code == 200

    progress_after = client.get("/api/v1/learning/progress", headers=auth_headers).json()
    assert progress_after["completed_lessons"] >= 1

    # -------------------------------------------------------------------------
    # 3. Network Simulator & PCAP Offline Packet Analysis
    # -------------------------------------------------------------------------
    topo_res = client.get("/api/v1/simulator/topologies")
    assert topo_res.status_code == 200
    topos = topo_res.json()
    assert isinstance(topos, list)

    captures_res = client.get("/api/v1/packet-analysis/captures", headers=auth_headers)
    assert captures_res.status_code == 200
    captures = captures_res.json()
    assert isinstance(captures, list)

    # -------------------------------------------------------------------------
    # 4. Detection Engineering & Mini SOC
    # -------------------------------------------------------------------------
    rules_res = client.get("/api/v1/detection/rules")
    assert rules_res.status_code == 200
    rules = rules_res.json()
    assert len(rules) > 0

    soc_alerts_res = client.get("/api/v1/soc/alerts")
    assert soc_alerts_res.status_code == 200

    # -------------------------------------------------------------------------
    # 5. Threat Intelligence & Threat Hunting
    # -------------------------------------------------------------------------
    intel_overview = client.get("/api/v1/threat-intel/overview", headers=auth_headers)
    assert intel_overview.status_code == 200
    intel_data = intel_overview.json()
    assert "total_indicators" in intel_data

    hunt_overview = client.get("/api/v1/threat-hunting/overview", headers=auth_headers)
    assert hunt_overview.status_code == 200
    hunt_data = hunt_overview.json()
    assert "total_hunts" in hunt_data

    # -------------------------------------------------------------------------
    # 6. SIEM & Host Endpoint Telemetry
    # -------------------------------------------------------------------------
    siem_overview = client.get("/api/v1/siem/overview", headers=auth_headers)
    assert siem_overview.status_code == 200

    endpoint_stats = client.get("/api/v1/endpoint-security/overview")
    assert endpoint_stats.status_code == 200

    # -------------------------------------------------------------------------
    # 7. Incident Response, MITRE ATT&CK & SOAR Playbooks
    # -------------------------------------------------------------------------
    incidents_res = client.get("/api/v1/incidents")
    assert incidents_res.status_code == 200
    inc_items = incidents_res.json()
    incidents = inc_items["items"] if isinstance(inc_items, dict) and "items" in inc_items else inc_items
    assert len(incidents) > 0
    inc_id = incidents[0]["id"]

    inc_detail = client.get(f"/api/v1/incidents/{inc_id}")
    assert inc_detail.status_code == 200

    mitre_techs = client.get("/api/v1/mitre/techniques")
    assert mitre_techs.status_code == 200

    playbooks_res = client.get("/api/v1/automation/playbooks")
    assert playbooks_res.status_code == 200
    playbooks = playbooks_res.json()
    assert len(playbooks) > 0

    dry_run_res = client.post(
        "/api/v1/automation/playbooks/1/dry-run",
        json={"mock_input": {"threat_score": 90, "ip": "10.0.0.45"}},
    )
    assert dry_run_res.status_code == 200
    assert dry_run_res.json()["dry_run"] is True

    # -------------------------------------------------------------------------
    # 8. SOC Scenarios & CTF Challenges
    # -------------------------------------------------------------------------
    scenarios_res = client.get("/api/v1/soc-scenarios")
    assert scenarios_res.status_code == 200
    scenarios = scenarios_res.json()
    assert len(scenarios) > 0

    chal_res = client.get("/api/v1/challenges")
    assert chal_res.status_code == 200
    chals = chal_res.json()
    assert len(chals) > 0

    first_chal_id = chals[0]["challenge_id"]
    chal_detail = client.get(f"/api/v1/challenges/{first_chal_id}")
    assert chal_detail.status_code == 200
    detail_json = chal_detail.json()
    assert "flag_hash" not in detail_json

    # -------------------------------------------------------------------------
    # 9. Skill Assessment, Recommendations & Student Portfolio
    # -------------------------------------------------------------------------
    skills_res = client.get("/api/v1/skills/assessment", headers=auth_headers)
    assert skills_res.status_code == 200
    assert isinstance(skills_res.json(), list)

    recs_res = client.get("/api/v1/recommendations", headers=auth_headers)
    assert recs_res.status_code == 200
    assert isinstance(recs_res.json(), list)

    port_create = client.post(
        "/api/v1/portfolio/projects",
        headers=auth_headers,
        json={
            "title": "E2E Capstone Portfolio",
            "description": "Completed full learning curriculum and SOC incident simulations.",
            "skills": ["Packet Analysis", "Incident Response"],
        },
    )
    assert port_create.status_code == 201
    port_id = port_create.json()["id"]

    port_res = client.get("/api/v1/portfolio", headers=auth_headers)
    assert port_res.status_code == 200
    projects = port_res.json()["projects"]
    assert any(p["id"] == port_id for p in projects)

    # -------------------------------------------------------------------------
    # 10. Logout & Token Invalidation
    # -------------------------------------------------------------------------
    logout_res = client.post("/api/v1/auth/logout", headers=auth_headers)
    assert logout_res.status_code == 200
    assert logout_res.json()["status"] == "ok"

    # Verifying token is rejected after revocation
    revoked_me = client.get("/api/v1/auth/me", headers=auth_headers)
    assert revoked_me.status_code == 401


def test_e2e_unauthenticated_access_denials(client: TestClient, monkeypatch) -> None:
    """Ensure sensitive endpoints reject requests missing authentication tokens in production or with invalid tokens."""
    # 1. Invalid Bearer tokens must always be rejected with 401
    bad_headers = {"Authorization": "Bearer invalid.token.payload"}
    res_bad_auth = client.get("/api/v1/auth/me", headers=bad_headers)
    assert res_bad_auth.status_code == 401

    res_bad_port = client.get("/api/v1/portfolio", headers=bad_headers)
    assert res_bad_port.status_code == 401

    # 2. In production mode, endpoints without any token must be strictly rejected with 401
    monkeypatch.setattr("app.api.deps.settings.ENVIRONMENT", "production")

    res_portfolio = client.post(
        "/api/v1/portfolio/projects",
        json={"title": "Unauthorized", "description": "Needs Auth", "skills": ["Web Security"]},
    )
    assert res_portfolio.status_code == 401

    res_progress = client.get("/api/v1/learning/progress")
    assert res_progress.status_code == 401

    res_recs = client.get("/api/v1/recommendations")
    assert res_recs.status_code == 401

    res_skills = client.get("/api/v1/skills/assessment")
    assert res_skills.status_code == 401


def test_e2e_pagination_and_query_robustness(client: TestClient) -> None:
    """Verify system robustness against pagination bounds and non-existent queries."""
    # 1. Bounds enforcement: limit > 100 is rejected with 422
    res_inc_over_limit = client.get("/api/v1/incidents?limit=500&skip=0")
    assert res_inc_over_limit.status_code == 422

    # 2. Negative skip is rejected with 422
    res_inc_neg = client.get("/api/v1/incidents?skip=-1")
    assert res_inc_neg.status_code == 422

    # 3. Valid pagination max boundary works cleanly
    res_inc_max = client.get("/api/v1/incidents?limit=100&skip=0")
    assert res_inc_max.status_code == 200

    # 4. Challenges valid pagination works cleanly
    res_chal_valid = client.get("/api/v1/challenges?limit=100&skip=0")
    assert res_chal_valid.status_code == 200

    # 5. Detection rules filtering with non-matching search returns empty list
    res_rules_empty = client.get("/api/v1/detection/rules?search=non_existent_rule_xyz_999999")
    assert res_rules_empty.status_code == 200
    assert len(res_rules_empty.json()) == 0

    # 6. Unknown challenge lookup returns 404 safely, not 500
    res_chal_404 = client.get("/api/v1/challenges/CHAL-DOES-NOT-EXIST")
    assert res_chal_404.status_code == 404
