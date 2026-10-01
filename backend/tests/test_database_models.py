from datetime import datetime, timezone

import pytest
from app.db.session import SessionLocal
from app.models import (
    AttemptStatus,
    CognitiveLevel,
    ContentType,
    Course,
    DifficultyLevel,
    Lesson,
    MockTest,
    MockTestAttempt,
    Module,
    Question,
    QuestionOption,
    QuestionTag,
    StudentAnswer,
    TestBlueprint,
    TestBlueprintTopic,
    TestResult,
    Topic,
    User,
)
from sqlalchemy.exc import IntegrityError


@pytest.fixture
def db_session():
    """Provides a fresh transactional session rolled back after test."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


def test_course_module_topic_lesson_hierarchy(db_session):
    """Test full curriculum hierarchy creation and relationships."""
    course = Course(
        title="Test Advanced Defense Course",
        slug="test-advanced-defense",
        description="Testing curriculum hierarchy.",
        level=DifficultyLevel.ADVANCED,
        estimated_hours=50,
    )
    db_session.add(course)
    db_session.flush()
    assert course.id is not None

    module = Module(
        course_id=course.id,
        title="Test Threat Hunting",
        slug="test-threat-hunting",
        order_index=1,
        difficulty=DifficultyLevel.ADVANCED,
    )
    db_session.add(module)
    db_session.flush()
    assert module.id is not None

    topic = Topic(
        module_id=module.id,
        title="Test C2 Beacon Detection",
        slug="test-c2-beacon-detection",
        difficulty=DifficultyLevel.ADVANCED,
        order_index=1,
    )
    db_session.add(topic)
    db_session.flush()
    assert topic.id is not None

    lesson = Lesson(
        topic_id=topic.id,
        title="Analyzing High-Jitter Beacons",
        slug="analyzing-high-jitter-beacons",
        content="# Beacon Detection\nLearn how jitter obfuscates C2 intervals.",
        content_type=ContentType.LESSON,
        order_index=1,
        difficulty=DifficultyLevel.ADVANCED,
    )
    db_session.add(lesson)
    db_session.flush()

    assert len(course.modules) == 1
    assert len(module.topics) == 1
    assert len(topic.lessons) == 1
    assert topic.lessons[0].title == "Analyzing High-Jitter Beacons"


def test_duplicate_slug_constraint_prevention(db_session):
    """Verify unique constraint prevents duplicate slugs under same parent."""
    course = Course(
        title="Unique Course 1",
        slug="unique-course-slug",
        level=DifficultyLevel.BEGINNER,
    )
    db_session.add(course)
    db_session.flush()

    # Attempting to add duplicate course slug should fail
    duplicate_course = Course(
        title="Unique Course 2",
        slug="unique-course-slug",
        level=DifficultyLevel.BEGINNER,
    )
    db_session.add(duplicate_course)
    with pytest.raises(IntegrityError):
        db_session.flush()

    db_session.rollback()


def test_question_and_options_creation(db_session):
    """Test Question, Options, and Tag association modeling."""
    topic = db_session.query(Topic).first()
    assert topic is not None, "Topics should be seeded"

    tag = QuestionTag(name="Test Security Tag", slug="test-sec-tag")
    db_session.add(tag)
    db_session.flush()

    question = Question(
        topic_id=topic.id,
        question_text="What does a SYN scan send to an open port?",
        question_type="SINGLE_CHOICE",
        difficulty=DifficultyLevel.INTERMEDIATE,
        cognitive_level=CognitiveLevel.UNDERSTAND,
        explanation="An open port responds with SYN-ACK to an initial SYN packet.",
        points=2,
    )
    question.tags.append(tag)
    db_session.add(question)
    db_session.flush()

    opt1 = QuestionOption(
        question_id=question.id, option_text="SYN-ACK", is_correct=True, order_index=1
    )
    opt2 = QuestionOption(
        question_id=question.id, option_text="RST-ACK", is_correct=False, order_index=2
    )
    db_session.add_all([opt1, opt2])
    db_session.flush()

    assert len(question.options) == 2
    assert question.options[0].is_correct is True
    assert len(question.tags) == 1
    assert question.tags[0].name == "Test Security Tag"


def test_mock_test_attempt_and_result_workflow(db_session):
    """Test student attempt creation, answer recording, and test scoring calculation."""
    user = db_session.query(User).first()
    assert user is not None, "Seeded user should exist"

    mock_test = db_session.query(MockTest).first()
    assert mock_test is not None, "Seeded mock test should exist"

    now = datetime.now(timezone.utc)
    attempt = MockTestAttempt(
        mock_test_id=mock_test.id,
        user_id=user.id,
        started_at=now,
        expires_at=now,
        status=AttemptStatus.SUBMITTED,
        score=2.0,
        percentage=100.0,
    )
    db_session.add(attempt)
    db_session.flush()

    question = db_session.query(Question).first()
    answer = StudentAnswer(
        attempt_id=attempt.id,
        question_id=question.id,
        answer_data='{"selected_option_id": 1}',
        is_correct=True,
        points_earned=question.points,
        answered_at=now,
    )
    db_session.add(answer)
    db_session.flush()

    result = TestResult(
        attempt_id=attempt.id,
        correct_answers=1,
        incorrect_answers=0,
        unanswered=0,
        total_questions=1,
        score=2.0,
        percentage=100.0,
        time_taken_seconds=120,
    )
    db_session.add(result)
    db_session.flush()

    assert attempt.result is not None
    assert attempt.result.score == 2.0
    assert len(attempt.student_answers) == 1


def test_test_blueprint_and_topic_rules(db_session):
    """Test blueprint creation with topic question count distributions."""
    topic = db_session.query(Topic).first()
    blueprint = TestBlueprint(
        title="Custom Certification Blueprint",
        slug="custom-cert-blueprint",
        total_questions=15,
        duration_minutes=30,
        difficulty=DifficultyLevel.BEGINNER,
    )
    db_session.add(blueprint)
    db_session.flush()

    rule = TestBlueprintTopic(
        blueprint_id=blueprint.id,
        topic_id=topic.id,
        question_count=5,
        difficulty=DifficultyLevel.BEGINNER,
    )
    db_session.add(rule)
    db_session.flush()

    assert len(blueprint.topics) == 1
    assert blueprint.topics[0].question_count == 5
