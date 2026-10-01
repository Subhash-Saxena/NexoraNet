import random
import re
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session, selectinload

from app.models.enums import (
    DifficultyLevel,
    MockTestStatus,
    MockTestType,
    QuestionStatus,
)
from app.models.mock_test import (
    MockTest,
    MockTestQuestion,
    TestBlueprint,
    TestBlueprintTopic,
)
from app.models.question import Question


class TestGenerationService:
    """Algorithmic examination generation from modular syllabus blueprints."""

    @staticmethod
    def validate_blueprint_availability(
        db: Session, blueprint_id: int
    ) -> dict[str, Any]:
        """
        Inspect available published question pool against each rule in a blueprint.
        Returns validation status, total requested, total available, and shortfall diagnostics.
        """
        blueprint = (
            db.query(TestBlueprint)
            .options(
                selectinload(TestBlueprint.topics).selectinload(
                    TestBlueprintTopic.topic
                )
            )
            .filter(TestBlueprint.id == blueprint_id)
            .first()
        )

        if not blueprint:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Test blueprint ID {blueprint_id} was not found.",
            )

        rules_summary: list[dict[str, Any]] = []
        is_sufficient = True
        total_required = 0

        for rule in blueprint.topics:
            total_required += rule.question_count
            query = db.query(Question).filter(
                Question.topic_id == rule.topic_id,
                Question.status == QuestionStatus.PUBLISHED,
            )

            if rule.difficulty is not None:
                query = query.filter(Question.difficulty == rule.difficulty)
            if rule.question_type is not None:
                query = query.filter(Question.question_type == rule.question_type)
            if rule.cognitive_level is not None:
                query = query.filter(Question.cognitive_level == rule.cognitive_level)

            available_count = query.count()
            shortfall = max(0, rule.question_count - available_count)
            if shortfall > 0:
                is_sufficient = False

            topic_title = rule.topic.title if rule.topic else f"Topic #{rule.topic_id}"

            rules_summary.append(
                {
                    "rule_id": rule.id,
                    "topic_id": rule.topic_id,
                    "topic_title": topic_title,
                    "difficulty": rule.difficulty.value if rule.difficulty else None,
                    "required_count": rule.question_count,
                    "available_count": available_count,
                    "shortfall": shortfall,
                    "is_met": shortfall == 0,
                }
            )

        return {
            "blueprint_id": blueprint.id,
            "blueprint_title": blueprint.title,
            "total_required_questions": total_required,
            "is_sufficient": is_sufficient,
            "rules": rules_summary,
        }

    @staticmethod
    def generate_mock_test_from_blueprint(
        db: Session,
        blueprint_id: int,
        custom_title: str | None = None,
        custom_slug: str | None = None,
        random_seed: int | None = None,
    ) -> MockTest:
        """
        Dynamically synthesize a production MockTest based on a blueprint matrix.
        Guarantees strict distribution adherence and raises clear error if pool is deficient.
        """
        blueprint = (
            db.query(TestBlueprint)
            .options(
                selectinload(TestBlueprint.topics).selectinload(
                    TestBlueprintTopic.topic
                )
            )
            .filter(TestBlueprint.id == blueprint_id)
            .first()
        )

        if not blueprint:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Test blueprint ID {blueprint_id} was not found.",
            )

        rng = random.Random(random_seed) if random_seed is not None else random.Random()

        selected_question_ids: set[int] = set()
        chosen_questions: list[Question] = []

        # Validate and accumulate questions per rule
        for rule in blueprint.topics:
            query = db.query(Question).filter(
                Question.topic_id == rule.topic_id,
                Question.status == QuestionStatus.PUBLISHED,
            )

            if rule.difficulty is not None:
                query = query.filter(Question.difficulty == rule.difficulty)
            if rule.question_type is not None:
                query = query.filter(Question.question_type == rule.question_type)
            if rule.cognitive_level is not None:
                query = query.filter(Question.cognitive_level == rule.cognitive_level)

            candidates = [q for q in query.all() if q.id not in selected_question_ids]

            if len(candidates) < rule.question_count:
                topic_title = (
                    rule.topic.title if rule.topic else f"Topic #{rule.topic_id}"
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"Insufficient published questions available for this test blueprint: "
                        f"required {rule.question_count} for '{topic_title}' "
                        f"(difficulty={rule.difficulty.value if rule.difficulty else 'ANY'}), "
                        f"but only found {len(candidates)} unselected questions."
                    ),
                )

            sampled = rng.sample(candidates, rule.question_count)
            for q in sampled:
                selected_question_ids.add(q.id)
                chosen_questions.append(q)

        # Shuffle selected questions to ensure inter-topic interleaving
        rng.shuffle(chosen_questions)

        # Generate unique slug
        base_slug = (
            custom_slug
            if custom_slug
            else f"{blueprint.slug}-gen-{random.randint(1000, 9999)}"
        )
        clean_slug = re.sub(r"[^a-zA-Z0-9_-]", "-", base_slug).lower()

        # Check existing slug collision
        counter = 1
        candidate_slug = clean_slug
        while db.query(MockTest).filter(MockTest.slug == candidate_slug).first():
            candidate_slug = f"{clean_slug}-{counter}"
            counter += 1

        title = custom_title or f"{blueprint.title} (Generated Examination)"

        # Infer test type
        distinct_topic_ids = {rule.topic_id for rule in blueprint.topics}
        if len(distinct_topic_ids) <= 1:
            inferred_type = MockTestType.TOPIC
        else:
            inferred_type = MockTestType.COMPREHENSIVE

        instructions = (
            f"Automated assessment generated from blueprint '{blueprint.title}'. "
            f"Complete all {len(chosen_questions)} questions within {blueprint.duration_minutes} minutes. "
            f"Requires 70% or higher to pass."
        )

        mock_test = MockTest(
            title=title,
            slug=candidate_slug,
            description=blueprint.description,
            difficulty=blueprint.difficulty or DifficultyLevel.BEGINNER,
            test_type=inferred_type,
            duration_minutes=blueprint.duration_minutes,
            total_questions=len(chosen_questions),
            passing_percentage=70.0,
            status=MockTestStatus.PUBLISHED,
            instructions=instructions,
        )
        db.add(mock_test)
        db.flush()

        for idx, question in enumerate(chosen_questions, start=1):
            link = MockTestQuestion(
                mock_test_id=mock_test.id,
                question_id=question.id,
                order_index=idx,
                points=question.points or 1,
            )
            db.add(link)

        db.commit()
        db.refresh(mock_test)
        return mock_test


test_generation_service = TestGenerationService()
