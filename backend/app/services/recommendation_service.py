"""
Recommendation Service for NexoraNet.

Generates transparent, explainable recommendations across Lessons, Labs, Mock Tests,
Topic Practice, and Adaptive Test Sessions based on deterministic student performance,
prerequisite dependencies, and curriculum hierarchy.
"""

import uuid
from typing import Any

from sqlalchemy.orm import Session

from app.core.adaptive_config import adaptive_config
from app.models.curriculum import Lesson, Topic
from app.models.enums import (
    DifficultyLevel,
    LabStatus,
    MockTestStatus,
    MockTestType,
    RecommendationPriority,
    RecommendationType,
)
from app.models.lab import Lab
from app.models.mock_test import MockTest
from app.schemas.adaptive import RecommendationItem, TopicPerformanceItem


class RecommendationService:
    """Rule-based curriculum recommendation engine with prerequisite awareness."""

    @staticmethod
    def generate_recommendations(
        user_id: int,
        performance_data: dict[str, Any],
        db: Session,
    ) -> list[RecommendationItem]:
        """
        Generate personalized, explainable recommendations.
        Never fabricates claims; supplies precise rationale for every recommended item.
        """
        has_sufficient_data = performance_data.get("has_sufficient_data", False)
        rec_diff: DifficultyLevel = performance_data.get(
            "recommended_difficulty", DifficultyLevel.BEGINNER
        )
        recommendations: list[RecommendationItem] = []

        # Case A: Insufficient Data / New Student Onboarding
        if not has_sufficient_data:
            return RecommendationService._generate_onboarding_recommendations(db)

        # Case B: Diagnostic Profile Active
        topics_needing_practice: list[TopicPerformanceItem] = performance_data.get(
            "top_topics_needing_practice", []
        )
        developing_topics: list[TopicPerformanceItem] = performance_data.get(
            "developing_topics", []
        )
        strong_topics: list[TopicPerformanceItem] = performance_data.get(
            "strongest_topics", []
        )
        decayed_topics: list[TopicPerformanceItem] = performance_data.get(
            "decayed_topics", []
        )

        # 1. Prerequisite-aware reordering
        # If a fundamental prerequisite topic needs practice, prioritize it before advanced topics
        ordered_weak_topics = RecommendationService._order_by_prerequisites(
            topics_needing_practice, db
        )

        # 2. Add Top Weak Topic Recommendations (Topic Practice + Lab + Lesson)
        for topic_item in ordered_weak_topics[:3]:
            # Adaptive Practice for this weak topic
            recommendations.append(
                RecommendationItem(
                    id=f"rec-prac-{topic_item.topic_id}-{uuid.uuid4().hex[:6]}",
                    type=RecommendationType.TOPIC_PRACTICE,
                    title=f"Practice {topic_item.topic_title}",
                    reason=(
                        f"Your recent {topic_item.topic_title} accuracy is "
                        f"{topic_item.recent_accuracy:.0f}% across {topic_item.questions_answered} questions."
                    ),
                    priority=RecommendationPriority.HIGH,
                    topic_id=topic_item.topic_id,
                    topic_slug=topic_item.topic_slug,
                    recommended_difficulty=rec_diff,
                    action_label="Start Topic Practice",
                    action_url=f"/adaptive-test?focus={topic_item.topic_id}",
                )
            )

            # Check if there is an associated hands-on lab
            matching_lab = (
                db.query(Lab)
                .filter(
                    Lab.topic_id == topic_item.topic_id,
                    Lab.status == LabStatus.PUBLISHED,
                )
                .first()
            )
            if matching_lab:
                recommendations.append(
                    RecommendationItem(
                        id=f"rec-lab-{matching_lab.id}-{uuid.uuid4().hex[:6]}",
                        type=RecommendationType.LAB,
                        title=f"Hands-On Lab: {matching_lab.title}",
                        reason=(
                            f"Strengthen your understanding of {topic_item.topic_title} "
                            f"through hands-on CLI terminal verification."
                        ),
                        priority=RecommendationPriority.HIGH,
                        topic_id=topic_item.topic_id,
                        topic_slug=topic_item.topic_slug,
                        recommended_difficulty=matching_lab.difficulty,
                        action_label="Launch Lab",
                        action_url=f"/labs/{matching_lab.slug}",
                    )
                )

            # Check if there is an introductory or core lesson
            matching_lesson = (
                db.query(Lesson)
                .filter(
                    Lesson.topic_id == topic_item.topic_id,
                    Lesson.is_published.is_(True),
                )
                .order_by(Lesson.order_index)
                .first()
            )
            if matching_lesson:
                recommendations.append(
                    RecommendationItem(
                        id=f"rec-les-{matching_lesson.id}-{uuid.uuid4().hex[:6]}",
                        type=RecommendationType.LESSON,
                        title=f"Review Lesson: {matching_lesson.title}",
                        reason=(
                            f"Review core theory and mechanics for {topic_item.topic_title} "
                            f"to reinforce key concepts."
                        ),
                        priority=RecommendationPriority.MEDIUM,
                        topic_id=topic_item.topic_id,
                        topic_slug=topic_item.topic_slug,
                        recommended_difficulty=matching_lesson.difficulty,
                        action_label="Read Lesson",
                        action_url=f"/learning/lessons/{matching_lesson.slug}",
                    )
                )

        # 3. Add Developing Topic Solidification
        for dev_item in developing_topics[:2]:
            recommendations.append(
                RecommendationItem(
                    id=f"rec-dev-{dev_item.topic_id}-{uuid.uuid4().hex[:6]}",
                    type=RecommendationType.TOPIC_PRACTICE,
                    title=f"Solidify {dev_item.topic_title}",
                    reason=(
                        f"Your recent {dev_item.topic_title} accuracy is developing at "
                        f"{dev_item.recent_accuracy:.0f}%; targeted practice will help lock in mastery."
                    ),
                    priority=RecommendationPriority.MEDIUM,
                    topic_id=dev_item.topic_id,
                    topic_slug=dev_item.topic_slug,
                    recommended_difficulty=rec_diff,
                    action_label="Solidify Topic",
                    action_url=f"/adaptive-test?focus={dev_item.topic_id}",
                )
            )

        # 4. Add Strong Topic Advancement if few or no weak topics exist
        if not ordered_weak_topics and strong_topics:
            best_strong = strong_topics[0]
            recommendations.append(
                RecommendationItem(
                    id=f"rec-strong-{best_strong.topic_id}-{uuid.uuid4().hex[:6]}",
                    type=RecommendationType.DIFFICULTY_REINFORCEMENT,
                    title=f"Advanced Drills: {best_strong.topic_title}",
                    reason=(
                        f"High proficiency demonstrated in {best_strong.topic_title} "
                        f"({best_strong.recent_accuracy:.0f}%). Ready for advanced difficulty drills."
                    ),
                    priority=RecommendationPriority.LOW,
                    topic_id=best_strong.topic_id,
                    topic_slug=best_strong.topic_slug,
                    recommended_difficulty=DifficultyLevel.ADVANCED,
                    action_label="Advanced Drills",
                    action_url=f"/adaptive-test?focus={best_strong.topic_id}",
                )
            )

        # 5. Add Decayed Topic Refreshers
        for decay_item in decayed_topics[:2]:
            recommendations.append(
                RecommendationItem(
                    id=f"rec-decay-{decay_item.topic_id}-{uuid.uuid4().hex[:6]}",
                    type=RecommendationType.REVIEW,
                    title=f"Quick Refresher: {decay_item.topic_title}",
                    reason=(
                        f"You demonstrated strong proficiency earlier, but have not practiced "
                        f"{decay_item.topic_title} in over {adaptive_config.ADAPTIVE_DECAY_DAYS} days."
                    ),
                    priority=RecommendationPriority.MEDIUM,
                    topic_id=decay_item.topic_id,
                    topic_slug=decay_item.topic_slug,
                    recommended_difficulty=rec_diff,
                    action_label="Review Topic",
                    action_url=f"/adaptive-test?focus={decay_item.topic_id}",
                )
            )

        # 4. Add Matching Catalog Mock Test at recommended difficulty
        matching_mock = (
            db.query(MockTest)
            .filter(
                MockTest.difficulty == rec_diff,
                MockTest.status == MockTestStatus.PUBLISHED,
                MockTest.test_type != MockTestType.PRACTICE,
            )
            .order_by(MockTest.id)
            .first()
        )
        if matching_mock:
            recommendations.append(
                RecommendationItem(
                    id=f"rec-mock-{matching_mock.id}-{uuid.uuid4().hex[:6]}",
                    type=RecommendationType.MOCK_TEST,
                    title=f"Assessment: {matching_mock.title}",
                    reason=(
                        f"Challenge your skills under formal timed exam conditions "
                        f"matched to your recommended {rec_diff.value} level."
                    ),
                    priority=RecommendationPriority.MEDIUM,
                    topic_id=None,
                    topic_slug=None,
                    recommended_difficulty=rec_diff,
                    action_label="Take Mock Test",
                    action_url=f"/mock-tests/{matching_mock.slug}",
                )
            )

        # 5. Add Global Personalized Adaptive Practice Session
        recommendations.append(
            RecommendationItem(
                id=f"rec-adapt-main-{uuid.uuid4().hex[:6]}",
                type=RecommendationType.ADAPTIVE_TEST,
                title="Personalized Adaptive Practice Session",
                reason=(
                    f"A balanced 20-question practice set dynamically composed to address "
                    f"topics needing improvement while reinforcing your solid domains at the {rec_diff.value} tier."
                ),
                priority=RecommendationPriority.HIGH,
                recommended_difficulty=rec_diff,
                action_label="Start Adaptive Practice",
                action_url="/adaptive-test",
            )
        )

        return recommendations

    @staticmethod
    def get_highest_priority_recommendation(
        recommendations: list[RecommendationItem],
    ) -> RecommendationItem | None:
        """Pick the single most urgent recommendation for the hero banner."""
        if not recommendations:
            return None

        # Prioritize HIGH urgency items in specific order: TOPIC_PRACTICE / LAB / LESSON / ADAPTIVE_TEST
        high_recs = [r for r in recommendations if r.priority == RecommendationPriority.HIGH]
        if high_recs:
            for pref_type in [
                RecommendationType.TOPIC_PRACTICE,
                RecommendationType.LAB,
                RecommendationType.LESSON,
                RecommendationType.ADAPTIVE_TEST,
            ]:
                for r in high_recs:
                    if r.type == pref_type:
                        return r
            return high_recs[0]

        return recommendations[0]

    @staticmethod
    def _order_by_prerequisites(
        weak_topics: list[TopicPerformanceItem],
        db: Session,
    ) -> list[TopicPerformanceItem]:
        """
        Sort weak topics so foundational prerequisite topics are recommended first.
        Leverages Topic.order_index as curriculum sequence.
        """
        if not weak_topics:
            return []

        topic_ids = [t.topic_id for t in weak_topics]
        db_topics = db.query(Topic).filter(Topic.id.in_(topic_ids)).all()
        order_map = {t.id: t.order_index for t in db_topics}

        # Sort by curriculum order_index ascending (fundamentals before advanced)
        return sorted(weak_topics, key=lambda item: order_map.get(item.topic_id, 999))

    @staticmethod
    def _generate_onboarding_recommendations(db: Session) -> list[RecommendationItem]:
        """Warm, foundational starting track recommendations for new students."""
        items: list[RecommendationItem] = []

        # Find first module's topics
        first_topics = (
            db.query(Topic)
            .filter(Topic.is_published.is_(True))
            .order_by(Topic.order_index)
            .limit(3)
            .all()
        )

        for idx, t in enumerate(first_topics):
            priority = (
                RecommendationPriority.HIGH if idx == 0 else RecommendationPriority.MEDIUM
            )
            items.append(
                RecommendationItem(
                    id=f"rec-onboard-topic-{t.id}",
                    type=RecommendationType.LESSON,
                    title=f"Start Here: {t.title}",
                    reason=(
                        f"Foundational curriculum topic to establish your networking fundamentals. "
                        f"Estimated: {t.estimated_minutes} minutes."
                    ),
                    priority=priority,
                    topic_id=t.id,
                    topic_slug=t.slug,
                    recommended_difficulty=DifficultyLevel.BEGINNER,
                    action_label="Start Learning",
                    action_url=f"/learning/topics/{t.slug}",
                )
            )

        # Introductory Lab
        intro_lab = (
            db.query(Lab)
            .filter(
                Lab.status == LabStatus.PUBLISHED,
                Lab.difficulty == DifficultyLevel.BEGINNER,
            )
            .order_by(Lab.id)
            .first()
        )
        if intro_lab:
            items.append(
                RecommendationItem(
                    id=f"rec-onboard-lab-{intro_lab.id}",
                    type=RecommendationType.LAB,
                    title=f"Hands-On Lab: {intro_lab.title}",
                    reason="Inspect local interfaces and verify network addressing in an interactive sandbox.",
                    priority=RecommendationPriority.MEDIUM,
                    topic_id=intro_lab.topic_id,
                    recommended_difficulty=DifficultyLevel.BEGINNER,
                    action_label="Launch Lab",
                    action_url=f"/labs/{intro_lab.slug}",
                )
            )

        # Introductory Mock Test
        intro_test = (
            db.query(MockTest)
            .filter(
                MockTest.difficulty == DifficultyLevel.BEGINNER,
                MockTest.status == MockTestStatus.PUBLISHED,
                MockTest.test_type != MockTestType.PRACTICE,
            )
            .order_by(MockTest.id)
            .first()
        )
        if intro_test:
            items.append(
                RecommendationItem(
                    id=f"rec-onboard-test-{intro_test.id}",
                    type=RecommendationType.MOCK_TEST,
                    title=f"Diagnostic Quiz: {intro_test.title}",
                    reason="Quick assessment to establish your starting performance baseline.",
                    priority=RecommendationPriority.LOW,
                    recommended_difficulty=DifficultyLevel.BEGINNER,
                    action_label="Take Quiz",
                    action_url=f"/mock-tests/{intro_test.slug}",
                )
            )

        # Generic Adaptive Practice
        items.append(
            RecommendationItem(
                id="rec-onboard-adaptive-starter",
                type=RecommendationType.ADAPTIVE_TEST,
                title="Adaptive Practice Session",
                reason="Beginner-focused practice session that calibrates question difficulty as you progress.",
                priority=RecommendationPriority.MEDIUM,
                recommended_difficulty=DifficultyLevel.BEGINNER,
                action_label="Start Adaptive Practice",
                action_url="/adaptive-test",
            )
        )

        return items


recommendation_service = RecommendationService()
