"""Comprehensive Automated Test Suite for NexoraNet Hands-on Lab Engine.

Verifies lab listing, filtering, search, zero-knowledge answer shielding,
answer validation across all supported question types (Single Choice, Text,
Numeric, IP, CIDR, Subnet, Port), attempt lifecycle, step submission,
scoring idempotency, retries, history review, and security constraints.
"""

from app.services.lab_validator import (
    validate_cidr,
    validate_ip_address,
    validate_numerical,
    validate_port,
    validate_single_choice,
    validate_text,
)
from fastapi import status
from fastapi.testclient import TestClient


def test_list_published_labs(client: TestClient) -> None:
    """Verify listing returns published labs with step counts and difficulty tiers."""
    response = client.get("/api/v1/labs")
    assert response.status_code == status.HTTP_200_OK

    labs = response.json()
    assert isinstance(labs, list)
    assert len(labs) >= 18  # 10 Beginner + 8 Intermediate published

    # Verify first lab structure
    first = labs[0]
    assert "id" in first
    assert "title" in first
    assert "slug" in first
    assert "difficulty" in first
    assert "environment_type" in first
    assert "total_steps" in first
    assert first["total_steps"] > 0
    assert first["user_status"] in ("NOT_STARTED", "IN_PROGRESS", "COMPLETED")


def test_filter_labs_by_difficulty_case_insensitive(client: TestClient) -> None:
    """Verify case-insensitive difficulty query filtering."""
    # Lowercase 'beginner'
    resp_beg = client.get("/api/v1/labs?difficulty=beginner")
    assert resp_beg.status_code == status.HTTP_200_OK
    beg_labs = resp_beg.json()
    assert len(beg_labs) >= 10
    assert all(l["difficulty"] == "BEGINNER" for l in beg_labs)

    # Uppercase 'INTERMEDIATE'
    resp_int = client.get("/api/v1/labs?difficulty=INTERMEDIATE")
    assert resp_int.status_code == status.HTTP_200_OK
    int_labs = resp_int.json()
    assert len(int_labs) >= 8
    assert all(l["difficulty"] == "INTERMEDIATE" for l in int_labs)


def test_filter_labs_by_environment(client: TestClient) -> None:
    """Verify filtering by environment type (LOCAL_SYSTEM vs CONCEPTUAL)."""
    resp_local = client.get("/api/v1/labs?environment=LOCAL_SYSTEM")
    assert resp_local.status_code == status.HTTP_200_OK
    local_labs = resp_local.json()
    assert len(local_labs) >= 10
    assert all(l["environment_type"] == "LOCAL_SYSTEM" for l in local_labs)

    resp_conc = client.get("/api/v1/labs?environment=CONCEPTUAL")
    assert resp_conc.status_code == status.HTTP_200_OK
    conc_labs = resp_conc.json()
    assert len(conc_labs) >= 8
    assert all(l["environment_type"] == "CONCEPTUAL" for l in conc_labs)


def test_search_labs(client: TestClient) -> None:
    """Verify search returns matching labs by keyword."""
    resp = client.get("/api/v1/labs/search?q=Subnet")
    assert resp.status_code == status.HTTP_200_OK
    results = resp.json()
    assert len(results) >= 2
    assert any("subnet" in r["title"].lower() for r in results)


def test_get_lab_detail_and_answer_shielding(client: TestClient) -> None:
    """Verify detailed lab retrieval shields secret answer keys from student view."""
    resp = client.get("/api/v1/labs/find-local-ip-address")
    assert resp.status_code == status.HTTP_200_OK

    lab = resp.json()
    assert lab["slug"] == "find-local-ip-address"
    assert "steps" in lab
    assert len(lab["steps"]) == 3

    # Crucial security check: answer keys, regexes, and correct choices MUST NOT be exposed
    serialized = str(lab).lower()
    assert "correct_option" not in serialized
    assert "correct_answers" not in serialized
    assert "expected_ip" not in serialized


def test_start_lab_attempt_workflow(client: TestClient) -> None:
    """Verify starting a lab initializes or resumes an in-progress attempt."""
    resp = client.get("/api/v1/labs/find-local-ip-address")
    lab_id = resp.json()["id"]

    start_resp = client.post(f"/api/v1/labs/{lab_id}/start")
    assert start_resp.status_code == status.HTTP_200_OK
    data = start_resp.json()
    assert data["active_attempt_id"] is not None
    assert data["active_attempt_status"] == "IN_PROGRESS"


def test_validation_engine_single_choice() -> None:
    """Test single choice validation with correct and incorrect options."""
    rule = {
        "correct_option": "ipconfig",
        "explanation": "Standard Windows tool.",
    }
    res_valid = validate_single_choice("ipconfig", rule)
    assert res_valid.is_correct is True
    assert res_valid.points_earned == 10.0

    res_invalid = validate_single_choice("netstat", rule)
    assert res_invalid.is_correct is False
    assert res_invalid.points_earned == 0.0


def test_validation_engine_text_normalization() -> None:
    """Test text validation with trimming, case sensitivity, and acceptable synonyms."""
    rule = {
        "accepted_answers": ["Wi-Fi", "eth0", "en0"],
        "case_sensitive": False,
    }
    # Lowercase match
    res_low = validate_text("  wi-fi  ", rule)
    assert res_low.is_correct is True

    # Synonym match
    res_eth = validate_text("eth0", rule)
    assert res_eth.is_correct is True

    # Bad input
    res_bad = validate_text("bluetooth0", rule)
    assert res_bad.is_correct is False


def test_validation_engine_numerical() -> None:
    """Test numeric calculation comparison with tolerance."""
    rule = {"expected_value": 62, "tolerance": 0}
    assert validate_numerical("62", rule).is_correct is True
    assert validate_numerical(62, rule).is_correct is True
    assert validate_numerical("64", rule).is_correct is False
    assert validate_numerical("not-a-number", rule).is_correct is False


def test_validation_engine_ip_address() -> None:
    """Test IP address validation for syntax, version, private space, and loopback."""
    # Syntax check
    assert validate_ip_address("999.999.999.999", {}).is_correct is False

    # Target match
    rule_target = {"expected_ip": "192.168.10.32", "expected_version": 4}
    assert validate_ip_address("192.168.10.32", rule_target).is_correct is True
    assert validate_ip_address("192.168.10.33", rule_target).is_correct is False

    # Private constraint
    rule_private = {"require_private": True}
    assert validate_ip_address("192.168.1.100", rule_private).is_correct is True
    assert validate_ip_address("10.0.0.1", rule_private).is_correct is True
    assert validate_ip_address("8.8.8.8", rule_private).is_correct is False

    # IPv6 Loopback
    rule_v6_loop = {"expected_ip": "::1", "expected_version": 6}
    assert validate_ip_address("::1", rule_v6_loop).is_correct is True


def test_validation_engine_cidr() -> None:
    """Test CIDR prefix and network notation validation."""
    rule_prefix = {"prefix_only": True, "expected_prefix_length": "26"}
    assert validate_cidr("/26", rule_prefix).is_correct is True
    assert validate_cidr("26", rule_prefix).is_correct is True
    assert validate_cidr("/27", rule_prefix).is_correct is False

    rule_net = {"expected_cidr": "192.168.10.0/24"}
    assert validate_cidr("192.168.10.0/24", rule_net).is_correct is True
    assert validate_cidr("192.168.20.0/24", rule_net).is_correct is False


def test_validation_engine_port() -> None:
    """Test port number range (1-65535) and target matching."""
    rule_https = {"expected_port": 443}
    assert validate_port("443", rule_https).is_correct is True
    assert validate_port(443, rule_https).is_correct is True
    assert validate_port("80", rule_https).is_correct is False
    assert validate_port("70000", rule_https).is_correct is False
    assert validate_port("-1", rule_https).is_correct is False


def test_step_submission_and_attempt_completion(client: TestClient) -> None:
    """
    Test full student attempt workflow:
    Start lab -> Submit step answers -> Verify scoring & completion.
    """
    # 1. Start Lab 1
    lab_resp = client.post("/api/v1/labs/find-local-ip-address/start")
    assert lab_resp.status_code == status.HTTP_200_OK
    lab = lab_resp.json()
    attempt_id = lab["active_attempt_id"]
    steps = lab["steps"]

    # 2. Submit Step 1 (ipconfig)
    sub1_resp = client.post(
        f"/api/v1/lab-attempts/{attempt_id}/steps/{steps[0]['id']}/submit",
        json={"submitted_answer": "ipconfig", "hint_used": False},
    )
    assert sub1_resp.status_code == status.HTTP_200_OK
    data1 = sub1_resp.json()
    assert data1["is_correct"] is True
    assert data1["points_earned"] == 10.0
    assert data1["attempt_score"] >= 10.0

    # 3. Test Idempotency: Re-submitting same step does not inflate score
    sub1_re_resp = client.post(
        f"/api/v1/lab-attempts/{attempt_id}/steps/{steps[0]['id']}/submit",
        json={"submitted_answer": "ipconfig", "hint_used": False},
    )
    assert sub1_re_resp.status_code == status.HTTP_200_OK
    data1_re = sub1_re_resp.json()
    assert data1_re["attempt_score"] == data1["attempt_score"]

    # 4. Submit Step 2 (valid local IP)
    sub2_resp = client.post(
        f"/api/v1/lab-attempts/{attempt_id}/steps/{steps[1]['id']}/submit",
        json={"submitted_answer": "192.168.1.150", "hint_used": True},
    )
    assert sub2_resp.status_code == status.HTTP_200_OK
    assert sub2_resp.json()["is_correct"] is True

    # 5. Submit Step 3 (Private address classification)
    sub3_resp = client.post(
        f"/api/v1/lab-attempts/{attempt_id}/steps/{steps[2]['id']}/submit",
        json={
            "submitted_answer": "RFC 1918 Private Address (10.x, 172.16-31.x, 192.168.x)",
            "hint_used": False,
        },
    )
    assert sub3_resp.status_code == status.HTTP_200_OK
    data3 = sub3_resp.json()
    assert data3["is_correct"] is True
    assert data3["is_lab_completed"] is True
    assert data3["attempt_percentage"] == 100.0


def test_retry_lab_attempt_workflow(client: TestClient) -> None:
    """Verify retrying a lab preserves old attempt and starts a new attempt."""
    # Start and get attempt
    lab_resp = client.get("/api/v1/labs/find-local-ip-address")
    lab = lab_resp.json()
    old_attempt_id = lab["active_attempt_id"]

    # Trigger retry
    retry_resp = client.post(f"/api/v1/lab-attempts/{old_attempt_id}/retry")
    assert retry_resp.status_code == status.HTTP_200_OK

    new_lab = retry_resp.json()
    new_attempt_id = new_lab["active_attempt_id"]
    assert new_attempt_id != old_attempt_id
    assert new_lab["attempt_number"] > 1
    assert new_lab["active_attempt_score"] == 0.0


def test_lab_history_and_review(client: TestClient) -> None:
    """Verify student lab attempt history and granular submission review."""
    history_resp = client.get("/api/v1/lab-attempts")
    assert history_resp.status_code == status.HTTP_200_OK
    history = history_resp.json()
    assert isinstance(history, list)
    assert len(history) >= 1

    first_attempt = history[0]
    detail_resp = client.get(f"/api/v1/lab-attempts/{first_attempt['id']}")
    assert detail_resp.status_code == status.HTTP_200_OK
    detail = detail_resp.json()
    assert "submissions" in detail
    assert "lab_title" in detail


def test_security_cannot_submit_to_invalid_step(client: TestClient) -> None:
    """Verify security check rejects submissions to steps that do not belong to the lab."""
    # Attempt on lab 1
    lab_resp = client.get("/api/v1/labs/find-local-ip-address")
    attempt_id = lab_resp.json()["active_attempt_id"]

    # Submit with non-existent step id 999999
    bad_resp = client.post(
        f"/api/v1/lab-attempts/{attempt_id}/steps/999999/submit",
        json={"submitted_answer": "test"},
    )
    assert bad_resp.status_code == status.HTTP_404_NOT_FOUND


def test_lab_telemetry_endpoint(client: TestClient) -> None:
    """Verify student aggregate telemetry metrics."""
    telemetry_resp = client.get("/api/v1/labs/telemetry")
    assert telemetry_resp.status_code == status.HTTP_200_OK
    data = telemetry_resp.json()
    assert "total_labs" in data
    assert data["total_labs"] >= 18
    assert "completed_labs" in data
    assert "average_score" in data
    assert "beginner_total" in data
    assert "intermediate_total" in data
