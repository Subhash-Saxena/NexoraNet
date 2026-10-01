"""
Adaptive Performance Service for NexoraNet.

Analyzes student examination history, question-level responses, lab progress,
and lesson engagement to compute explainable topic-level and difficulty-level
performance diagnostics using deterministic recency-weighted metrics.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session, selectinload

from app.core.adaptive_config import adaptive_config
from app.models.curriculum import Topic
from app.models.enums import (
    AttemptStatus,
    ConfidenceLevel,
    DifficultyLevel,
    TopicPerformanceStatus,
)
from app.models.mock_test import MockTestAttempt, StudentAnswer
from app.models.question import Question
from app.schemas.adaptive import (
    DifficultyPerformanceSummary,
    DifficultyStats,
    TopicPerformanceItem,
)


@dataclass
class TopicStatsAccumulator:
    """Internal aggregator for topic-level responses within the analysis window."""

    topic_id: int
    topic_title: str
    topic_slug: str
    questions_seen: int = 0
    questions_answered: int = 0
    correct_answers: int = 0
    incorrect_answers: int = 0
    unanswered: int = 0
    weighted_correct: float = 0.0
    weighted_answered: float = 0.0
    last_attempt_at: datetime | None = None
    diff_seen: dict[DifficultyLevel, int] = field(
        default_factory=lambda: {
            DifficultyLevel.BEGINNER: 0,
            DifficultyLevel.INTERMEDIATE: 0,
            DifficultyLevel.ADVANCED: 0,
        }
    )
    diff_correct: dict[DifficultyLevel, int] = field(
        default_factory=lambda: {
            DifficultyLevel.BEGINNER: 0,
            DifficultyLevel.INTERMEDIATE: 0,
            DifficultyLevel.ADVANCED: 0,
        }
    )


class AdaptivePerformanceService:
    """Deterministic, rule-based student performance diagnostic engine."""

    @staticmethod
    def calculate_user_performance(
        user_id: int,
        db: Session,
    ) -> dict[str, Any]:
        """
        Analyze recent student examination and question performance.
        Returns topic breakdown, difficulty performance, and data sufficiency state.
        """
        # 1. Fetch recent completed / submitted / expired test attempts
        recent_attempts = (
            db.query(MockTestAttempt)
            .options(
                selectinload(MockTestAttempt.mock_test),
                selectinload(MockTestAttempt.student_answers)
                .selectinload(StudentAnswer.question)
                .selectinload(Question.topic),
            )
            .filter(
                MockTestAttempt.user_id == user_id,
                MockTestAttempt.status.in_(
                    [
                        AttemptStatus.SUBMITTED,
                        AttemptStatus.COMPLETED,
                        AttemptStatus.EXPIRED,
                    ]
                ),
                MockTestAttempt.student_answers.any(),
            )
            .order_by(MockTestAttempt.submitted_at.desc())
            .limit(adaptive_config.ADAPTIVE_RECENT_ATTEMPTS)
            .all()
        )

        # 2. Collect all topics from database to ensure complete coverage representation
        all_topics = db.query(Topic).filter(Topic.is_published.is_(True)).order_by(Topic.order_index).all()
        topic_map: dict[int, TopicStatsAccumulator] = {
            t.id: TopicStatsAccumulator(
                topic_id=t.id,
                topic_title=t.title,
                topic_slug=t.slug,
            )
            for t in all_topics
        }

        # 3. Overall and Difficulty tracking
        overall_total_answered = 0
        overall_total_correct = 0
        difficulty_seen: dict[DifficultyLevel, int] = {
            DifficultyLevel.BEGINNER: 0,
            DifficultyLevel.INTERMEDIATE: 0,
            DifficultyLevel.ADVANCED: 0,
        }
        difficulty_correct: dict[DifficultyLevel, int] = {
            DifficultyLevel.BEGINNER: 0,
            DifficultyLevel.INTERMEDIATE: 0,
            DifficultyLevel.ADVANCED: 0,
        }

        # 4. Iterate chronologically over attempts (index 0 is most recent)
        total_questions_processed = 0

        for attempt_idx, attempt in enumerate(recent_attempts):
            weight = adaptive_config.get_recency_weight(attempt_idx)
            attempt_time = attempt.submitted_at or attempt.started_at

            for ans in attempt.student_answers:
                if total_questions_processed >= adaptive_config.ADAPTIVE_RECENT_QUESTION_LIMIT:
                    break

                q = ans.question
                if not q:
                    continue

                total_questions_processed += 1
                q_diff = q.difficulty if q.difficulty in difficulty_seen else DifficultyLevel.BEGINNER

                # Normalize topic accumulator
                if q.topic_id not in topic_map:
                    topic_map[q.topic_id] = TopicStatsAccumulator(
                        topic_id=q.topic_id,
                        topic_title=q.topic.title if q.topic else f"Topic #{q.topic_id}",
                        topic_slug=q.topic.slug if q.topic else f"topic-{q.topic_id}",
                    )

                accum = topic_map[q.topic_id]
                accum.questions_seen += 1

                # Update timestamp
                if attempt_time and (not accum.last_attempt_at or attempt_time > accum.last_attempt_at):
                    accum.last_attempt_at = attempt_time

                # Check if answered
                has_selection = bool(ans.answer_data and ans.answer_data != "[]")
                if has_selection:
                    accum.questions_answered += 1
                    accum.weighted_answered += weight
                    overall_total_answered += 1
                    difficulty_seen[q_diff] += 1
                    accum.diff_seen[q_diff] += 1

                    if ans.is_correct:
                        accum.correct_answers += 1
                        accum.weighted_correct += weight
                        overall_total_correct += 1
                        difficulty_correct[q_diff] += 1
                        accum.diff_correct[q_diff] += 1
                    else:
                        accum.incorrect_answers += 1
                else:
                    accum.unanswered += 1

        # 5. Build TopicPerformanceItems
        now_dt = datetime.now(timezone.utc)
        topic_items: list[TopicPerformanceItem] = []
        decayed_topics: list[TopicPerformanceItem] = []

        for accum in topic_map.values():
            # Accuracy calculations
            if accum.questions_answered > 0:
                accuracy = (accum.correct_answers / accum.questions_answered) * 100.0
            else:
                accuracy = 0.0

            if accum.weighted_answered > 0:
                recent_accuracy = (accum.weighted_correct / accum.weighted_answered) * 100.0
            else:
                recent_accuracy = accuracy

            # Confidence Level determination
            if accum.questions_answered < adaptive_config.ADAPTIVE_MIN_QUESTIONS:
                confidence = ConfidenceLevel.INSUFFICIENT
                status = TopicPerformanceStatus.INSUFFICIENT_DATA
            elif accum.questions_answered <= adaptive_config.ADAPTIVE_PRELIMINARY_LIMIT:
                confidence = ConfidenceLevel.PRELIMINARY
            elif accum.questions_answered <= adaptive_config.ADAPTIVE_DEVELOPING_LIMIT:
                confidence = ConfidenceLevel.DEVELOPING
            else:
                confidence = ConfidenceLevel.STRONG

            # Topic Status assignment
            if accum.questions_answered >= adaptive_config.ADAPTIVE_MIN_QUESTIONS:
                if recent_accuracy < adaptive_config.ADAPTIVE_NEEDS_PRACTICE_THRESHOLD:
                    status = TopicPerformanceStatus.NEEDS_PRACTICE
                elif recent_accuracy < adaptive_config.ADAPTIVE_DEVELOPING_THRESHOLD:
                    status = TopicPerformanceStatus.DEVELOPING
                elif recent_accuracy < adaptive_config.ADAPTIVE_SOLID_THRESHOLD:
                    status = TopicPerformanceStatus.SOLID
                else:
                    status = TopicPerformanceStatus.STRONG

            # Explainable recommended action
            if status == TopicPerformanceStatus.INSUFFICIENT_DATA:
                remaining = max(0, adaptive_config.ADAPTIVE_MIN_QUESTIONS - accum.questions_answered)
                if accum.questions_answered == 0:
                    action_msg = "No recent attempts recorded. Foundational study or introductory quiz recommended."
                else:
                    action_msg = f"Complete {remaining} more question(s) to establish an explainable diagnostic baseline."
            elif status == TopicPerformanceStatus.NEEDS_PRACTICE:
                action_msg = f"Targeted practice recommended to reinforce core concepts (Recent accuracy: {recent_accuracy:.0f}%)."
            elif status == TopicPerformanceStatus.DEVELOPING:
                action_msg = f"Continue intermediate practice to solidify conceptual understanding (Recent accuracy: {recent_accuracy:.0f}%)."
            elif status == TopicPerformanceStatus.SOLID:
                action_msg = f"Solid proficiency demonstrated ({recent_accuracy:.0f}%). Ready for challenging scenarios and mixed assessments."
            else:  # STRONG
                action_msg = f"Strong mastery demonstrated ({recent_accuracy:.0f}%). Maintain proficiency with advanced drills."

            # Decay check: If topic was SOLID or STRONG, but last practiced > ADAPTIVE_DECAY_DAYS ago
            is_decayed = False
            if status in (TopicPerformanceStatus.SOLID, TopicPerformanceStatus.STRONG) and accum.last_attempt_at:
                # Ensure timezone aware
                last_dt = accum.last_attempt_at
                if last_dt.tzinfo is None:
                    last_dt = last_dt.replace(tzinfo=timezone.utc)
                days_since = (now_dt - last_dt).total_seconds() / 86400.0
                if days_since > adaptive_config.ADAPTIVE_DECAY_DAYS:
                    is_decayed = True
                    action_msg = f"Previously solid, but not practiced in {int(days_since)} days. Quick refresher review recommended."

            # Difficulty breakdown for this topic
            diff_dist: dict[str, DifficultyStats] = {}
            for d in [DifficultyLevel.BEGINNER, DifficultyLevel.INTERMEDIATE, DifficultyLevel.ADVANCED]:
                seen_count = accum.diff_seen[d]
                corr_count = accum.diff_correct[d]
                d_acc = (corr_count / seen_count * 100.0) if seen_count > 0 else 0.0
                diff_dist[d.value] = DifficultyStats(
                    seen=seen_count,
                    correct=corr_count,
                    accuracy=round(d_acc, 1),
                )

            item = TopicPerformanceItem(
                topic_id=accum.topic_id,
                topic_title=accum.topic_title,
                topic_slug=accum.topic_slug,
                status=status,
                questions_seen=accum.questions_seen,
                questions_answered=accum.questions_answered,
                correct_answers=accum.correct_answers,
                incorrect_answers=accum.incorrect_answers,
                unanswered=accum.unanswered,
                accuracy=round(accuracy, 1),
                recent_accuracy=round(recent_accuracy, 1),
                confidence_level=confidence,
                recommended_action=action_msg,
                last_attempt_at=accum.last_attempt_at,
                difficulty_distribution=diff_dist,
            )
            topic_items.append(item)
            if is_decayed:
                decayed_topics.append(item)

        # 6. Difficulty Performance Summary across entire window
        diff_summary = DifficultyPerformanceSummary(
            BEGINNER=DifficultyStats(
                seen=difficulty_seen[DifficultyLevel.BEGINNER],
                correct=difficulty_correct[DifficultyLevel.BEGINNER],
                accuracy=round(
                    (difficulty_correct[DifficultyLevel.BEGINNER] / max(1, difficulty_seen[DifficultyLevel.BEGINNER]))
                    * 100.0,
                    1,
                )
                if difficulty_seen[DifficultyLevel.BEGINNER] > 0
                else 0.0,
            ),
            INTERMEDIATE=DifficultyStats(
                seen=difficulty_seen[DifficultyLevel.INTERMEDIATE],
                correct=difficulty_correct[DifficultyLevel.INTERMEDIATE],
                accuracy=round(
                    (
                        difficulty_correct[DifficultyLevel.INTERMEDIATE]
                        / max(1, difficulty_seen[DifficultyLevel.INTERMEDIATE])
                    )
                    * 100.0,
                    1,
                )
                if difficulty_seen[DifficultyLevel.INTERMEDIATE] > 0
                else 0.0,
            ),
            ADVANCED=DifficultyStats(
                seen=difficulty_seen[DifficultyLevel.ADVANCED],
                correct=difficulty_correct[DifficultyLevel.ADVANCED],
                accuracy=round(
                    (difficulty_correct[DifficultyLevel.ADVANCED] / max(1, difficulty_seen[DifficultyLevel.ADVANCED]))
                    * 100.0,
                    1,
                )
                if difficulty_seen[DifficultyLevel.ADVANCED] > 0
                else 0.0,
            ),
        )

        # 7. Recommended Difficulty Algorithm
        recommended_difficulty, difficulty_reason = AdaptivePerformanceService._recommend_difficulty(
            diff_summary=diff_summary,
            total_answered=overall_total_answered,
        )

        # 8. Sort and bucket topics
        active_topics = [t for t in topic_items if t.questions_answered > 0]
        topics_needing_practice = [
            t for t in topic_items if t.status == TopicPerformanceStatus.NEEDS_PRACTICE
        ]
        # Sort needing practice by lowest recent accuracy
        topics_needing_practice.sort(key=lambda t: t.recent_accuracy)

        developing_topics = [
            t for t in topic_items if t.status == TopicPerformanceStatus.DEVELOPING
        ]
        developing_topics.sort(key=lambda t: t.recent_accuracy)

        strong_topics = [
            t
            for t in topic_items
            if t.status in (TopicPerformanceStatus.SOLID, TopicPerformanceStatus.STRONG)
        ]
        strong_topics.sort(key=lambda t: t.recent_accuracy, reverse=True)

        overall_acc = (
            (overall_total_correct / overall_total_answered * 100.0)
            if overall_total_answered > 0
            else 0.0
        )

        # Sufficiency state
        attempts_count = len(recent_attempts)
        has_sufficient_data = (
            overall_total_answered >= adaptive_config.ADAPTIVE_MIN_QUESTIONS
            and attempts_count >= 1
        )

        if not has_sufficient_data:
            if attempts_count == 0:
                data_msg = (
                    "No completed mock tests yet. Complete 1–2 tests or introductory lessons "
                    "to unlock personalized adaptive recommendations."
                )
            else:
                data_msg = (
                    f"You have completed {attempts_count} test with {overall_total_answered} answered questions. "
                    f"Complete at least {adaptive_config.ADAPTIVE_MIN_QUESTIONS} questions to establish an explainable diagnostic profile."
                )
        else:
            data_msg = (
                f"Diagnostic profile active based on {overall_total_answered} recent questions "
                f"across {attempts_count} assessment attempt(s)."
            )

        return {
            "user_id": user_id,
            "has_sufficient_data": has_sufficient_data,
            "data_message": data_msg,
            "overall_accuracy": round(overall_acc, 1),
            "total_questions_analyzed": overall_total_answered,
            "total_attempts_analyzed": attempts_count,
            "recommended_difficulty": recommended_difficulty,
            "difficulty_reason": difficulty_reason,
            "difficulty_performance": diff_summary,
            "top_topics_needing_practice": topics_needing_practice[:5],
            "developing_topics": developing_topics[:5],
            "strongest_topics": strong_topics[:5],
            "decayed_topics": decayed_topics,
            "all_topics": topic_items,
            "active_topics": active_topics,
            "recent_attempt_ids": [a.id for a in recent_attempts],
        }

    @staticmethod
    def _recommend_difficulty(
        diff_summary: DifficultyPerformanceSummary,
        total_answered: int,
    ) -> tuple[DifficultyLevel, str]:
        """
        Deterministic, rule-based difficulty progression evaluator.
        Never makes permanent ability claims; uses neutral recent accuracy thresholds.
        """
        if total_answered < adaptive_config.ADAPTIVE_MIN_QUESTIONS:
            return (
                DifficultyLevel.BEGINNER,
                "Foundational track recommended for onboarding students to establish core networking proficiency.",
            )

        b = diff_summary.BEGINNER
        i = diff_summary.INTERMEDIATE
        a = diff_summary.ADVANCED

        # Evaluate Intermediate tier if substantial data exists
        if i.seen >= adaptive_config.ADAPTIVE_MIN_QUESTIONS:
            if i.accuracy < adaptive_config.ADAPTIVE_INTERMEDIATE_LOWER_THRESHOLD:
                return (
                    DifficultyLevel.BEGINNER,
                    f"Your recent Intermediate accuracy is {i.accuracy:.0f}%; foundational Beginner reinforcement and guided practice are recommended.",
                )
            elif i.accuracy < adaptive_config.ADAPTIVE_INTERMEDIATE_UPPER_THRESHOLD:
                return (
                    DifficultyLevel.INTERMEDIATE,
                    f"Your Intermediate accuracy is steady at {i.accuracy:.0f}%; continued Intermediate practice is recommended to master complex subnetting and routing.",
                )
            else:
                # i.accuracy >= 80%
                if a.seen >= adaptive_config.ADAPTIVE_MIN_QUESTIONS and a.accuracy >= adaptive_config.ADAPTIVE_ADVANCED_THRESHOLD:
                    return (
                        DifficultyLevel.ADVANCED,
                        f"Strong Intermediate proficiency ({i.accuracy:.0f}%) and solid Advanced accuracy ({a.accuracy:.0f}%); Advanced security and packet analysis drills recommended.",
                    )
                return (
                    DifficultyLevel.INTERMEDIATE,
                    f"High Intermediate proficiency ({i.accuracy:.0f}%); ready for Intermediate mastery assessments and selective Advanced exposure.",
                )

        # Evaluate Beginner tier
        if b.seen >= adaptive_config.ADAPTIVE_MIN_QUESTIONS:
            if b.accuracy < adaptive_config.ADAPTIVE_BEGINNER_LOWER_THRESHOLD:
                return (
                    DifficultyLevel.BEGINNER,
                    f"Recent Beginner accuracy is {b.accuracy:.0f}%; continued practice on OSI, IPv4, and device fundamentals recommended.",
                )
            elif b.accuracy < adaptive_config.ADAPTIVE_BEGINNER_UPPER_THRESHOLD:
                return (
                    DifficultyLevel.BEGINNER,
                    f"Beginner accuracy is progressing well at {b.accuracy:.0f}%; practice mixed Beginner and introductory Intermediate questions.",
                )
            else:
                return (
                    DifficultyLevel.INTERMEDIATE,
                    f"Strong Beginner fundamentals ({b.accuracy:.0f}%); ready to progress to Intermediate networking, subnetting, and protocols.",
                )

        # Default fallback
        return (
            DifficultyLevel.BEGINNER,
            "Initial foundational practice recommended across core networking concepts.",
        )


adaptive_performance_service = AdaptivePerformanceService()
