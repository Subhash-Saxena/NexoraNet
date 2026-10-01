
from fastapi import status
from fastapi.testclient import TestClient


def test_list_mock_tests_with_filters(client: TestClient):
    """Verify listing mock tests with difficulty, test_type, and search filters."""
    # List all
    res = client.get("/api/v1/mock-tests")
    assert res.status_code == status.HTTP_200_OK
    tests = res.json()
    assert len(tests) >= 4

    # Filter by difficulty
    res_diff = client.get("/api/v1/mock-tests?difficulty=BEGINNER")
    assert res_diff.status_code == status.HTTP_200_OK
    beginner_tests = res_diff.json()
    assert all(t["difficulty"] == "BEGINNER" for t in beginner_tests)

    # Filter by test type
    res_type = client.get("/api/v1/mock-tests?test_type=COMPREHENSIVE")
    assert res_type.status_code == status.HTTP_200_OK
    comp_tests = res_type.json()
    assert any(t["test_type"] == "COMPREHENSIVE" for t in comp_tests)

    # Search keyword
    res_search = client.get("/api/v1/mock-tests?q=Fundamentals")
    assert res_search.status_code == status.HTTP_200_OK
    search_tests = res_search.json()
    assert any("Fundamentals" in t["title"] for t in search_tests)


def test_mock_test_detail_instructions_and_topics(client: TestClient):
    """Verify mock test detail returns instructions, topics breakdown, and shielded questions."""
    res = client.get("/api/v1/mock-tests/beginner-networking-fundamentals-test")
    assert res.status_code == status.HTTP_200_OK
    data = res.json()
    assert data["title"] == "Beginner Networking Fundamentals Test"
    assert data["total_questions"] == 30
    assert data["passing_percentage"] == 70.0
    assert data["instructions"] is not None
    assert len(data["topics_covered"]) > 0
    assert len(data["topics_breakdown"]) > 0

    # Shielded questions
    for q in data["questions"]:
        assert "explanation" not in q
        assert len(q["options"]) > 0
        for opt in q["options"]:
            assert "is_correct" not in opt


def test_start_attempt_authoritative_timer_and_resume(client: TestClient):
    """Verify starting an attempt creates authoritative UTC timestamps, and re-calling resumes."""
    res = client.post("/api/v1/mock-tests/beginner-networking-fundamentals-test/start")
    assert res.status_code == status.HTTP_200_OK
    attempt = res.json()
    attempt_id = attempt["attempt_id"]
    assert attempt_id > 0
    assert attempt["remaining_seconds"] > 0
    assert attempt["remaining_seconds"] <= 30 * 60
    assert attempt["status"] == "IN_PROGRESS"
    assert len(attempt["questions"]) == 30

    # Questions zero-knowledge check
    for q in attempt["questions"]:
        assert "explanation" not in q
        for opt in q["options"]:
            assert "is_correct" not in opt

    # Resume active sitting (retake=False)
    res_resume = client.post("/api/v1/mock-tests/beginner-networking-fundamentals-test/start")
    assert res_resume.status_code == status.HTTP_200_OK
    resume_data = res_resume.json()
    assert resume_data["attempt_id"] == attempt_id


def test_save_and_clear_student_answers(client: TestClient):
    """Verify saving answer, idempotent update, and clearing answer."""
    # Start sitting
    res = client.post("/api/v1/mock-tests/beginner-networking-basics/start?retake=true")
    assert res.status_code == status.HTTP_200_OK
    attempt = res.json()
    attempt_id = attempt["attempt_id"]
    q1 = attempt["questions"][0]
    opt1_id = q1["options"][0]["id"]
    opt2_id = q1["options"][1]["id"]

    # Save answer for q1
    save_res = client.post(
        f"/api/v1/mock-test-attempts/{attempt_id}/save-answer",
        json={"question_id": q1["id"], "selected_option_ids": [opt1_id]},
    )
    assert save_res.status_code == status.HTTP_200_OK
    assert save_res.json()["success"] is True

    # Idempotently update answer with different option
    save_res2 = client.post(
        f"/api/v1/mock-test-attempts/{attempt_id}/save-answer",
        json={"question_id": q1["id"], "selected_option_ids": [opt2_id]},
    )
    assert save_res2.status_code == status.HTTP_200_OK
    assert save_res2.json()["selected_option_ids"] == [opt2_id]

    # Clear answer
    clear_res = client.post(
        f"/api/v1/mock-test-attempts/{attempt_id}/clear-answer/{q1['id']}"
    )
    assert clear_res.status_code == status.HTTP_200_OK
    assert clear_res.json()["selected_option_ids"] == []


def test_mark_question_and_timer_sync_status(client: TestClient):
    """Verify marking question for review and authoritative status endpoint."""
    res = client.post("/api/v1/mock-tests/beginner-networking-basics/start?retake=true")
    attempt_id = res.json()["attempt_id"]
    q1 = res.json()["questions"][0]
    q2 = res.json()["questions"][1]

    # Save answer for q1
    client.post(
        f"/api/v1/mock-test-attempts/{attempt_id}/save-answer",
        json={"question_id": q1["id"], "selected_option_ids": [q1["options"][0]["id"]]},
    )

    # Mark q2 for review
    mark_res = client.post(
        f"/api/v1/mock-test-attempts/{attempt_id}/mark-question/{q2['id']}",
        json={"is_marked_for_review": True},
    )
    assert mark_res.status_code == status.HTTP_200_OK

    # Check status
    status_res = client.get(f"/api/v1/mock-test-attempts/{attempt_id}/status")
    assert status_res.status_code == status.HTTP_200_OK
    status_data = status_res.json()
    assert status_data["answered_count"] == 1
    assert status_data["marked_count"] == 1
    assert status_data["is_expired"] is False
    assert status_data["remaining_seconds"] > 0


def test_shielding_guard_review_forbidden_while_in_progress(client: TestClient):
    """Verify get_attempt_review raises 403 Forbidden while attempt is in progress."""
    res = client.post("/api/v1/mock-tests/beginner-networking-basics/start?retake=true")
    attempt_id = res.json()["attempt_id"]

    review_res = client.get(f"/api/v1/mock-test-attempts/{attempt_id}/review")
    assert review_res.status_code == status.HTTP_403_FORBIDDEN


def test_submit_attempt_and_authoritative_scoring(client: TestClient):
    """Verify submission, server-authoritative scoring, and post-submission review."""
    res = client.post("/api/v1/mock-tests/beginner-networking-basics/start?retake=true")
    attempt = res.json()
    attempt_id = attempt["attempt_id"]

    # Submit test without answering all (test partial completion)
    submit_res = client.post(f"/api/v1/mock-test-attempts/{attempt_id}/submit")
    assert submit_res.status_code == status.HTTP_200_OK
    result = submit_res.json()
    assert result["status"] == "SUBMITTED"
    assert result["total_questions"] == 10
    assert result["unanswered_questions"] >= 0
    assert "passed" in result
    assert "topic_breakdown" in result
    assert "difficulty_breakdown" in result

    # Post-submission review is now accessible
    review_res = client.get(f"/api/v1/mock-test-attempts/{attempt_id}/review")
    assert review_res.status_code == status.HTTP_200_OK
    review = review_res.json()
    assert len(review["questions"]) == 10
    for rq in review["questions"]:
        assert rq["explanation"] is not None
        assert len(rq["options"]) > 0
        assert any(opt["is_correct"] for opt in rq["options"])


def test_retake_and_history(client: TestClient):
    """Verify retake creates a fresh sitting and history shows past records."""
    # Start first sitting and submit
    res1 = client.post("/api/v1/mock-tests/beginner-networking-basics/start?retake=true")
    att1_id = res1.json()["attempt_id"]
    client.post(f"/api/v1/mock-test-attempts/{att1_id}/submit")

    # Start fresh retake
    res2 = client.post("/api/v1/mock-tests/beginner-networking-basics/start?retake=true")
    att2_id = res2.json()["attempt_id"]
    assert att2_id != att1_id

    # Check history
    hist_res = client.get("/api/v1/mock-test-attempts/history")
    assert hist_res.status_code == status.HTTP_200_OK
    history = hist_res.json()
    att_ids = [h["attempt_id"] for h in history]
    assert att1_id in att_ids
    assert att2_id in att_ids


def test_practice_mode_generation_for_unanswered(client: TestClient):
    """Verify generating practice exam from unanswered/incorrect questions."""
    res = client.post("/api/v1/mock-tests/beginner-networking-basics/start?retake=true")
    attempt_id = res.json()["attempt_id"]
    client.post(f"/api/v1/mock-test-attempts/{attempt_id}/submit")

    # Generate practice session
    prac_res = client.post(
        f"/api/v1/mock-test-attempts/{attempt_id}/practice?mode=incorrect_or_unanswered"
    )
    assert prac_res.status_code == status.HTTP_200_OK
    prac_data = prac_res.json()
    assert prac_data["attempt_id"] > 0
    assert len(prac_data["questions"]) > 0


def test_security_guards_invalid_options_and_questions(client: TestClient):
    """Verify IDOR protections, invalid option IDs, and post-submission tampering rejection."""
    res = client.post("/api/v1/mock-tests/beginner-networking-basics/start?retake=true")
    attempt_id = res.json()["attempt_id"]
    q1 = res.json()["questions"][0]

    # Invalid option ID that does not belong to question
    bad_opt_res = client.post(
        f"/api/v1/mock-test-attempts/{attempt_id}/save-answer",
        json={"question_id": q1["id"], "selected_option_ids": [999999]},
    )
    assert bad_opt_res.status_code == status.HTTP_400_BAD_REQUEST

    # Question not part of mock test
    bad_q_res = client.post(
        f"/api/v1/mock-test-attempts/{attempt_id}/save-answer",
        json={"question_id": 999999, "selected_option_ids": [1]},
    )
    assert bad_q_res.status_code == status.HTTP_400_BAD_REQUEST

    # Submit test
    client.post(f"/api/v1/mock-test-attempts/{attempt_id}/submit")

    # Attempt to modify answers after submission
    late_save = client.post(
        f"/api/v1/mock-test-attempts/{attempt_id}/save-answer",
        json={"question_id": q1["id"], "selected_option_ids": [q1["options"][0]["id"]]},
    )
    assert late_save.status_code == status.HTTP_400_BAD_REQUEST


def test_blueprints_listing_and_validation(client: TestClient):
    """Verify test blueprints listing and question availability validation."""
    res = client.get("/api/v1/mock-tests/blueprints/list")
    assert res.status_code == status.HTTP_200_OK
    blueprints = res.json()
    assert len(blueprints) >= 2

    bp1_id = blueprints[0]["id"]
    val_res = client.get(f"/api/v1/mock-tests/blueprints/{bp1_id}/validate")
    assert val_res.status_code == status.HTTP_200_OK
    val = val_res.json()
    assert "is_sufficient" in val
    assert "total_required_questions" in val
    assert len(val["rules"]) > 0
