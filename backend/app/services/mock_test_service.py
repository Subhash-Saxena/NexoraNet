from typing import Any

from sqlalchemy import or_
from sqlalchemy.orm import Session, selectinload

from app.models.enums import DifficultyLevel, MockTestStatus, MockTestType
from app.models.mock_test import MockTest, MockTestAttempt, MockTestQuestion
from app.models.question import Question
from app.schemas.mock_test import (
    MockTestBrief,
    MockTestDetail,
    StudentOptionBrief,
    StudentQuestionPayload,
)


class MockTestService:
    """Service layer managing mock examination catalogs and metadata."""

    @staticmethod
    def list_mock_tests(
        db: Session,
        difficulty: str | None = None,
        test_type: str | None = None,
        q: str | None = None,
        user_id: int | None = None,
    ) -> list[MockTestBrief]:
        """Query and return all published mock examinations with topic and attempt metadata."""
        query = (
            db.query(MockTest)
            .options(
                selectinload(MockTest.test_questions)
                .selectinload(MockTestQuestion.question)
                .selectinload(Question.topic)
            )
            .filter(MockTest.status == MockTestStatus.PUBLISHED)
        )

        if difficulty:
            try:
                diff_enum = DifficultyLevel(difficulty.upper())
                query = query.filter(MockTest.difficulty == diff_enum)
            except ValueError:
                return []

        if test_type:
            try:
                type_enum = MockTestType(test_type.upper())
                query = query.filter(MockTest.test_type == type_enum)
            except ValueError:
                return []

        if q and q.strip():
            term = f"%{q.strip()}%"
            query = query.filter(
                or_(
                    MockTest.title.ilike(term),
                    MockTest.description.ilike(term),
                )
            )

        mock_tests = query.order_by(MockTest.id.asc()).all()

        # Query user latest attempts if user_id is provided
        user_attempts: dict[int, MockTestAttempt] = {}
        if user_id:
            recent_attempts = (
                db.query(MockTestAttempt)
                .filter(MockTestAttempt.user_id == user_id)
                .order_by(MockTestAttempt.id.desc())
                .all()
            )
            for att in recent_attempts:
                if att.mock_test_id not in user_attempts:
                    user_attempts[att.mock_test_id] = att

        results: list[MockTestBrief] = []
        for mt in mock_tests:
            # Extract distinct topic titles
            topics: set[str] = set()
            for tq in mt.test_questions:
                if tq.question and tq.question.topic:
                    topics.add(tq.question.topic.title)

            latest_att = user_attempts.get(mt.id)
            results.append(
                MockTestBrief(
                    id=mt.id,
                    title=mt.title,
                    slug=mt.slug,
                    description=mt.description,
                    difficulty=mt.difficulty,
                    test_type=mt.test_type,
                    duration_minutes=mt.duration_minutes,
                    total_questions=len(mt.test_questions) or mt.total_questions,
                    passing_percentage=mt.passing_percentage,
                    status=mt.status,
                    topics_covered=sorted(topics),
                    latest_attempt_score=latest_att.score if latest_att else None,
                    latest_attempt_status=latest_att.status.value if latest_att else None,
                )
            )

        return results

    @staticmethod
    def get_mock_test_detail(
        db: Session,
        test_id_or_slug: str | int,
        user_id: int | None = None,
    ) -> MockTestDetail | None:
        """Fetch complete mock test metadata and topic distribution."""
        query = (
            db.query(MockTest)
            .options(
                selectinload(MockTest.test_questions)
                .selectinload(MockTestQuestion.question)
                .selectinload(Question.topic),
                selectinload(MockTest.test_questions)
                .selectinload(MockTestQuestion.question)
                .selectinload(Question.options),
            )
            .filter(MockTest.status == MockTestStatus.PUBLISHED)
        )

        if isinstance(test_id_or_slug, int) or str(test_id_or_slug).isdigit():
            mt = query.filter(MockTest.id == int(test_id_or_slug)).first()
        else:
            mt = query.filter(MockTest.slug == str(test_id_or_slug)).first()

        if not mt:
            return None

        # Build topic distribution breakdown and shielded questions
        topic_counts: dict[str, int] = {}
        questions_payload: list[StudentQuestionPayload] = []
        for idx, tq in enumerate(mt.test_questions, start=1):
            if tq.question:
                q = tq.question
                if q.topic:
                    t_name = q.topic.title
                    topic_counts[t_name] = topic_counts.get(t_name, 0) + 1
                else:
                    t_name = "General"

                shielded_opts = [
                    StudentOptionBrief(
                        id=opt.id,
                        option_text=opt.option_text,
                        order_index=opt.order_index,
                    )
                    for opt in q.options
                ]
                questions_payload.append(
                    StudentQuestionPayload(
                        id=q.id,
                        question_number=idx,
                        question_text=q.question_text,
                        question_type=q.question_type,
                        points=tq.points or q.points or 1,
                        topic_title=t_name,
                        difficulty=q.difficulty,
                        options=shielded_opts,
                    )
                )

        topics_breakdown: list[dict[str, Any]] = [
            {"topic": name, "question_count": count}
            for name, count in sorted(topic_counts.items())
        ]

        # Tags list
        tags_list: list[str] = []
        if mt.tags:
            try:
                import json
                loaded = json.loads(mt.tags)
                if isinstance(loaded, list):
                    tags_list = loaded
            except (json.JSONDecodeError, ValueError, TypeError):
                tags_list = [t.strip() for t in mt.tags.split(",") if t.strip()]

        # Practice points
        practice_points = [
            f"Mastering core principles of {topic_name}"
            for topic_name in sorted(topic_counts.keys())[:4]
        ]
        if mt.test_type == MockTestType.FULL_MOCK:
            practice_points.append(
                f"Full-length exam time management ({mt.duration_minutes} minutes, {mt.total_questions} questions)"
            )
        practice_points.append(f"Minimum passing threshold: {int(mt.passing_percentage)}%")

        # Readiness
        is_ready = mt.status == MockTestStatus.PUBLISHED and len(mt.test_questions) > 0
        shortfall = max(0, mt.total_questions - len(mt.test_questions)) if not is_ready else 0

        latest_att = None
        active_attempt_id = None
        attempt_count = 0

        if user_id:
            from datetime import datetime, timezone
            now = datetime.now(timezone.utc)
            user_atts = (
                db.query(MockTestAttempt)
                .filter(
                    MockTestAttempt.mock_test_id == mt.id,
                    MockTestAttempt.user_id == user_id,
                )
                .order_by(MockTestAttempt.id.desc())
                .all()
            )
            attempt_count = len(user_atts)
            if user_atts:
                latest_att = user_atts[0]
                for att in user_atts:
                    if att.status.value == "IN_PROGRESS":
                        exp = att.expires_at
                        if exp.tzinfo is None:
                            exp = exp.replace(tzinfo=timezone.utc)
                        if now < exp:
                            active_attempt_id = att.id
                            break

        return MockTestDetail(
            id=mt.id,
            code=mt.code,
            title=mt.title,
            slug=mt.slug,
            description=mt.description,
            difficulty=mt.difficulty,
            test_type=mt.test_type,
            duration_minutes=mt.duration_minutes,
            total_questions=len(mt.test_questions) or mt.total_questions,
            passing_percentage=mt.passing_percentage,
            status=mt.status,
            instructions=mt.instructions,
            prerequisites=mt.prerequisites,
            tags=tags_list,
            is_ready=is_ready,
            shortfall=shortfall,
            topics_covered=sorted(topic_counts.keys()),
            topics_breakdown=topics_breakdown,
            what_you_will_practice=practice_points,
            blueprint_id=mt.blueprint_id,
            questions=questions_payload,
            latest_attempt_score=latest_att.score if latest_att else None,
            latest_attempt_status=latest_att.status.value if latest_att else None,
            active_attempt_id=active_attempt_id,
            attempt_count=attempt_count,
        )


mock_test_service = MockTestService()
