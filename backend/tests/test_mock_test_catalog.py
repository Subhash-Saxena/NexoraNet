from fastapi import status
from fastapi.testclient import TestClient


def test_catalog_listing_and_category_filtering(client: TestClient):
    """Verify that catalog listing supports all required category filters."""
    # List all
    res = client.get("/api/v1/mock-tests")
    assert res.status_code == status.HTTP_200_OK
    all_tests = res.json()
    assert len(all_tests) >= 40

    # Category: recommended
    res_rec = client.get("/api/v1/mock-tests?category=recommended")
    assert res_rec.status_code == status.HTTP_200_OK
    rec_tests = res_rec.json()
    assert len(rec_tests) > 0
    assert all(t["status"] == "PUBLISHED" for t in rec_tests)

    # Category: beginner
    res_beg = client.get("/api/v1/mock-tests?category=beginner")
    assert res_beg.status_code == status.HTTP_200_OK
    beg_tests = res_beg.json()
    assert len(beg_tests) > 0
    assert all(t["difficulty"] == "BEGINNER" for t in beg_tests)

    # Category: intermediate
    res_int = client.get("/api/v1/mock-tests?category=intermediate")
    assert res_int.status_code == status.HTTP_200_OK
    int_tests = res_int.json()
    assert len(int_tests) > 0
    assert all(t["difficulty"] == "INTERMEDIATE" for t in int_tests)

    # Category: advanced
    res_adv = client.get("/api/v1/mock-tests?category=advanced")
    assert res_adv.status_code == status.HTTP_200_OK
    adv_tests = res_adv.json()
    assert len(adv_tests) > 0
    assert all(t["difficulty"] == "ADVANCED" for t in adv_tests)

    # Category: full_mocks
    res_full = client.get("/api/v1/mock-tests?category=full_mocks")
    assert res_full.status_code == status.HTTP_200_OK
    full_tests = res_full.json()
    assert len(full_tests) >= 3
    assert all(t["test_type"] == "FULL_MOCK" for t in full_tests)


def test_catalog_multi_attribute_filtering(client: TestClient):
    """Verify combined difficulty, duration, and keyword search filters."""
    # Difficulty + Type filter
    res = client.get("/api/v1/mock-tests?difficulty=INTERMEDIATE&test_type=TOPIC")
    assert res.status_code == status.HTTP_200_OK
    tests = res.json()
    assert all(t["difficulty"] == "INTERMEDIATE" and t["test_type"] == "TOPIC" for t in tests)

    # Duration range filter: 15 to 30 mins
    res_dur = client.get("/api/v1/mock-tests?duration_min=15&duration_max=30")
    assert res_dur.status_code == status.HTTP_200_OK
    dur_tests = res_dur.json()
    assert all(15 <= t["duration_minutes"] <= 30 for t in dur_tests)

    # Keyword search across title/description/tags/code
    res_search = client.get("/api/v1/mock-tests?q=wireshark")
    assert res_search.status_code == status.HTTP_200_OK
    search_tests = res_search.json()
    assert len(search_tests) > 0


def test_catalog_metadata_endpoints(client: TestClient):
    """Verify /categories, /topics, /difficulties, /types, /filter-options, and /statistics."""
    # /categories
    res_cat = client.get("/api/v1/mock-tests/categories")
    assert res_cat.status_code == status.HTTP_200_OK
    cats = res_cat.json()
    cat_keys = {c["key"] for c in cats}
    assert {"all", "recommended", "beginner", "intermediate", "advanced", "comprehensive", "full_mocks"}.issubset(cat_keys)

    # /topics
    res_top = client.get("/api/v1/mock-tests/topics")
    assert res_top.status_code == status.HTTP_200_OK
    topics = res_top.json()
    assert len(topics) > 10

    # /difficulties
    res_diff = client.get("/api/v1/mock-tests/difficulties")
    assert res_diff.status_code == status.HTTP_200_OK
    diffs = res_diff.json()
    assert len(diffs) >= 3

    # /types
    res_type = client.get("/api/v1/mock-tests/types")
    assert res_type.status_code == status.HTTP_200_OK
    types = res_type.json()
    assert len(types) >= 4

    # /filter-options
    res_filters = client.get("/api/v1/mock-tests/filter-options")
    assert res_filters.status_code == status.HTTP_200_OK
    f_data = res_filters.json()
    assert "categories" in f_data
    assert "topics" in f_data
    assert "difficulties" in f_data
    assert "types" in f_data
    assert "duration_ranges" in f_data

    # /statistics
    res_stats = client.get("/api/v1/mock-tests/statistics")
    assert res_stats.status_code == status.HTTP_200_OK
    s_data = res_stats.json()
    assert s_data["total_tests"] >= 46
    assert s_data["ready_tests"] >= 35
    assert s_data["total_questions_represented"] > 500


def test_mock_test_blueprint_and_preview_endpoints(client: TestClient):
    """Verify test blueprint retrieval and safe preview without answer spoilers."""
    # Test preview for full mock
    res = client.get("/api/v1/mock-tests/full-networking-mock-exam/preview")
    assert res.status_code == status.HTTP_200_OK
    preview = res.json()
    assert preview["code"] == "FULL-MOCK-001"
    assert preview["total_questions"] == 50
    assert preview["is_ready"] is True
    assert preview["shortfall"] == 0
    assert len(preview["syllabus_rules"]) > 0
    assert len(preview["what_you_will_practice"]) > 0

    # Zero spoilers check: No question text, options, or correct answers in preview
    assert "questions" not in preview
    for rule in preview["syllabus_rules"]:
        assert "topic_title" in rule
        assert "question_count" in rule
        assert "correct_answer" not in rule

    # Test blueprint endpoint
    res_bp = client.get("/api/v1/mock-tests/full-networking-mock-exam/blueprint")
    assert res_bp.status_code == status.HTTP_200_OK
    bp = res_bp.json()
    assert bp["total_questions"] == 50
    assert len(bp["rules"]) > 0


def test_start_attempt_readiness_validation(client: TestClient):
    """Verify starting a draft test with pool shortfall raises HTTP 400 Bad Request."""
    # BEGINNER-DNS-001 (slug: dns-basics) is DRAFT due to question bank pool shortfall
    res = client.post("/api/v1/mock-tests/dns-basics/start")
    assert res.status_code == status.HTTP_400_BAD_REQUEST
    assert "not ready" in res.json()["detail"].lower()


def test_attempt_lifecycle_continue_and_retake(client: TestClient):
    """Verify continue active attempt, attempt history, and retake creating separate history record."""
    test_slug = "networking-fundamentals"

    # 1. Start fresh attempt
    start_res = client.post(f"/api/v1/mock-tests/{test_slug}/start")
    assert start_res.status_code == status.HTTP_200_OK
    att1 = start_res.json()
    att1_id = att1["attempt_id"]

    # 2. Resuming without retake returns the exact same attempt
    resume_res = client.post(f"/api/v1/mock-tests/{test_slug}/start")
    assert resume_res.status_code == status.HTTP_200_OK
    att_resumed = resume_res.json()
    assert att_resumed["attempt_id"] == att1_id

    # 3. Check attempt history endpoint
    hist_res = client.get(f"/api/v1/mock-tests/{test_slug}/attempt-history")
    assert hist_res.status_code == status.HTTP_200_OK
    history = hist_res.json()
    assert any(h["attempt_id"] == att1_id for h in history)

    # 4. Retake creates a fresh sitting
    retake_res = client.post(f"/api/v1/mock-tests/{test_slug}/start?retake=true")
    assert retake_res.status_code == status.HTTP_200_OK
    att2 = retake_res.json()
    att2_id = att2["attempt_id"]
    assert att2_id != att1_id

    # 5. History should now contain both attempts
    hist2_res = client.get(f"/api/v1/mock-tests/{test_slug}/attempt-history")
    assert hist2_res.status_code == status.HTTP_200_OK
    history2 = hist2_res.json()
    assert len(history2) >= 2
    attempt_ids = [h["attempt_id"] for h in history2]
    assert att1_id in attempt_ids
    assert att2_id in attempt_ids
