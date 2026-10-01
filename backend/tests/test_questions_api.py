from fastapi import status
from fastapi.testclient import TestClient


def test_list_questions_shields_answer_keys(client: TestClient):
    """
    CRITICAL SECURITY TEST:
    Verify that student-facing question list endpoints strictly omit
    'is_correct' and internal 'explanation' fields.
    """
    response = client.get("/api/v1/questions")
    assert response.status_code == status.HTTP_200_OK

    questions = response.json()
    assert len(questions) >= 10

    for q in questions:
        # Explanation must never be leaked to students prior to exam submission
        assert "explanation" not in q
        assert "options" in q
        assert len(q["options"]) > 0

        # is_correct must never be leaked in options
        for opt in q["options"]:
            assert "is_correct" not in opt
            assert "option_text" in opt
            assert "id" in opt


def test_get_single_question_shields_answer_key(client: TestClient):
    """Verify single question lookup also protects answer keys from inspection."""
    response = client.get("/api/v1/questions/1")
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert "explanation" not in data
    for opt in data["options"]:
        assert "is_correct" not in opt


def test_admin_question_endpoint_exposes_answer_key(client: TestClient):
    """Verify admin endpoint contains full answer key and authoritative rationale."""
    response = client.get("/api/v1/questions/admin/1")
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert "explanation" in data
    assert len(data["explanation"]) > 0

    has_correct_option = any(opt.get("is_correct") is True for opt in data["options"])
    assert has_correct_option is True


def test_question_filtering_by_difficulty_and_tag(client: TestClient):
    """Verify query filtering by difficulty and tag."""
    # Filter by difficulty
    resp_diff = client.get("/api/v1/questions?difficulty=BEGINNER")
    assert resp_diff.status_code == status.HTTP_200_OK
    data_diff = resp_diff.json()
    assert len(data_diff) > 0
    assert all(q["difficulty"] == "BEGINNER" for q in data_diff)

    # Lowercase difficulty test
    resp_diff_lower = client.get("/api/v1/questions?difficulty=beginner")
    assert resp_diff_lower.status_code == status.HTTP_200_OK
    assert len(resp_diff_lower.json()) == len(data_diff)

    # Filter by tag: subnetting
    resp_tag = client.get("/api/v1/questions?tag=subnetting")
    assert resp_tag.status_code == status.HTTP_200_OK
    data_tag = resp_tag.json()
    assert len(data_tag) > 0
    for q in data_tag:
        tag_slugs = [t["slug"] for t in q["tags"]]
        assert "subnetting" in tag_slugs

    # Filter by question type: TRUE_FALSE
    resp_tf = client.get("/api/v1/questions?question_type=TRUE_FALSE")
    assert resp_tf.status_code == status.HTTP_200_OK
    data_tf = resp_tf.json()
    assert len(data_tf) > 0
    assert all(q["question_type"] == "TRUE_FALSE" for q in data_tf)

    # Lowercase question_type test
    resp_tf_lower = client.get("/api/v1/questions?question_type=true_false")
    assert resp_tf_lower.status_code == status.HTTP_200_OK
    assert len(resp_tf_lower.json()) == len(data_tf)
