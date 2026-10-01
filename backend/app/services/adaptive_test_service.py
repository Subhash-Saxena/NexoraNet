"""
Adaptive Test Generation Service for NexoraNet.

Dynamically compiles personalized, balanced practice sessions based on recent
diagnostic accuracy, gradual difficulty adaptation, question novelty, and
question-type variety while reusing the authoritative Mock Test Engine.
"""

import random
import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session, selectinload

from app.core.adaptive_config import adaptive_config
from app.models.enums import (
    DifficultyLevel,
    MockTestStatus,
    MockTestType,
    QuestionStatus,
)
from app.models.mock_test import (
    MockTest,
    MockTestAttempt,
    MockTestQuestion,
    StudentAnswer,
)
from app.models.question import Question
from app.schemas.adaptive import StartAdaptiveTestRequest
from app.schemas.mock_test import StartAttemptResponse
from app.services.adaptive_performance_service import adaptive_performance_service
from app.services.test_attempt_service import test_attempt_service


class AdaptiveTestService:
    """Service dynamically compiling and starting personalized adaptive exams."""

    @staticmethod
    def generate_and_start_adaptive_test(
        user_id: int,
        request: StartAdaptiveTestRequest,
        db: Session,
    ) -> StartAttemptResponse:
        """
        Dynamically select candidate questions, assemble a formal MockTest record,
        and launch an authoritative sitting.
        """
        # 1. Inspect recent student diagnostic profile
        perf = adaptive_performance_service.calculate_user_performance(
            user_id=user_id,
            db=db,
        )
        rec_diff: DifficultyLevel = perf["recommended_difficulty"]
        target_count = request.question_count

        # 2. Gather recent question IDs to avoid repeated presentation
        seen_question_ids = AdaptiveTestService._get_recently_seen_question_ids(
            user_id=user_id,
            db=db,
            attempts_window=adaptive_config.ADAPTIVE_NO_REPEAT_ATTEMPTS_COUNT,
        )

        # 3. Topic quota planning
        selected_questions: list[Question] = []

        if request.focus_topic_ids and len(request.focus_topic_ids) > 0:
            # User explicitly requested specific focus topic(s)
            selected_questions = AdaptiveTestService._select_focus_topic_questions(
                topic_ids=request.focus_topic_ids,
                target_count=target_count,
                recommended_difficulty=rec_diff,
                seen_question_ids=seen_question_ids,
                db=db,
            )
        else:
            # Automatic personalized distribution: ~50% weak, ~30% developing, ~20% strong/reinforcement
            selected_questions = AdaptiveTestService._select_personalized_questions(
                perf=perf,
                target_count=target_count,
                recommended_difficulty=rec_diff,
                seen_question_ids=seen_question_ids,
                db=db,
            )

        if not selected_questions:
            # Fallback to any published questions
            selected_questions = (
                db.query(Question)
                .filter(Question.status == QuestionStatus.PUBLISHED)
                .order_by(Question.id)
                .limit(target_count)
                .all()
            )

        if not selected_questions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unable to generate adaptive test: No published questions are available in the question bank.",
            )

        # 4. Create dedicated MockTest session entity
        now = datetime.now(timezone.utc)
        test_slug = f"adaptive-{user_id}-{int(now.timestamp())}-{uuid.uuid4().hex[:6]}"
        test_title = f"Adaptive Practice ({rec_diff.value.title()} - {now.strftime('%b %d')})"

        mock_test = MockTest(
            title=test_title,
            slug=test_slug,
            description=(
                f"Personalized practice session calibrated dynamically to your diagnostic performance profile "
                f"({len(selected_questions)} questions, target difficulty: {rec_diff.value})."
            ),
            test_type=MockTestType.ADAPTIVE,
            difficulty=rec_diff,
            duration_minutes=request.duration_minutes,
            total_questions=len(selected_questions),
            passing_percentage=70.0,
            status=MockTestStatus.PUBLISHED,
            instructions=(
                "This adaptive session is dynamically generated for your current competencies. "
                "Questions are drawn from topics needing reinforcement while maintaining broad protocol coverage."
            ),
        )
        db.add(mock_test)
        db.flush()

        # 5. Link questions via MockTestQuestion preserving order
        for idx, q in enumerate(selected_questions):
            link = MockTestQuestion(
                mock_test_id=mock_test.id,
                question_id=q.id,
                order_index=idx,
                points=q.points,
            )
            db.add(link)

        db.commit()

        # 6. Delegate sitting creation to authoritative TestAttemptService
        return test_attempt_service.start_or_resume_attempt(
            user_id=user_id,
            test_id_or_slug=mock_test.id,
            retake=True,
            db=db,
        )

    @staticmethod
    def _select_personalized_questions(
        perf: dict[str, Any],
        target_count: int,
        recommended_difficulty: DifficultyLevel,
        seen_question_ids: set[int],
        db: Session,
    ) -> list[Question]:
        """Distribute target count across weak, developing, and solid topic tiers."""
        weak_topics = perf.get("top_topics_needing_practice", [])
        dev_topics = perf.get("developing_topics", [])
        solid_topics = perf.get("strongest_topics", [])

        # Quota targets
        weak_quota = int(target_count * adaptive_config.ADAPTIVE_TOPIC_TARGET_DISTRIBUTION["NEEDS_PRACTICE"])
        dev_quota = int(target_count * adaptive_config.ADAPTIVE_TOPIC_TARGET_DISTRIBUTION["DEVELOPING"])
        solid_quota = target_count - weak_quota - dev_quota

        selected: list[Question] = []
        selected_ids: set[int] = set()

        def pick_from_tier(topic_list: list[Any], quota: int) -> None:
            nonlocal selected, selected_ids
            if not topic_list or quota <= 0:
                return

            t_ids = [t.topic_id for t in topic_list]
            candidates = (
                db.query(Question)
                .options(selectinload(Question.options), selectinload(Question.topic))
                .filter(
                    Question.topic_id.in_(t_ids),
                    Question.status == QuestionStatus.PUBLISHED,
                    ~Question.id.in_(selected_ids),
                )
                .all()
            )

            # Score candidates
            scored = []
            for q in candidates:
                score = AdaptiveTestService._score_candidate(
                    q=q,
                    recommended_difficulty=recommended_difficulty,
                    seen_question_ids=seen_question_ids,
                )
                scored.append((score, q))

            # Sort by highest candidate score
            scored.sort(key=lambda pair: pair[0], reverse=True)

            for _, q in scored:
                if len(selected) >= target_count:
                    break
                selected.append(q)
                selected_ids.add(q.id)
                quota -= 1
                if quota <= 0:
                    break

        # Pick from each tier
        pick_from_tier(weak_topics, weak_quota)
        pick_from_tier(dev_topics, dev_quota)
        pick_from_tier(solid_topics, solid_quota)

        # If shortfall remains, backfill from any published questions matching recommended difficulty
        if len(selected) < target_count:
            remaining = target_count - len(selected)
            fillers = (
                db.query(Question)
                .options(selectinload(Question.options), selectinload(Question.topic))
                .filter(
                    Question.status == QuestionStatus.PUBLISHED,
                    ~Question.id.in_(selected_ids),
                )
                .order_by(
                    # Prefer matching recommended difficulty
                    (Question.difficulty == recommended_difficulty).desc(),
                    Question.id,
                )
                .limit(remaining)
                .all()
            )
            for q in fillers:
                selected.append(q)
                selected_ids.add(q.id)

        # Shuffle selected questions deterministically so weak questions aren't all clustered at the beginning
        # We can interleave them
        rng = random.Random(42)
        rng.shuffle(selected)
        return selected

    @staticmethod
    def _select_focus_topic_questions(
        topic_ids: list[int],
        target_count: int,
        recommended_difficulty: DifficultyLevel,
        seen_question_ids: set[int],
        db: Session,
    ) -> list[Question]:
        """Select questions when user focused on specific topic(s)."""
        candidates = (
            db.query(Question)
            .options(selectinload(Question.options), selectinload(Question.topic))
            .filter(
                Question.topic_id.in_(topic_ids),
                Question.status == QuestionStatus.PUBLISHED,
            )
            .all()
        )

        scored = []
        for q in candidates:
            score = AdaptiveTestService._score_candidate(
                q=q,
                recommended_difficulty=recommended_difficulty,
                seen_question_ids=seen_question_ids,
            )
            scored.append((score, q))

        scored.sort(key=lambda pair: pair[0], reverse=True)
        selected = [q for _, q in scored[:target_count]]

        # If not enough in focus topics, backfill
        if len(selected) < target_count:
            existing_ids = {q.id for q in selected}
            remaining = target_count - len(selected)
            fillers = (
                db.query(Question)
                .options(selectinload(Question.options), selectinload(Question.topic))
                .filter(
                    Question.status == QuestionStatus.PUBLISHED,
                    ~Question.id.in_(existing_ids),
                )
                .limit(remaining)
                .all()
            )
            selected.extend(fillers)

        rng = random.Random(42)
        rng.shuffle(selected)
        return selected

    @staticmethod
    def _score_candidate(
        q: Question,
        recommended_difficulty: DifficultyLevel,
        seen_question_ids: set[int],
    ) -> float:
        """
        Deterministic scoring function for selecting questions.
        Combines difficulty appropriateness, novelty, and type variety.
        """
        score = 0.0

        # 1. Difficulty weight
        if q.difficulty == recommended_difficulty:
            score += 30.0
        elif (
            (recommended_difficulty == DifficultyLevel.INTERMEDIATE and q.difficulty in (DifficultyLevel.BEGINNER, DifficultyLevel.ADVANCED))
            or (recommended_difficulty == DifficultyLevel.BEGINNER and q.difficulty == DifficultyLevel.INTERMEDIATE)
            or (recommended_difficulty == DifficultyLevel.ADVANCED and q.difficulty == DifficultyLevel.INTERMEDIATE)
        ):
            score += 15.0  # Adjacent difficulty
        else:
            score += 5.0  # Non-adjacent (e.g. Beginner vs Advanced)

        # 2. Novelty weight
        if q.id not in seen_question_ids:
            score += 25.0
        else:
            score += 0.0  # Already seen in recent attempts

        # 3. Question type variety bonus
        # Reward complex interactive types slightly to prevent single-choice monotony
        if q.question_type.value in ("NUMERICAL", "SUBNETTING", "SCENARIO", "PACKET_ANALYSIS"):
            score += 10.0
        else:
            score += 5.0

        return score

    @staticmethod
    def _get_recently_seen_question_ids(
        user_id: int,
        db: Session,
        attempts_window: int = 2,
    ) -> set[int]:
        """Fetch question IDs answered by student in recent attempts."""
        recent_attempts = (
            db.query(MockTestAttempt)
            .filter(MockTestAttempt.user_id == user_id)
            .order_by(MockTestAttempt.id.desc())
            .limit(attempts_window)
            .all()
        )
        if not recent_attempts:
            return set()

        attempt_ids = [a.id for a in recent_attempts]
        answers = (
            db.query(StudentAnswer.question_id)
            .filter(StudentAnswer.attempt_id.in_(attempt_ids))
            .all()
        )
        return {r[0] for r in answers}


adaptive_test_service = AdaptiveTestService()
