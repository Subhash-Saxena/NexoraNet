import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sqlalchemy import func, or_
from sqlalchemy.orm import Session, selectinload

from app.models.curriculum import Topic
from app.models.enums import (
    AttemptStatus,
    DifficultyLevel,
    MockTestStatus,
    MockTestType,
    QuestionStatus,
)
from app.models.mock_test import (
    MockTest,
    MockTestAttempt,
    MockTestQuestion,
    TestBlueprint,
    TestBlueprintTopic,
)
from app.models.question import Question
from app.schemas.mock_test import (
    AttemptHistoryItem,
    CatalogCategoryItem,
    CatalogDifficultyItem,
    CatalogDurationOption,
    CatalogFilterOptionsResponse,
    CatalogStatisticsResponse,
    CatalogTopicItem,
    CatalogTypeItem,
    MockTestBrief,
    MockTestPreviewResponse,
    MockTestPreviewTopicRule,
)

logger = logging.getLogger("nexoranet.catalog")


def _ensure_utc(dt: datetime) -> datetime:
    """Ensure a datetime object is timezone-aware in UTC."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


class MockTestCatalogService:
    """Service managing the comprehensive Mock Test Catalog and examination library."""

    @staticmethod
    def sync_catalog_from_files(
        db: Session, data_dir: Path | None = None
    ) -> dict[str, Any]:
        """
        Sync catalog definitions from JSON files into the database.
        Checks question bank pool availability and assigns PUBLISHED/READY or DRAFT/NOT_READY status.
        Populates deterministic question allocations for all ready mock tests.
        """
        if data_dir is None:
            data_dir = (
                Path(__file__).resolve().parents[2] / "data" / "mock_tests"
            )

        json_files = [
            data_dir / "beginner.json",
            data_dir / "intermediate.json",
            data_dir / "advanced.json",
            data_dir / "full_mocks.json",
        ]

        # Cache existing topics by slug
        topics_by_slug = {t.slug: t for t in db.query(Topic).all()}

        total_processed = 0
        ready_count = 0
        draft_count = 0
        questions_linked = 0

        for file_path in json_files:
            if not file_path.exists():
                logger.warning("Mock test catalog file not found: %s", file_path)
                continue

            with open(file_path, "r", encoding="utf-8") as f:
                test_specs = json.load(f)

            for spec in test_specs:
                total_processed += 1
                code = spec.get("code")
                slug = spec["slug"]
                title = spec["title"]
                test_type = MockTestType(spec["test_type"])
                difficulty = DifficultyLevel(spec["difficulty"])
                duration_minutes = spec["duration_minutes"]
                total_questions = spec["total_questions"]
                passing_percentage = float(spec.get("passing_percentage", 70.0))
                description = spec.get("description")
                instructions = spec.get("instructions")
                prerequisites = spec.get("prerequisites")
                tags_list = spec.get("tags", [])
                tags_str = json.dumps(tags_list)

                # 1. Blueprint & availability evaluation
                blueprint_spec = spec.get("blueprint", {})
                bp_title = blueprint_spec.get("title", f"{title} Blueprint")
                bp_slug = f"bp-{slug}"

                blueprint = (
                    db.query(TestBlueprint)
                    .filter(TestBlueprint.slug == bp_slug)
                    .first()
                )
                if not blueprint:
                    blueprint = TestBlueprint(
                        title=bp_title,
                        slug=bp_slug,
                        description=blueprint_spec.get("description", description),
                        total_questions=total_questions,
                        duration_minutes=duration_minutes,
                        difficulty=difficulty,
                    )
                    db.add(blueprint)
                    db.flush()
                else:
                    blueprint.title = bp_title
                    blueprint.description = blueprint_spec.get(
                        "description", description
                    )
                    blueprint.total_questions = total_questions
                    blueprint.duration_minutes = duration_minutes
                    blueprint.difficulty = difficulty

                # Reset blueprint topic rules
                db.query(TestBlueprintTopic).filter(
                    TestBlueprintTopic.blueprint_id == blueprint.id
                ).delete()
                db.flush()

                is_sufficient = True
                total_shortfall = 0
                rule_allocations: list[dict[str, Any]] = []

                for rule in blueprint_spec.get("topics", []):
                    t_slug = rule["topic_slug"]
                    q_count = rule["question_count"]
                    diff_str = rule.get("difficulty")
                    rule_diff = DifficultyLevel(diff_str) if diff_str else None

                    topic_entity = topics_by_slug.get(t_slug)
                    if not topic_entity:
                        logger.warning(
                            "Topic slug '%s' not found for test '%s'.", t_slug, slug
                        )
                        is_sufficient = False
                        total_shortfall += q_count
                        continue

                    bp_rule = TestBlueprintTopic(
                        blueprint_id=blueprint.id,
                        topic_id=topic_entity.id,
                        question_count=q_count,
                        difficulty=rule_diff,
                    )
                    db.add(bp_rule)
                    db.flush()

                    # Check available published questions in bank
                    q_query = db.query(Question).filter(
                        Question.topic_id == topic_entity.id,
                        Question.status == QuestionStatus.PUBLISHED,
                    )
                    if rule_diff is not None:
                        q_query = q_query.filter(Question.difficulty == rule_diff)

                    available = q_query.count()
                    shortfall = max(0, q_count - available)
                    if shortfall > 0:
                        is_sufficient = False
                        total_shortfall += shortfall

                    rule_allocations.append(
                        {
                            "topic_id": topic_entity.id,
                            "difficulty": rule_diff,
                            "count": q_count,
                            "shortfall": shortfall,
                        }
                    )

                # Determine status based on pool readiness
                catalog_status = (
                    MockTestStatus.PUBLISHED if is_sufficient else MockTestStatus.DRAFT
                )
                if is_sufficient:
                    ready_count += 1
                else:
                    draft_count += 1

                # 2. Mock Test Record
                mock_test = (
                    db.query(MockTest).filter(MockTest.slug == slug).first()
                )
                if not mock_test and code:
                    mock_test = (
                        db.query(MockTest).filter(MockTest.code == code).first()
                    )

                if not mock_test:
                    mock_test = MockTest(
                        title=title,
                        slug=slug,
                        code=code,
                        description=description,
                        test_type=test_type,
                        difficulty=difficulty,
                        duration_minutes=duration_minutes,
                        total_questions=total_questions,
                        passing_percentage=passing_percentage,
                        status=catalog_status,
                        instructions=instructions,
                        prerequisites=prerequisites,
                        tags=tags_str,
                        blueprint_id=blueprint.id,
                    )
                    db.add(mock_test)
                    db.flush()
                else:
                    mock_test.title = title
                    mock_test.code = code
                    mock_test.description = description
                    mock_test.test_type = test_type
                    mock_test.difficulty = difficulty
                    mock_test.duration_minutes = duration_minutes
                    mock_test.total_questions = total_questions
                    mock_test.passing_percentage = passing_percentage
                    mock_test.status = catalog_status
                    mock_test.instructions = instructions
                    mock_test.prerequisites = prerequisites
                    mock_test.tags = tags_str
                    mock_test.blueprint_id = blueprint.id

                # 3. If ready, link questions deterministically
                if is_sufficient:
                    # Check if already has correct question links
                    current_links_count = (
                        db.query(MockTestQuestion)
                        .filter(MockTestQuestion.mock_test_id == mock_test.id)
                        .count()
                    )
                    if current_links_count != total_questions:
                        db.query(MockTestQuestion).filter(
                            MockTestQuestion.mock_test_id == mock_test.id
                        ).delete()
                        db.flush()

                        chosen_questions: list[Question] = []
                        used_question_ids: set[int] = set()

                        for alloc in rule_allocations:
                            q_query = db.query(Question).filter(
                                Question.topic_id == alloc["topic_id"],
                                Question.status == QuestionStatus.PUBLISHED,
                            )
                            if alloc["difficulty"] is not None:
                                q_query = q_query.filter(
                                    Question.difficulty == alloc["difficulty"]
                                )
                            candidates = [
                                q
                                for q in q_query.order_by(Question.id.asc()).all()
                                if q.id not in used_question_ids
                            ]
                            sampled = candidates[: alloc["count"]]
                            for q in sampled:
                                used_question_ids.add(q.id)
                                chosen_questions.append(q)

                        for order_idx, q in enumerate(chosen_questions, start=1):
                            link = MockTestQuestion(
                                mock_test_id=mock_test.id,
                                question_id=q.id,
                                order_index=order_idx,
                                points=q.points or 1,
                            )
                            db.add(link)
                            questions_linked += 1

        db.commit()
        return {
            "total_processed": total_processed,
            "ready_count": ready_count,
            "draft_count": draft_count,
            "questions_linked": questions_linked,
        }

    @staticmethod
    def list_catalog_tests(
        db: Session,
        category: str | None = None,
        difficulty: str | None = None,
        test_type: str | None = None,
        topic: str | None = None,
        duration_min: int | None = None,
        duration_max: int | None = None,
        status: str | None = None,
        q: str | None = None,
        user_id: int | None = None,
    ) -> list[MockTestBrief]:
        """
        Query mock test catalog with multi-dimensional filtering, user attempt status, and availability diagnostics.
        """
        query = (
            db.query(MockTest)
            .options(
                selectinload(MockTest.test_questions)
                .selectinload(MockTestQuestion.question)
                .selectinload(Question.topic),
                selectinload(MockTest.blueprint)
                .selectinload(TestBlueprint.topics)
                .selectinload(TestBlueprintTopic.topic),
            )
        )

        # Category mapping
        if category and category.lower() != "all":
            cat = category.lower()
            if cat == "beginner":
                query = query.filter(MockTest.difficulty == DifficultyLevel.BEGINNER)
            elif cat == "intermediate":
                query = query.filter(MockTest.difficulty == DifficultyLevel.INTERMEDIATE)
            elif cat == "advanced":
                query = query.filter(MockTest.difficulty == DifficultyLevel.ADVANCED)
            elif cat == "comprehensive":
                query = query.filter(
                    MockTest.test_type.in_(
                        [MockTestType.COMPREHENSIVE, MockTestType.MIXED]
                    )
                )
            elif cat == "full_mocks":
                query = query.filter(MockTest.test_type == MockTestType.FULL_MOCK)
            elif cat == "recommended":
                # Recommended Practice (simple non-adaptive): Beginner fundamentals or ready tests
                query = query.filter(
                    MockTest.status == MockTestStatus.PUBLISHED,
                    MockTest.difficulty.in_(
                        [DifficultyLevel.BEGINNER, DifficultyLevel.MIXED]
                    ),
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

        if duration_min is not None:
            query = query.filter(MockTest.duration_minutes >= duration_min)

        if duration_max is not None:
            query = query.filter(MockTest.duration_minutes <= duration_max)

        if status:
            try:
                st_enum = MockTestStatus(status.upper())
                query = query.filter(MockTest.status == st_enum)
            except ValueError:
                return []

        if q and q.strip():
            term = f"%{q.strip()}%"
            query = query.filter(
                or_(
                    MockTest.title.ilike(term),
                    MockTest.description.ilike(term),
                    MockTest.code.ilike(term),
                    MockTest.tags.ilike(term),
                )
            )

        all_tests = query.order_by(MockTest.id.asc()).all()

        # Filter by topic if specified (matching question topic or blueprint topic)
        if topic and topic.strip():
            topic_str = topic.strip().lower()
            filtered: list[MockTest] = []
            for mt in all_tests:
                matched = False
                for tq in mt.test_questions:
                    if (
                        tq.question
                        and tq.question.topic
                        and (
                            tq.question.topic.slug == topic_str
                            or topic_str in tq.question.topic.title.lower()
                        )
                    ):
                        matched = True
                        break
                if not matched and mt.blueprint:
                    for bt in mt.blueprint.topics:
                        if bt.topic and (
                            bt.topic.slug == topic_str
                            or topic_str in bt.topic.title.lower()
                        ):
                            matched = True
                            break
                if matched:
                    filtered.append(mt)
            all_tests = filtered

        # Fetch user attempts for active sitting and historical stats
        user_attempts_map: dict[int, list[MockTestAttempt]] = {}
        if user_id:
            all_user_attempts = (
                db.query(MockTestAttempt)
                .filter(MockTestAttempt.user_id == user_id)
                .order_by(MockTestAttempt.id.desc())
                .all()
            )
            for att in all_user_attempts:
                user_attempts_map.setdefault(att.mock_test_id, []).append(att)

        now = datetime.now(timezone.utc)
        results: list[MockTestBrief] = []

        for mt in all_tests:
            # Topics covered
            topics_set: set[str] = set()
            for tq in mt.test_questions:
                if tq.question and tq.question.topic:
                    topics_set.add(tq.question.topic.title)
            if not topics_set and mt.blueprint:
                for bt in mt.blueprint.topics:
                    if bt.topic:
                        topics_set.add(bt.topic.title)

            # Parse tags
            tags_list: list[str] = []
            if mt.tags:
                try:
                    loaded = json.loads(mt.tags)
                    if isinstance(loaded, list):
                        tags_list = loaded
                except (json.JSONDecodeError, ValueError):
                    tags_list = [t.strip() for t in mt.tags.split(",") if t.strip()]

            # Determine readiness & shortfall
            is_ready = (
                mt.status == MockTestStatus.PUBLISHED and len(mt.test_questions) > 0
            )
            shortfall = 0
            if not is_ready:
                req = mt.total_questions
                avail = len(mt.test_questions)
                shortfall = max(0, req - avail)

            # User attempt statistics
            user_atts = user_attempts_map.get(mt.id, [])
            attempt_count = len(user_atts)
            latest_score = None
            latest_status = None
            active_attempt_id = None

            if user_atts:
                latest_att = user_atts[0]
                latest_score = latest_att.score
                latest_status = latest_att.status.value

                for att in user_atts:
                    if att.status == AttemptStatus.IN_PROGRESS:
                        exp = _ensure_utc(att.expires_at)
                        if now < exp:
                            active_attempt_id = att.id
                            break

            results.append(
                MockTestBrief(
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
                    prerequisites=mt.prerequisites,
                    tags=tags_list,
                    topics_covered=sorted(topics_set),
                    is_ready=is_ready,
                    shortfall=shortfall,
                    latest_attempt_score=latest_score,
                    latest_attempt_status=latest_status,
                    active_attempt_id=active_attempt_id,
                    attempt_count=attempt_count,
                )
            )

        # Sort: Ready tests first, then by difficulty (Beginner -> Intermediate -> Advanced -> Mixed), then ID
        diff_order = {
            DifficultyLevel.BEGINNER: 1,
            DifficultyLevel.INTERMEDIATE: 2,
            DifficultyLevel.ADVANCED: 3,
            DifficultyLevel.MIXED: 4,
        }
        results.sort(
            key=lambda t: (
                0 if t.is_ready else 1,
                diff_order.get(t.difficulty, 5),
                t.id,
            )
        )
        return results

    @staticmethod
    def get_catalog_statistics(db: Session) -> CatalogStatisticsResponse:
        """Get aggregate metrics across the mock test catalog."""
        tests = (
            db.query(MockTest)
            .options(selectinload(MockTest.test_questions))
            .all()
        )

        ready_count = 0
        draft_count = 0
        beginner_count = 0
        intermediate_count = 0
        advanced_count = 0
        full_mock_count = 0
        questions_rep = 0

        for t in tests:
            is_ready = t.status == MockTestStatus.PUBLISHED and len(t.test_questions) > 0
            if is_ready:
                ready_count += 1
            else:
                draft_count += 1

            if t.difficulty == DifficultyLevel.BEGINNER:
                beginner_count += 1
            elif t.difficulty == DifficultyLevel.INTERMEDIATE:
                intermediate_count += 1
            elif t.difficulty == DifficultyLevel.ADVANCED:
                advanced_count += 1

            if t.test_type == MockTestType.FULL_MOCK:
                full_mock_count += 1

            questions_rep += len(t.test_questions)

        return CatalogStatisticsResponse(
            total_tests=len(tests),
            ready_tests=ready_count,
            draft_tests=draft_count,
            beginner_tests=beginner_count,
            intermediate_tests=intermediate_count,
            advanced_tests=advanced_count,
            full_mock_tests=full_mock_count,
            total_questions_represented=questions_rep,
        )

    @staticmethod
    def list_catalog_categories(
        db: Session, user_id: int | None = None
    ) -> list[CatalogCategoryItem]:
        """List predefined catalog categories with live test counts."""
        tests = db.query(MockTest).all()

        total = len(tests)
        beginner = sum(1 for t in tests if t.difficulty == DifficultyLevel.BEGINNER)
        intermediate = sum(1 for t in tests if t.difficulty == DifficultyLevel.INTERMEDIATE)
        advanced = sum(1 for t in tests if t.difficulty == DifficultyLevel.ADVANCED)
        comprehensive = sum(
            1
            for t in tests
            if t.test_type in [MockTestType.COMPREHENSIVE, MockTestType.MIXED]
        )
        full_mocks = sum(1 for t in tests if t.test_type == MockTestType.FULL_MOCK)
        recommended = sum(
            1
            for t in tests
            if t.status == MockTestStatus.PUBLISHED
            and t.difficulty in [DifficultyLevel.BEGINNER, DifficultyLevel.MIXED]
        )

        return [
            CatalogCategoryItem(
                key="all",
                title="All Tests",
                description="Complete library of networking and cybersecurity mock tests.",
                test_count=total,
                icon="Layers",
            ),
            CatalogCategoryItem(
                key="recommended",
                title="Recommended Practice",
                description="Curated high-yield practice tests to build your core networking foundation.",
                test_count=recommended,
                icon="Star",
            ),
            CatalogCategoryItem(
                key="beginner",
                title="Beginner",
                description="Core networking fundamentals, OSI model, IP addressing, and devices.",
                test_count=beginner,
                icon="ShieldCheck",
            ),
            CatalogCategoryItem(
                key="intermediate",
                title="Intermediate",
                description="Subnetting, routing, switching, DNS/DHCP, firewalls, and packet troubleshooting.",
                test_count=intermediate,
                icon="Sliders",
            ),
            CatalogCategoryItem(
                key="advanced",
                title="Advanced",
                description="Deep packet analysis, detection engineering, reconnaissance defense, and SOC analytics.",
                test_count=advanced,
                icon="Cpu",
            ),
            CatalogCategoryItem(
                key="comprehensive",
                title="Comprehensive",
                description="Cross-topic syntheses testing end-to-end network protocol mastery.",
                test_count=comprehensive,
                icon="FileSpreadsheet",
            ),
            CatalogCategoryItem(
                key="full_mocks",
                title="Full Mocks",
                description="Full-length timed examinations simulating industry certification tests.",
                test_count=full_mocks,
                icon="Award",
            ),
        ]

    @staticmethod
    def list_catalog_topics(db: Session) -> list[CatalogTopicItem]:
        """List distinct topics represented in the mock test catalog."""
        # Find topics from mock test questions and blueprints
        topic_counts: dict[int, dict[str, Any]] = {}

        tests = (
            db.query(MockTest)
            .options(
                selectinload(MockTest.test_questions)
                .selectinload(MockTestQuestion.question)
                .selectinload(Question.topic),
                selectinload(MockTest.blueprint)
                .selectinload(TestBlueprint.topics)
                .selectinload(TestBlueprintTopic.topic),
            )
            .all()
        )

        for mt in tests:
            seen_topics_for_test: set[int] = set()
            for tq in mt.test_questions:
                if tq.question and tq.question.topic:
                    t = tq.question.topic
                    seen_topics_for_test.add(t.id)
                    if t.id not in topic_counts:
                        topic_counts[t.id] = {
                            "id": t.id,
                            "title": t.title,
                            "slug": t.slug,
                            "count": 0,
                        }
            if mt.blueprint:
                for bt in mt.blueprint.topics:
                    if bt.topic:
                        t = bt.topic
                        seen_topics_for_test.add(t.id)
                        if t.id not in topic_counts:
                            topic_counts[t.id] = {
                                "id": t.id,
                                "title": t.title,
                                "slug": t.slug,
                                "count": 0,
                            }
            for tid in seen_topics_for_test:
                topic_counts[tid]["count"] += 1

        items = [
            CatalogTopicItem(
                topic_id=v["id"],
                topic_title=v["title"],
                topic_slug=v["slug"],
                test_count=v["count"],
            )
            for v in topic_counts.values()
        ]
        items.sort(key=lambda x: (-x.test_count, x.topic_title))
        return items

    @staticmethod
    def list_catalog_difficulties(db: Session) -> list[CatalogDifficultyItem]:
        """List difficulties with test counts."""
        diff_labels = {
            DifficultyLevel.BEGINNER: "Beginner",
            DifficultyLevel.INTERMEDIATE: "Intermediate",
            DifficultyLevel.ADVANCED: "Advanced",
            DifficultyLevel.MIXED: "Mixed",
        }
        counts = dict(
            db.query(MockTest.difficulty, func.count(MockTest.id))
            .group_by(MockTest.difficulty)
            .all()
        )

        return [
            CatalogDifficultyItem(
                difficulty=diff,
                label=diff_labels.get(diff, diff.value),
                test_count=counts.get(diff, 0),
            )
            for diff in DifficultyLevel
            if diff in diff_labels
        ]

    @staticmethod
    def list_catalog_types(db: Session) -> list[CatalogTypeItem]:
        """List mock test types with test counts."""
        type_labels = {
            MockTestType.TOPIC: "Topic Quiz",
            MockTestType.DIFFICULTY: "Difficulty Assessment",
            MockTestType.MIXED: "Mixed Assessment",
            MockTestType.COMPREHENSIVE: "Comprehensive",
            MockTestType.PRACTICE: "Practice Test",
            MockTestType.FULL_MOCK: "Full Mock Exam",
        }
        counts = dict(
            db.query(MockTest.test_type, func.count(MockTest.id))
            .group_by(MockTest.test_type)
            .all()
        )

        return [
            CatalogTypeItem(
                test_type=t,
                label=type_labels.get(t, t.value),
                test_count=counts.get(t, 0),
            )
            for t in MockTestType
        ]

    @staticmethod
    def get_filter_options(
        db: Session, user_id: int | None = None
    ) -> CatalogFilterOptionsResponse:
        """Get aggregate filter options for catalog UI."""
        return CatalogFilterOptionsResponse(
            categories=MockTestCatalogService.list_catalog_categories(db, user_id),
            topics=MockTestCatalogService.list_catalog_topics(db),
            difficulties=MockTestCatalogService.list_catalog_difficulties(db),
            types=MockTestCatalogService.list_catalog_types(db),
            duration_ranges=[
                CatalogDurationOption(label="Quick (< 20 mins)", min_minutes=0, max_minutes=20),
                CatalogDurationOption(label="Standard (20-45 mins)", min_minutes=20, max_minutes=45),
                CatalogDurationOption(label="Extended (45-60 mins)", min_minutes=45, max_minutes=60),
                CatalogDurationOption(label="Full Mock (60+ mins)", min_minutes=60, max_minutes=180),
            ],
        )

    @staticmethod
    def get_test_preview(
        db: Session, test_id_or_slug: str | int
    ) -> MockTestPreviewResponse | None:
        """
        Generate a safe examination preview revealing syllabus coverage,
        blueprint rules, and pool readiness WITHOUT exposing question keys or answers.
        """
        query = (
            db.query(MockTest)
            .options(
                selectinload(MockTest.test_questions)
                .selectinload(MockTestQuestion.question)
                .selectinload(Question.topic),
                selectinload(MockTest.blueprint)
                .selectinload(TestBlueprint.topics)
                .selectinload(TestBlueprintTopic.topic),
            )
        )
        if isinstance(test_id_or_slug, int) or str(test_id_or_slug).isdigit():
            mt = query.filter(MockTest.id == int(test_id_or_slug)).first()
        else:
            mt = query.filter(MockTest.slug == str(test_id_or_slug)).first()

        if not mt:
            return None

        # Build syllabus rules from blueprint
        rules_preview: list[MockTestPreviewTopicRule] = []
        is_ready = mt.status == MockTestStatus.PUBLISHED and len(mt.test_questions) > 0
        total_shortfall = 0

        topics_set: set[str] = set()

        if mt.blueprint and mt.blueprint.topics:
            for rule in mt.blueprint.topics:
                t_title = rule.topic.title if rule.topic else f"Topic #{rule.topic_id}"
                t_slug = rule.topic.slug if rule.topic else "unknown"
                topics_set.add(t_title)

                # Query question bank pool
                q_query = db.query(Question).filter(
                    Question.topic_id == rule.topic_id,
                    Question.status == QuestionStatus.PUBLISHED,
                )
                if rule.difficulty is not None:
                    q_query = q_query.filter(Question.difficulty == rule.difficulty)

                avail = q_query.count()
                shortfall = max(0, rule.question_count - avail)
                if shortfall > 0:
                    total_shortfall += shortfall

                rules_preview.append(
                    MockTestPreviewTopicRule(
                        topic_title=t_title,
                        topic_slug=t_slug,
                        difficulty=rule.difficulty,
                        question_count=rule.question_count,
                        available_in_bank=avail,
                        is_met=shortfall == 0,
                    )
                )

        for tq in mt.test_questions:
            if tq.question and tq.question.topic:
                topics_set.add(tq.question.topic.title)

        # Parse tags
        tags_list: list[str] = []
        if mt.tags:
            try:
                loaded = json.loads(mt.tags)
                if isinstance(loaded, list):
                    tags_list = loaded
            except (json.JSONDecodeError, ValueError):
                tags_list = [t.strip() for t in mt.tags.split(",") if t.strip()]

        # Generate "what you will practice" bullet points based on covered topics
        practice_points = [
            f"Mastering core principles of {topic_name}"
            for topic_name in sorted(topics_set)[:4]
        ]
        if mt.test_type == MockTestType.FULL_MOCK:
            practice_points.append(
                f"Full-length exam time management ({mt.duration_minutes} minutes, {mt.total_questions} questions)"
            )
        practice_points.append(f"Minimum passing threshold: {int(mt.passing_percentage)}%")

        return MockTestPreviewResponse(
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
            prerequisites=mt.prerequisites,
            tags=tags_list,
            is_ready=is_ready,
            shortfall=total_shortfall,
            topics_covered=sorted(topics_set),
            what_you_will_practice=practice_points,
            syllabus_rules=rules_preview,
        )

    @staticmethod
    def get_attempt_history(
        db: Session, test_id_or_slug: str | int, user_id: int
    ) -> list[AttemptHistoryItem]:
        """Fetch complete chronological attempt history for a specific student and test."""
        query = db.query(MockTest)
        if isinstance(test_id_or_slug, int) or str(test_id_or_slug).isdigit():
            mt = query.filter(MockTest.id == int(test_id_or_slug)).first()
        else:
            mt = query.filter(MockTest.slug == str(test_id_or_slug)).first()

        if not mt:
            return []

        attempts = (
            db.query(MockTestAttempt)
            .options(selectinload(MockTestAttempt.result))
            .filter(
                MockTestAttempt.mock_test_id == mt.id,
                MockTestAttempt.user_id == user_id,
            )
            .order_by(MockTestAttempt.id.desc())
            .all()
        )

        history: list[AttemptHistoryItem] = []
        for att in attempts:
            started = _ensure_utc(att.started_at).isoformat()
            submitted = (
                _ensure_utc(att.submitted_at).isoformat() if att.submitted_at else None
            )

            res = att.result
            total_pts = res.total_points if res else 100.0
            passed = res.passed if res else (att.percentage >= mt.passing_percentage)
            time_taken = res.time_taken_seconds if res else 0

            history.append(
                AttemptHistoryItem(
                    attempt_id=att.id,
                    test_id=mt.id,
                    test_title=mt.title,
                    test_slug=mt.slug,
                    difficulty=mt.difficulty,
                    test_type=mt.test_type,
                    status=att.status,
                    score=att.score,
                    total_points=total_pts,
                    percentage=att.percentage,
                    passed=passed,
                    started_at=started,
                    submitted_at=submitted,
                    time_taken_seconds=time_taken,
                )
            )
        return history


mock_test_catalog_service = MockTestCatalogService()
