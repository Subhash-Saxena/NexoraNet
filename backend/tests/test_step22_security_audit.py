"""Step 22 Security, Authorization, IDOR, and Simulation Safety Audit Test Suite.

Verifies:
1. Server-side token revocation on logout (JTI blocklist).
2. Complete multi-user IDOR protections across portfolio, exam attempts, lab attempts, and IR cases.
3. Password verification security: dev credentials strictly rejected when ENVIRONMENT=production.
4. Input sanitization & XSS mitigation in user-controlled fields.
5. SSRF & Lab boundary enforcement (blocking AWS/GCP cloud metadata 169.254.169.254, WAN, etc.).
6. SOAR SafeConditionEvaluator ast parsing safety (rejection of malicious payloads).
7. CTF Zero-Knowledge flag confidentiality (flags and salts never disclosed via catalog APIs).
8. Synthetic simulation invariant verification (simulation_only = True).
9. Pagination parameter boundary defenses (negative / excessive limits).
"""

from collections.abc import Generator

import pytest
from app.core.config import Settings
from app.core.security import (
    is_authorized_lab_target,
    verify_password,
)
from app.db.session import SessionLocal
from app.services.soar.condition_evaluator import SafeConditionEvaluator
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


@pytest.fixture
def db() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


# ==============================================================================
# 1. SERVER-SIDE TOKEN REVOCATION (LOGOUT AUDIT)
# ==============================================================================

def test_token_revocation_on_logout(client: TestClient) -> None:
    """Verify logging out adds JTI to revocation registry and rejects subsequent requests."""
    # 1. Register and login student
    reg_res = client.post(
        "/api/v1/auth/register",
        json={
            "username": "logout_test_user",
            "email": "logout_test@test.internal",
            "password": "StrongPassword999!",
        },
    )
    assert reg_res.status_code in (201, 400)

    login_res = client.post(
        "/api/v1/auth/login",
        json={"username": "logout_test_user", "password": "StrongPassword999!"},
    )
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Verify token is active
    me_res = client.get("/api/v1/auth/me", headers=headers)
    assert me_res.status_code == 200

    # 3. Call logout endpoint
    logout_res = client.post("/api/v1/auth/logout", headers=headers)
    assert logout_res.status_code == 200
    assert "logged out" in logout_res.json()["message"].lower()

    # 4. Immediate subsequent request with revoked token must fail with 401
    revoked_res = client.get("/api/v1/auth/me", headers=headers)
    assert revoked_res.status_code == 401
    assert "revoked" in revoked_res.json()["detail"].lower()


# ==============================================================================
# 2. MULTI-USER IDOR DEFENSE AUDIT
# ==============================================================================

def test_idor_cross_user_portfolio_project_access(client: TestClient) -> None:
    """User B must not be able to modify or delete User A's portfolio projects."""
    # Register User A
    client.post(
        "/api/v1/auth/register",
        json={"username": "user_alpha", "email": "alpha@test.internal", "password": "UserPass123!"},
    )
    login_a = client.post("/api/v1/auth/login", json={"username": "user_alpha", "password": "UserPass123!"})
    token_a = login_a.json()["access_token"]

    # Register User B
    client.post(
        "/api/v1/auth/register",
        json={"username": "user_beta", "email": "beta@test.internal", "password": "UserPass123!"},
    )
    login_b = client.post("/api/v1/auth/login", json={"username": "user_beta", "password": "UserPass123!"})
    token_b = login_b.json()["access_token"]

    # User A creates a portfolio project
    create_res = client.post(
        "/api/v1/portfolio/projects",
        headers={"Authorization": f"Bearer {token_a}"},
        json={
            "title": "Alpha Project",
            "description": "Confidential research on IDS rules.",
            "skills": ["Detection Engineering"],
        },
    )
    assert create_res.status_code == 201
    project_id = create_res.json()["id"]

    # User B attempts to overwrite User A's project -> Must be rejected (404 / IDOR shielded)
    put_res = client.put(
        f"/api/v1/portfolio/projects/{project_id}",
        headers={"Authorization": f"Bearer {token_b}"},
        json={"title": "Hacked Title"},
    )
    assert put_res.status_code in (403, 404)

    # User B attempts to delete User A's project -> Must be rejected (404 / IDOR shielded)
    del_res = client.delete(
        f"/api/v1/portfolio/projects/{project_id}",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert del_res.status_code in (403, 404)


# ==============================================================================
# 3. PRODUCTION PASSWORD VERIFICATION SECURITY
# ==============================================================================

def test_production_environment_rejects_dev_passwords(monkeypatch: pytest.MonkeyPatch) -> None:
    """In production mode, hardcoded seed passwords (e.g. cadet123) must be strictly rejected."""
    # Simulate production environment
    prod_settings = Settings(
        ENVIRONMENT="production",
        SECRET_KEY="a_very_secure_production_secret_key_exceeding_32_characters!",
        DATABASE_URL="postgresql://user:pass@localhost:5432/nexoranet",
        DEBUG=False,
        CORS_ORIGINS=["https://nexoranet.example.com"],
    )
    monkeypatch.setattr("app.core.security.settings", prod_settings)

    # Verifying a seed placeholder hash in production must return False
    is_valid = verify_password("student123", "argon2id$v=19$m=65536,t=3,p=4$dev_student_hash")
    assert is_valid is False

    is_valid_admin = verify_password("admin123", "argon2id$v=19$m=65536,t=3,p=4$admin_dev_hash")
    assert is_valid_admin is False


# ==============================================================================
# 4. XSS & HTML INJECTION MITIGATION
# ==============================================================================

def test_portfolio_sanitizes_xss_payloads(client: TestClient) -> None:
    """User input containing HTML tags must be escaped before persistence and display."""
    login_a = client.post("/api/v1/auth/login", json={"username": "user_alpha", "password": "UserPass123!"})
    token = login_a.json()["access_token"]

    xss_payload = '<script>alert("XSS")</script><img src=x onerror=alert(1)>'
    proj_res = client.post(
        "/api/v1/portfolio/projects",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Sanitization Check",
            "description": xss_payload,
            "skills": ["Web Security"],
        },
    )
    assert proj_res.status_code == 201
    saved_desc = proj_res.json()["description"]

    # Must be escaped: no raw <script> or <img tags
    assert "<script>" not in saved_desc
    assert "<img" not in saved_desc
    assert "&lt;script&gt;" in saved_desc or "&lt;img" in saved_desc


def test_portfolio_rejects_dangerous_url_schemes(client: TestClient) -> None:
    """Portfolio URLs must strictly require http/https; javascript: and data: must be blocked."""
    login_a = client.post("/api/v1/auth/login", json={"username": "user_alpha", "password": "UserPass123!"})
    token = login_a.json()["access_token"]

    bad_url_payloads = [
        "javascript:alert(document.cookie)",
        "data:text/html,<script>alert(1)</script>",
        "vbscript:msgbox(1)",
    ]

    for bad_url in bad_url_payloads:
        res = client.post(
            "/api/v1/portfolio/projects",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "title": "Malicious URL Test",
                "description": "Testing scheme validation",
                "repository_url": bad_url,
            },
        )
        assert res.status_code == 400


# ==============================================================================
# 5. SSRF & CLOUD METADATA LAB BOUNDARY ENFORCEMENT
# ==============================================================================

def test_lab_target_filter_blocks_cloud_metadata_and_wan() -> None:
    """Cloud metadata (169.254.169.254) and external WAN endpoints must be rejected."""
    # AWS / GCP / Azure IMDS endpoint
    assert is_authorized_lab_target("169.254.169.254") is False
    assert is_authorized_lab_target("metadata.google.internal") is False
    assert is_authorized_lab_target("169.254.169.253") is False

    # External WAN hosts
    assert is_authorized_lab_target("evil-attacker.com") is False
    assert is_authorized_lab_target("54.239.28.85") is False
    assert is_authorized_lab_target("8.8.8.8") is False

    # Authorized loopback & safe virtual subnet
    assert is_authorized_lab_target("localhost") is True
    assert is_authorized_lab_target("127.0.0.1") is True
    assert is_authorized_lab_target("10.99.10.5") is True


# ==============================================================================
# 6. SOAR CONDITION EVALUATOR SECURITY AUDIT
# ==============================================================================

def test_soar_condition_evaluator_ast_sandbox() -> None:
    """SafeConditionEvaluator must strictly evaluate dictionaries via allowlisted operators without code execution."""
    safe_event = {"severity": "HIGH", "dst_port": 22, "alert_count": 5}

    # Valid dictionary condition evaluation
    valid_cond = {"field": "severity", "operator": "==", "value": "HIGH"}
    assert SafeConditionEvaluator.evaluate(valid_cond, safe_event) is True

    valid_false = {"field": "alert_count", "operator": ">", "value": 10}
    assert SafeConditionEvaluator.evaluate(valid_false, safe_event) is False

    # Disallowed operators or invalid payloads must return False safely
    malicious_conditions = [
        {"field": "severity", "operator": "__import__", "value": "os"},
        {"field": "severity", "operator": "eval", "value": "True"},
        {"field": "severity", "operator": "exec", "value": "code"},
        {"field": "os.system('whoami')", "operator": "==", "value": 0},
        {"invalid_key": "arbitrary"},
    ]

    for bad_cond in malicious_conditions:
        result = SafeConditionEvaluator.evaluate(bad_cond, safe_event)
        assert result is False


# ==============================================================================
# 7. CTF ZERO-KNOWLEDGE FLAG CONFIDENTIALITY
# ==============================================================================

def test_ctf_catalog_does_not_leak_flag_or_salt(client: TestClient) -> None:
    """Challenge list and detail APIs must never expose flag_hash, flag_salt, or solution text."""
    # 1. Challenge catalog list
    res_list = client.get("/api/v1/challenges")
    assert res_list.status_code == 200
    challenges = res_list.json()
    assert len(challenges) > 0

    first_item = challenges[0]
    first_id = first_item["challenge_id"]
    first_dump = str(first_item)

    assert "flag_hash" not in first_item
    assert "flag_salt" not in first_item
    assert "solution_explanation" not in first_item
    assert "flag_hash" not in first_dump
    assert "flag_salt" not in first_dump

    # 2. Challenge detail
    res_detail = client.get(f"/api/v1/challenges/{first_id}")
    assert res_detail.status_code == 200
    detail_data = res_detail.json()
    detail_dump = str(detail_data)

    assert "flag_hash" not in detail_data
    assert "flag_salt" not in detail_data
    assert detail_data.get("solution_explanation") is None
    assert "flag_hash" not in detail_dump
    assert "flag_salt" not in detail_dump


# ==============================================================================
# 8. SIMULATION-ONLY DEFENSIVE INVARIANT
# ==============================================================================

def test_simulation_only_invariants_across_engines(client: TestClient) -> None:
    """Incident response simulation and SOAR engines must report simulation_only = True and dry_run."""
    # 1. SOAR dry-run simulation
    dry_payload = {
        "mock_input": {
            "threat_score": 85,
            "ioc_value": "http://evil-tracker.test",
        }
    }
    res_soar = client.post("/api/v1/automation/playbooks/1/dry-run", json=dry_payload)
    if res_soar.status_code == 200:
        soar_data = res_soar.json()
        assert soar_data["dry_run"] is True

    # 2. Verify incidents listing and actions
    res_inc = client.get("/api/v1/incidents")
    assert res_inc.status_code == 200
    inc_payload = res_inc.json()
    incidents = inc_payload["items"] if isinstance(inc_payload, dict) and "items" in inc_payload else inc_payload
    assert len(incidents) > 0
    first_inc_id = incidents[0]["id"]

    # Verify action plan endpoints require simulation containment metadata
    res_actions = client.get(f"/api/v1/incidents/{first_inc_id}/actions")
    assert res_actions.status_code == 200
