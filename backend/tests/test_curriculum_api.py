from fastapi import status
from fastapi.testclient import TestClient


def test_list_courses(client: TestClient):
    """Verify curriculum courses list endpoint."""
    response = client.get("/api/v1/courses")
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1

    first_course = data[0]
    assert first_course["slug"] == "networking-cybersecurity"
    assert first_course["modules_count"] > 0


def test_get_course_detail(client: TestClient):
    """Verify course detail lookup by slug."""
    response = client.get("/api/v1/courses/networking-cybersecurity")
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["title"] == "Computer Networking & Cybersecurity"
    assert len(data["modules"]) >= 15


def test_list_topics_and_filtering(client: TestClient):
    """Verify topics listing and filtering by difficulty."""
    # List all topics
    response = client.get("/api/v1/topics")
    assert response.status_code == status.HTTP_200_OK
    all_topics = response.json()
    assert len(all_topics) >= 100

    # Filter by difficulty: BEGINNER (case-insensitive test)
    resp_beg = client.get("/api/v1/topics?difficulty=BEGINNER")
    assert resp_beg.status_code == status.HTTP_200_OK
    beg_topics = resp_beg.json()
    assert len(beg_topics) > 0
    assert all(t["difficulty"] == "BEGINNER" for t in beg_topics)

    # Lowercase filter test
    resp_beg_lower = client.get("/api/v1/topics?difficulty=beginner")
    assert resp_beg_lower.status_code == status.HTTP_200_OK
    assert len(resp_beg_lower.json()) == len(beg_topics)

    # Filter by difficulty: ADVANCED
    resp_adv = client.get("/api/v1/topics?difficulty=ADVANCED")
    assert resp_adv.status_code == status.HTTP_200_OK
    adv_topics = resp_adv.json()
    assert len(adv_topics) > 0
    assert all(t["difficulty"] == "ADVANCED" for t in adv_topics)


def test_get_topic_detail_with_lessons(client: TestClient):
    """Verify topic detail includes associated lesson items."""
    response = client.get("/api/v1/topics/seven-osi-layers")
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["slug"] == "seven-osi-layers"
    assert "lessons" in data
    assert len(data["lessons"]) >= 1
    assert data["lessons"][0]["slug"] == "seven-layers-osi-model"


def test_get_nonexistent_course_404(client: TestClient):
    """Verify unknown course returns HTTP 404."""
    response = client.get("/api/v1/courses/unknown-course-1234")
    assert response.status_code == status.HTTP_404_NOT_FOUND
