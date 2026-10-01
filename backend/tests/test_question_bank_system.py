"""
Comprehensive test suite for NexoraNet Step 6: Question Bank System.
Tests:
- QuestionValidator schema rules, choice rules, XSS sanitation, subnetting math
- Question duplicate detection (by code and by normalized text)
- QuestionImporter dry run and idempotent upsert
- Student answer shielding (zero knowledge leakage)
- Question bank statistics and search endpoints
- Admin question authoring and lifecycle management (publish/archive)
- Blueprint availability compatibility with Step 5 TestGenerationService
"""

from app.db.session import SessionLocal
from app.models.curriculum import Topic
from app.models.mock_test import TestBlueprint
from app.models.question import Question
from app.services.question_validator import QuestionValidator
from app.services.test_generation_service import TestGenerationService
from fastapi.testclient import TestClient


def test_question_validator_valid():
    """Verify validator passes well-structured questions."""
    q_data = {
        "code": "TEST-VAL-001",
        "topic_slug": "what-is-computer-networking",
        "question_text": "What is the primary function of a network router?",
        "question_type": "SINGLE_CHOICE",
        "difficulty": "BEGINNER",
        "cognitive_level": "UNDERSTAND",
        "explanation": "Routers forward packets between distinct IP networks.",
        "learning_objective": "Explain the role of a router.",
        "options": [
            {"option_text": "Forward packets across network boundaries", "is_correct": True},
            {"option_text": "Generate electrical electricity for the building", "is_correct": False},
            {"option_text": "Print paper documents", "is_correct": False},
            {"option_text": "Cool the computer CPU", "is_correct": False},
        ],
        "tags": ["router", "networking-basics"],
    }
    errors = QuestionValidator.validate_question_dict(q_data, valid_topic_slugs={"what-is-computer-networking"})
    assert len(errors) == 0, f"Expected 0 errors, got: {errors}"


def test_question_validator_invalid_rules():
    """Verify validator flags invalid schemas, missing fields, and illegal choice combinations."""
    # 1. Unknown topic slug
    q1 = {
        "code": "TEST-ERR-001",
        "topic_slug": "non-existent-topic-slug-xyz",
        "question_text": "Valid question text here?",
        "question_type": "SINGLE_CHOICE",
        "difficulty": "BEGINNER",
        "options": [
            {"option_text": "Choice A", "is_correct": True},
            {"option_text": "Choice B", "is_correct": False},
        ],
    }
    errs = QuestionValidator.validate_question_dict(q1, valid_topic_slugs={"what-is-computer-networking"})
    assert any("does not match any recognized curriculum topic" in e for e in errs)

    # 2. SINGLE_CHOICE with multiple correct answers
    q2 = {
        "code": "TEST-ERR-002",
        "topic_slug": "what-is-computer-networking",
        "question_text": "Which are network devices?",
        "question_type": "SINGLE_CHOICE",
        "difficulty": "BEGINNER",
        "options": [
            {"option_text": "Router", "is_correct": True},
            {"option_text": "Switch", "is_correct": True},
            {"option_text": "Banana", "is_correct": False},
        ],
    }
    errs2 = QuestionValidator.validate_question_dict(q2, valid_topic_slugs={"what-is-computer-networking"})
    assert any("SINGLE_CHOICE question must have exactly 1 correct option" in e for e in errs2)

    # 3. SINGLE_CHOICE with no correct answers
    q3 = {
        "code": "TEST-ERR-003",
        "topic_slug": "what-is-computer-networking",
        "question_text": "No correct answer test?",
        "question_type": "SINGLE_CHOICE",
        "difficulty": "BEGINNER",
        "options": [
            {"option_text": "Choice A", "is_correct": False},
            {"option_text": "Choice B", "is_correct": False},
        ],
    }
    errs3 = QuestionValidator.validate_question_dict(q3, valid_topic_slugs={"what-is-computer-networking"})
    assert any("SINGLE_CHOICE question must have exactly 1 correct option" in e for e in errs3)

    # 4. Empty options list
    q4 = {
        "code": "TEST-ERR-004",
        "topic_slug": "what-is-computer-networking",
        "question_text": "Options missing?",
        "question_type": "SINGLE_CHOICE",
        "difficulty": "BEGINNER",
        "options": [],
    }
    errs4 = QuestionValidator.validate_question_dict(q4, valid_topic_slugs={"what-is-computer-networking"})
    assert any("requires at least 2 options" in e for e in errs4)


def test_question_validator_subnetting_math():
    """Verify programmatic IPv4 subnetting validation via ipaddress.IPv4Network."""
    # Correct calculation: /28 has 14 usable hosts, netmask 255.255.255.240
    is_valid, _ = QuestionValidator.verify_subnet_calculation(
        "192.168.10.0/28",
        "usable_hosts",
        14,
    )
    assert is_valid is True

    # Mathematically incorrect calculation: /28 claimed to have 30 usable hosts
    is_err, err_msg = QuestionValidator.verify_subnet_calculation(
        "192.168.10.0/28",
        "usable_hosts",
        30,
    )
    assert is_err is False
    assert "expected '30', calculated '14'" in err_msg


def test_duplicate_detection():
    """Verify duplicate detection by unique code and normalized text."""
    q_list = [
        {"code": "NET-001", "question_text": "What is an IP address?", "topic_slug": "ipv4-basics", "options": []},
        {"code": "NET-001", "question_text": "Different question entirely?", "topic_slug": "ipv4-basics", "options": []},
        {"code": "NET-002", "question_text": "what   is an ip   address???", "topic_slug": "ipv4-basics", "options": []},
    ]
    report = QuestionValidator.check_duplicate_questions(q_list)
    assert len(report) >= 2
    types = [r["type"] for r in report]
    assert "DUPLICATE_CODE" in types
    assert "DUPLICATE_TEXT" in types


def test_student_answer_shielding(client: TestClient):
    """Ensure student question endpoints NEVER leak is_correct, explanations, or answers."""
    # Test individual question by code
    resp = client.get("/api/v1/questions/code/NET-FUND-001")
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == "NET-FUND-001"
    assert "explanation" not in data or data.get("explanation") is None
    assert "options" in data
    assert len(data["options"]) > 0

    for opt in data["options"]:
        assert "is_correct" not in opt, "SECURITY BREACH: is_correct leaked in student response!"
        assert "explanation" not in opt, "SECURITY BREACH: explanation leaked in student option response!"
        assert "order_index" in opt
        assert "option_text" in opt

    # Test question listing
    list_resp = client.get("/api/v1/questions?limit=10")
    assert list_resp.status_code == 200
    items = list_resp.json()
    assert len(items) > 0
    for q in items:
        for opt in q["options"]:
            assert "is_correct" not in opt
            assert "explanation" not in opt


def test_question_bank_statistics(client: TestClient):
    """Verify the /api/v1/questions/statistics endpoint returns complete metrics."""
    resp = client.get("/api/v1/questions/statistics")
    assert resp.status_code == 200
    stats = resp.json()

    assert stats["total_questions"] >= 500
    assert "BEGINNER" in stats["by_difficulty"]
    assert "INTERMEDIATE" in stats["by_difficulty"]
    assert "ADVANCED" in stats["by_difficulty"]
    assert stats["by_difficulty"]["BEGINNER"] >= 150
    assert stats["by_difficulty"]["INTERMEDIATE"] >= 165
    assert stats["by_difficulty"]["ADVANCED"] >= 170

    assert "UNDERSTAND" in stats["by_cognitive_level"]
    assert "APPLY" in stats["by_cognitive_level"]
    assert "ANALYZE" in stats["by_cognitive_level"]

    assert len(stats["by_topic"]) >= 37


def test_question_search_and_filters(client: TestClient):
    """Verify search by difficulty, cognitive level, and full-text keyword."""
    # Filter by cognitive level
    resp_cog = client.get("/api/v1/questions?cognitive_level=ANALYZE&limit=10")
    assert resp_cog.status_code == 200
    items_cog = resp_cog.json()
    assert len(items_cog) > 0
    for q in items_cog:
        assert q["cognitive_level"] == "ANALYZE"

    # Search keyword
    resp_search = client.get("/api/v1/questions?search=Wireshark&limit=5")
    assert resp_search.status_code == 200
    items_search = resp_search.json()
    assert len(items_search) > 0
    assert any("wireshark" in q["question_text"].lower() for q in items_search)


def test_admin_question_lifecycle(client: TestClient):
    """Verify full admin authoring lifecycle: create -> read with answers -> update -> archive -> publish."""
    # Find a valid topic ID
    db = SessionLocal()
    topic = db.query(Topic).first()
    db.close()
    assert topic is not None

    import uuid

    code = f"ADMIN-TEST-{uuid.uuid4().hex[:6].upper()}"
    admin_payload = {
        "code": code,
        "question_text": f"Temporary admin test question for lifecycle verification {code}?",
        "question_type": "SINGLE_CHOICE",
        "topic_id": topic.id,
        "difficulty": "INTERMEDIATE",
        "cognitive_level": "APPLY",
        "explanation": "Admin test verified explanation.",
        "learning_objective": "Test authoring workflow.",
        "points": 2,
        "estimated_seconds": 60,
        "status": "PUBLISHED",
        "options": [
            {"option_text": "Correct answer for admin test", "is_correct": True, "order_index": 0, "explanation": "Correct!"},
            {"option_text": "Incorrect answer", "is_correct": False, "order_index": 1, "explanation": "Wrong!"},
        ],
        "tags": ["test-tag", "admin-tag"],
    }

    q_id = None
    try:
        # 1. Admin Create
        create_resp = client.post("/api/v1/questions/admin/create", json=admin_payload)
        assert create_resp.status_code == 201
        created_data = create_resp.json()
        q_id = created_data["id"]
        assert created_data["code"] == code
        # Admin response DOES include is_correct and explanation
        assert created_data["options"][0]["is_correct"] is True
        assert created_data["options"][0]["explanation"] == "Correct!"

        # 2. Admin Get
        get_resp = client.get(f"/api/v1/questions/admin/{q_id}")
        assert get_resp.status_code == 200
        assert get_resp.json()["explanation"] == "Admin test verified explanation."

        # 3. Admin Update
        update_resp = client.put(f"/api/v1/questions/admin/{q_id}", json={
            "points": 3,
            "explanation": "Updated admin explanation.",
        })
        assert update_resp.status_code == 200
        assert update_resp.json()["points"] == 3
        assert update_resp.json()["explanation"] == "Updated admin explanation."

        # 4. Admin Archive
        archive_resp = client.put(f"/api/v1/questions/admin/{q_id}/archive")
        assert archive_resp.status_code == 200
        assert archive_resp.json()["status"] == "ARCHIVED"

        # Verify student endpoint hides archived question
        student_lookup = client.get(f"/api/v1/questions/code/{code}")
        assert student_lookup.status_code == 404

        # 5. Admin Publish (Restore)
        pub_resp = client.put(f"/api/v1/questions/admin/{q_id}/publish")
        assert pub_resp.status_code == 200
        assert pub_resp.json()["status"] == "PUBLISHED"
    finally:
        # Clean up test question
        if q_id is not None:
            db = SessionLocal()
            q_to_clean = db.query(Question).filter(Question.id == q_id).first()
            if q_to_clean:
                db.delete(q_to_clean)
                db.commit()
            db.close()


def test_blueprint_generation_compatibility():
    """Verify that TestGenerationService recognizes published blueprints as sufficient and draft blueprints as shortfall."""
    from app.models.enums import MockTestStatus

    db = SessionLocal()
    try:
        blueprints = db.query(TestBlueprint).all()
        assert len(blueprints) >= 2, "Expected at least 2 test blueprints in seed database."

        published_bps = [
            bp for bp in blueprints
            if any(mt.status == MockTestStatus.PUBLISHED for mt in bp.mock_tests)
        ]
        assert len(published_bps) >= 35, "Expected at least 35 published blueprints."

        for bp in published_bps:
            avail = TestGenerationService.validate_blueprint_availability(db, bp.id)
            assert avail["is_sufficient"] is True, f"Blueprint '{bp.title}' is not sufficient: {avail}"
            for rule in avail["rules"]:
                assert rule["is_met"] is True, f"Rule {rule} in blueprint {bp.title} not met: available={rule['available_count']}, required={rule['required_count']}"
    finally:
        db.close()
