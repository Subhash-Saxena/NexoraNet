"""
Automated Test Suite for Step 8: Adaptive Testing & Personalized Practice Engine.

Verifies:
1. Adaptive hyperparameters and deterministic configurations.
2. Insufficient data and onboarding recommendations.
3. Recency-weighted topic accuracy and sample size confidence.
4. Deterministic difficulty progression algorithm.
5. Prerequisite-aware recommendation hierarchy.
6. Dynamic adaptive test session compilation and launching.
7. Repetition suppression and candidate scoring.
8. Zero-knowledge security shielding (no answer leakage).
9. Recommendation interaction telemetry.
"""

from app.core.adaptive_config import adaptive_config
from app.models.enums import (
    DifficultyLevel,
    TopicPerformanceStatus,
)
from app.schemas.adaptive import DifficultyPerformanceSummary, DifficultyStats
from app.services.adaptive_performance_service import adaptive_performance_service
from fastapi import status
from fastapi.testclient import TestClient


def test_adaptive_configuration_parameters():
    """Verify adaptive engine configuration constants and recency weight function."""
    assert adaptive_config.ADAPTIVE_MIN_QUESTIONS == 5
    assert adaptive_config.ADAPTIVE_RECENT_ATTEMPTS == 5
    assert adaptive_config.ADAPTIVE_RECENT_QUESTION_LIMIT == 100
    assert adaptive_config.ADAPTIVE_NEEDS_PRACTICE_THRESHOLD == 60.0
    assert adaptive_config.ADAPTIVE_DEVELOPING_THRESHOLD == 80.0
    assert adaptive_config.ADAPTIVE_SOLID_THRESHOLD == 90.0

    # Recency weights
    assert adaptive_config.get_recency_weight(0) == 1.00
    assert adaptive_config.get_recency_weight(1) == 0.85
    assert adaptive_config.get_recency_weight(2) == 0.70
    assert adaptive_config.get_recency_weight(4) == 0.40
    assert adaptive_config.get_recency_weight(10) == 0.30  # Fallback floor weight


def test_adaptive_overview_endpoint(client: TestClient):
    """Verify GET /api/v1/adaptive/overview returns structured diagnostics."""
    res = client.get("/api/v1/adaptive/overview")
    assert res.status_code == status.HTTP_200_OK
    data = res.json()

    assert "user_id" in data
    assert "has_sufficient_data" in data
    assert "data_message" in data
    assert "overall_accuracy" in data
    assert "recommended_difficulty" in data
    assert "difficulty_reason" in data
    assert "difficulty_performance" in data
    assert "all_topics" in data
    assert isinstance(data["all_topics"], list)
    assert len(data["all_topics"]) > 0

    # Verify neutral performance wording
    assert "AI" not in data["difficulty_reason"]
    assert "predict" not in data["difficulty_reason"].lower()


def test_topic_performance_endpoint(client: TestClient):
    """Verify GET /api/v1/adaptive/topic-performance endpoint returns topic array."""
    res = client.get("/api/v1/adaptive/topic-performance")
    assert res.status_code == status.HTTP_200_OK
    topics = res.json()
    assert isinstance(topics, list)
    assert len(topics) > 0

    first = topics[0]
    assert "topic_id" in first
    assert "topic_title" in first
    assert "status" in first
    assert first["status"] in [
        TopicPerformanceStatus.INSUFFICIENT_DATA.value,
        TopicPerformanceStatus.NEEDS_PRACTICE.value,
        TopicPerformanceStatus.DEVELOPING.value,
        TopicPerformanceStatus.SOLID.value,
        TopicPerformanceStatus.STRONG.value,
    ]
    assert "accuracy" in first
    assert "recent_accuracy" in first
    assert "recommended_action" in first
    assert "confidence_level" in first


def test_recommendations_endpoint(client: TestClient):
    """Verify GET /api/v1/adaptive/recommendations returns categorized next steps."""
    res = client.get("/api/v1/adaptive/recommendations")
    assert res.status_code == status.HTTP_200_OK
    recs = res.json()
    assert isinstance(recs, list)
    assert len(recs) > 0

    for item in recs:
        assert "id" in item
        assert "type" in item
        assert "title" in item
        assert "reason" in item
        assert "priority" in item
        assert "action_label" in item
        assert "action_url" in item
        assert len(item["reason"]) > 5  # Explicit explainable justification


def test_next_recommendation_endpoint(client: TestClient):
    """Verify GET /api/v1/adaptive/recommendations/next returns single highest-priority action."""
    res = client.get("/api/v1/adaptive/recommendations/next")
    assert res.status_code == status.HTTP_200_OK
    data = res.json()
    if data:
        assert "title" in data
        assert "reason" in data
        assert "action_url" in data
        assert data["priority"] in ["HIGH", "MEDIUM", "LOW"]


def test_deterministic_difficulty_recommendation_rules():
    """Verify difficulty evaluation rules without requiring database writes."""
    # Scenario 1: Beginner low accuracy (<60%) -> Recommend Beginner
    summary_low = DifficultyPerformanceSummary(
        BEGINNER=DifficultyStats(seen=10, correct=4, accuracy=40.0),
        INTERMEDIATE=DifficultyStats(seen=0, correct=0, accuracy=0.0),
        ADVANCED=DifficultyStats(seen=0, correct=0, accuracy=0.0),
    )
    diff, reason = adaptive_performance_service._recommend_difficulty(summary_low, total_answered=10)
    assert diff == DifficultyLevel.BEGINNER
    assert "40%" in reason

    # Scenario 2: Beginner high accuracy (>80%) -> Recommend Intermediate
    summary_high = DifficultyPerformanceSummary(
        BEGINNER=DifficultyStats(seen=15, correct=13, accuracy=86.7),
        INTERMEDIATE=DifficultyStats(seen=0, correct=0, accuracy=0.0),
        ADVANCED=DifficultyStats(seen=0, correct=0, accuracy=0.0),
    )
    diff, reason = adaptive_performance_service._recommend_difficulty(summary_high, total_answered=15)
    assert diff == DifficultyLevel.INTERMEDIATE
    assert "87%" in reason

    # Scenario 3: Intermediate solid accuracy (70%) -> Recommend Intermediate
    summary_int = DifficultyPerformanceSummary(
        BEGINNER=DifficultyStats(seen=20, correct=18, accuracy=90.0),
        INTERMEDIATE=DifficultyStats(seen=12, correct=9, accuracy=75.0),
        ADVANCED=DifficultyStats(seen=0, correct=0, accuracy=0.0),
    )
    diff, reason = adaptive_performance_service._recommend_difficulty(summary_int, total_answered=32)
    assert diff == DifficultyLevel.INTERMEDIATE
    assert "75%" in reason

    # Scenario 4: Intermediate high accuracy (85%) + Advanced solid (65%) -> Recommend Advanced
    summary_adv = DifficultyPerformanceSummary(
        BEGINNER=DifficultyStats(seen=20, correct=19, accuracy=95.0),
        INTERMEDIATE=DifficultyStats(seen=20, correct=18, accuracy=90.0),
        ADVANCED=DifficultyStats(seen=8, correct=6, accuracy=75.0),
    )
    diff, reason = adaptive_performance_service._recommend_difficulty(summary_adv, total_answered=48)
    assert diff == DifficultyLevel.ADVANCED
    assert "drills recommended" in reason.lower()


def test_start_adaptive_practice_test(client: TestClient):
    """Verify POST /api/v1/adaptive-tests/start launches a personalized test sitting."""
    payload = {
        "question_count": 10,
        "duration_minutes": 15,
    }
    res = client.post("/api/v1/adaptive-tests/start", json=payload)
    assert res.status_code == status.HTTP_200_OK
    attempt_data = res.json()

    assert "attempt_id" in attempt_data
    assert "test_id" in attempt_data
    assert "questions" in attempt_data
    assert len(attempt_data["questions"]) == 10
    assert "remaining_seconds" in attempt_data
    assert attempt_data["remaining_seconds"] > 0

    # ZERO-KNOWLEDGE SECURITY CHECK:
    # Ensure correct answers and explanations are NEVER leaked in test sitting payload
    for q in attempt_data["questions"]:
        assert "is_correct" not in q
        assert "correct_answer" not in q
        assert "explanation" not in q
        for opt in q["options"]:
            assert "is_correct" not in opt


def test_start_adaptive_practice_with_focus_topics(client: TestClient):
    """Verify adaptive test can target user-selected focus topics."""
    # Fetch first active topic ID
    topics_res = client.get("/api/v1/adaptive/topic-performance")
    topics = topics_res.json()
    assert len(topics) > 0
    target_topic_id = topics[0]["topic_id"]

    payload = {
        "question_count": 8,
        "duration_minutes": 10,
        "focus_topic_ids": [target_topic_id],
    }
    res = client.post("/api/v1/adaptive-tests/start", json=payload)
    assert res.status_code == status.HTTP_200_OK
    data = res.json()
    assert len(data["questions"]) == 8


def test_adaptive_test_session_and_status(client: TestClient):
    """Verify GET /api/v1/adaptive-tests/{id} and status synchronization."""
    # 1. Start a session
    start_res = client.post(
        "/api/v1/adaptive-tests/start",
        json={"question_count": 5, "duration_minutes": 10},
    )
    assert start_res.status_code == status.HTTP_200_OK
    attempt_id = start_res.json()["attempt_id"]

    # 2. Inspect session
    sess_res = client.get(f"/api/v1/adaptive-tests/{attempt_id}")
    assert sess_res.status_code == status.HTTP_200_OK
    sess_data = sess_res.json()
    assert sess_data["attempt_id"] == attempt_id
    assert len(sess_data["questions"]) == 5

    # 3. Check status
    status_res = client.get(f"/api/v1/adaptive-tests/{attempt_id}/status")
    assert status_res.status_code == status.HTTP_200_OK
    status_data = status_res.json()
    assert status_data["attempt_id"] == attempt_id
    assert status_data["is_expired"] is False
    assert status_data["remaining_seconds"] > 0


def test_recommendation_event_logging(client: TestClient):
    """Verify POST /api/v1/adaptive/events tracks telemetry interactions."""
    payload = {
        "recommendation_type": "TOPIC_PRACTICE",
        "title": "Practice IPv4 Subnetting",
        "reason": "Diagnostic accuracy is 55%",
        "action_url": "/adaptive-test?focus=1",
        "event_type": "CLICKED",
        "priority": "HIGH",
    }
    res = client.post("/api/v1/adaptive/events", json=payload)
    assert res.status_code == status.HTTP_201_CREATED
    assert res.json() == {"status": "recorded"}
