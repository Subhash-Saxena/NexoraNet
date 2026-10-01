from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_get_courses_and_detail():
    """Verify course list and individual course inspection."""
    response = client.get("/api/v1/courses")
    assert response.status_code == 200
    courses = response.json()
    assert len(courses) >= 1
    course_slug = courses[0]["slug"]

    detail_res = client.get(f"/api/v1/courses/{course_slug}")
    assert detail_res.status_code == 200
    detail = detail_res.json()
    assert detail["title"] == "Computer Networking & Cybersecurity"
    assert len(detail["modules"]) >= 19


def test_get_module_detail():
    """Verify module lookup by slug or ID."""
    response = client.get("/api/v1/modules/networking-fundamentals")
    assert response.status_code == 200
    module = response.json()
    assert module["title"] == "Networking Fundamentals"
    assert len(module["topics"]) >= 1

    # Nonexistent module returns 404
    missing_res = client.get("/api/v1/modules/nonexistent-module-xyz")
    assert missing_res.status_code == 404


def test_get_topic_detail_with_prerequisites():
    """Verify topic detail returns prerequisites, objectives, and lesson list."""
    response = client.get("/api/v1/topics/subnetting")
    assert response.status_code == 200
    topic = response.json()
    assert topic["title"] == "Subnetting"
    assert topic["estimated_minutes"] >= 30
    assert len(topic["learning_objectives"]) >= 1
    assert topic["security_relevance"] is not None

    # Check prerequisites
    prereqs = topic["prerequisites"]
    assert len(prereqs) >= 1
    assert any(p["slug"] == "ipv4-basics" for p in prereqs)

    # Check topic lessons endpoint
    lessons_res = client.get("/api/v1/topics/subnetting/lessons")
    assert lessons_res.status_code == 200
    assert len(lessons_res.json()) >= 1


def test_get_lesson_detail_and_navigation():
    """Verify lesson detail returns markdown content, breadcrumbs, and next/prev."""
    response = client.get("/api/v1/lessons/what-is-computer-networking-intro")
    assert response.status_code == 200
    lesson = response.json()
    assert "What is Computer Networking?" in lesson["title"]
    assert "# What is Computer Networking?" in lesson["content"]
    assert lesson["topic_slug"] == "what-is-computer-networking"
    assert lesson["module_slug"] == "networking-fundamentals"

    # Test next and previous endpoints
    next_res = client.get("/api/v1/lessons/what-is-computer-networking-intro/next")
    assert next_res.status_code in (200, 404)

    # Nonexistent lesson returns 404
    missing = client.get("/api/v1/lessons/nonexistent-lesson-abc")
    assert missing.status_code == 404


def test_mark_lesson_started_and_completed():
    """Verify starting and completing a lesson updates progress correctly."""
    from app.db.session import SessionLocal
    from app.models.progress import LessonProgress
    from app.models.user import User

    # 1. Fetch lesson
    lesson_res = client.get("/api/v1/lessons/what-is-computer-networking-intro")
    assert lesson_res.status_code == 200
    lesson_id = lesson_res.json()["id"]

    # Reset progress for test idempotency
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == "student_dev").first()
        if user:
            db.query(LessonProgress).filter(
                LessonProgress.user_id == user.id,
                LessonProgress.lesson_id == lesson_id,
            ).delete()
            db.commit()
    finally:
        db.close()

    # 2. Mark started
    start_res = client.post(f"/api/v1/lessons/{lesson_id}/start")
    assert start_res.status_code == 200
    assert start_res.json()["status"] == "IN_PROGRESS"

    # 3. Mark completed
    complete_res = client.post(f"/api/v1/lessons/{lesson_id}/complete")
    assert complete_res.status_code == 200
    assert complete_res.json()["status"] == "COMPLETED"

    # 4. Verify lesson detail reflects completed status
    recheck_res = client.get(f"/api/v1/lessons/{lesson_id}")
    assert recheck_res.status_code == 200
    assert recheck_res.json()["status"] == "COMPLETED"

    # 5. Cannot complete nonexistent lesson
    invalid_res = client.post("/api/v1/lessons/999999/complete")
    assert invalid_res.status_code == 404


def test_learning_progress_calculation():
    """Verify course progress does not exceed 100% and reports tiered stats."""
    response = client.get("/api/v1/learning/progress")
    assert response.status_code == 200
    data = response.json()

    assert "overall_percentage" in data
    assert 0.0 <= data["overall_percentage"] <= 100.0
    assert data["total_lessons"] >= 36
    assert data["completed_lessons"] >= 0
    assert data["remaining_lessons"] <= data["total_lessons"]

    # Verify tiered levels
    assert data["beginner_progress"]["level"].upper() == "BEGINNER"
    assert 0.0 <= data["beginner_progress"]["percentage"] <= 100.0
    assert data["intermediate_progress"]["level"].upper() == "INTERMEDIATE"
    assert data["advanced_progress"]["level"].upper() == "ADVANCED"

    # Verify Continue Learning resolution
    if data["continue_learning"]:
        cl = data["continue_learning"]
        assert "lesson_title" in cl
        assert "topic_title" in cl
        assert "module_title" in cl


def test_curriculum_search():
    """Verify search returns matched topics, lessons, and modules."""
    # Search for TCP
    response = client.get("/api/v1/learning/search?q=TCP")
    assert response.status_code == 200
    data = response.json()
    assert data["total_results"] >= 1
    types_found = {item["type"] for item in data["results"]}
    assert "lesson" in types_found or "topic" in types_found

    # Search with difficulty filter
    filtered_res = client.get("/api/v1/learning/search?q=TCP&difficulty=intermediate")
    assert filtered_res.status_code == 200
    for item in filtered_res.json()["results"]:
        assert item["difficulty"].upper() == "INTERMEDIATE"


def test_bookmark_lifecycle():
    """Verify bookmarking, listing, and unbookmarking a lesson."""
    lesson_res = client.get("/api/v1/lessons/what-is-computer-networking-intro")
    lesson_id = lesson_res.json()["id"]

    # 1. Add bookmark
    bm_res = client.post(f"/api/v1/lessons/{lesson_id}/bookmark")
    assert bm_res.status_code == 200
    assert bm_res.json()["is_bookmarked"] is True

    # 2. List bookmarks
    list_res = client.get("/api/v1/learning/bookmarks")
    assert list_res.status_code == 200
    bookmarks = list_res.json()
    assert any(b["lesson_id"] == lesson_id for b in bookmarks)

    # 3. Remove bookmark
    del_res = client.delete(f"/api/v1/lessons/{lesson_id}/bookmark")
    assert del_res.status_code == 200
    assert del_res.json()["is_bookmarked"] is False

    # 4. Confirm removed
    relist_res = client.get("/api/v1/learning/bookmarks")
    assert relist_res.status_code == 200
    assert not any(b["lesson_id"] == lesson_id for b in relist_res.json())
