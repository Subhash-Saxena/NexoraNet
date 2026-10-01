from fastapi import status
from fastapi.testclient import TestClient


def test_list_mock_tests(client: TestClient):
    """Verify list mock tests endpoint."""
    response = client.get("/api/v1/mock-tests")
    assert response.status_code == status.HTTP_200_OK

    tests = response.json()
    assert len(tests) >= 2
    slugs = [t["slug"] for t in tests]
    assert "beginner-networking-basics" in slugs
    assert "intermediate-networking-subnetting" in slugs


def test_get_mock_test_detail_with_shielded_questions(client: TestClient):
    """
    Verify mock test detail returns configured question set
    while protecting answer keys and explanations from students.
    """
    response = client.get("/api/v1/mock-tests/beginner-networking-basics")
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["title"] == "Beginner Networking Basics"
    assert data["duration_minutes"] == 30
    assert len(data["questions"]) >= 5

    # Check question shielding inside test session
    for q in data["questions"]:
        assert "explanation" not in q
        assert len(q["options"]) > 0
        for opt in q["options"]:
            assert "is_correct" not in opt


def test_mock_test_not_found(client: TestClient):
    """Verify unknown mock test returns 404."""
    response = client.get("/api/v1/mock-tests/nonexistent-test-slug")
    assert response.status_code == status.HTTP_404_NOT_FOUND
