import json
import logging
import sys
from pathlib import Path

# Ensure backend root is on sys.path
backend_root = Path(__file__).resolve().parents[2]
if str(backend_root) not in sys.path:
    sys.path.insert(0, str(backend_root))

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models import (
    ContentType,
    Course,
    DifficultyLevel,
    Lab,
    LabQuestion,
    LabStatus,
    LabStep,
    Lesson,
    MockTest,
    MockTestQuestion,
    MockTestType,
    Module,
    Question,
    QuestionOption,
    QuestionTag,
    QuestionType,
    TestBlueprint,
    TestBlueprintTopic,
    Topic,
    User,
    UserRole,
)
from app.core.security import hash_password
from app.seed.data_curriculum import COURSE_DATA, MODULES_DATA, SAMPLE_LESSONS
from app.seed.data_labs_advanced import ADVANCED_PLANNED_LABS
from app.seed.data_labs_beginner import BEGINNER_LABS
from app.seed.data_labs_intermediate import INTERMEDIATE_LABS
from app.seed.data_lessons_curriculum import (
    TOPIC_METADATA_EXTRAS,
    TOPIC_PREREQUISITES_MAP,
)
from app.seed.data_mock_tests import MOCK_TESTS_DATA, SAMPLE_BLUEPRINTS
from app.seed.data_questions import SAMPLE_QUESTIONS, TAGS_DATA
from app.seed.lessons_advanced import ADVANCED_LESSONS
from app.seed.lessons_beginner import BEGINNER_LESSONS
from app.seed.lessons_intermediate import INTERMEDIATE_LESSONS
from app.services.question_validator import validate_question_structure

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("nexoranet.seed")


def seed_database(db: Session) -> dict[str, int]:
    """
    Idempotent database seeder for NexoraNet curriculum, taxonomy,
    question bank, and mock tests.
    """
    stats = {
        "courses": 0,
        "modules": 0,
        "topics": 0,
        "lessons": 0,
        "tags": 0,
        "questions": 0,
        "mock_tests": 0,
        "blueprints": 0,
        "labs": 0,
        "lab_steps": 0,
        "users": 0,
    }

    # 1. Seed or retrieve demo users
    admin_user = db.query(User).filter(User.username == "admin").first()
    if not admin_user:
        admin_user = User(
            username="admin",
            email="admin@nexoranet.com",
            password_hash=hash_password("AdminPassword2026!"),
            display_name="Security Administrator",
            current_level="Commander Defend-IV",
            role=UserRole.ADMIN,
            is_active=True,
        )
        db.add(admin_user)
        db.flush()
        stats["users"] += 1
        logger.info("Created admin user: admin")
    elif admin_user.role != UserRole.ADMIN:
        admin_user.role = UserRole.ADMIN
        db.flush()

    student_user = db.query(User).filter(User.username == "student1").first()
    if not student_user:
        student_user = User(
            username="student1",
            email="student@nexoranet.com",
            password_hash=hash_password("ProductionPassword2026!"),
            display_name="Pilot Student",
            current_level="Cadet Defend-I",
            role=UserRole.STUDENT,
            is_active=True,
        )
        db.add(student_user)
        db.flush()
        stats["users"] += 1
        logger.info("Created demo student user: student1")

    demo_user = db.query(User).filter(User.username == "cadet_student").first()
    if not demo_user:
        demo_user = User(
            username="cadet_student",
            email="cadet@nexoranet.internal",
            password_hash=hash_password("CadetPassword2026!"),
            display_name="Cadet Student",
            current_level="Cadet Defend-I",
            role=UserRole.STUDENT,
            is_active=True,
        )
        db.add(demo_user)
        db.flush()
        stats["users"] += 1
        logger.info("Created demo student user: cadet_student")

    dev_user = db.query(User).filter(User.username == "student_dev").first()
    if not dev_user:
        dev_user = User(
            username="student_dev",
            email="dev@nexoranet.internal",
            password_hash=hash_password("StudentPassword2026!"),
            display_name="Alex Rivera (Cadet)",
            current_level="Cadet Defend-I",
            role=UserRole.STUDENT,
            is_active=True,
        )
        db.add(dev_user)
        db.flush()
        stats["users"] += 1
        logger.info("Created dev student user: student_dev")

    # 2. Seed Course
    course = db.query(Course).filter(Course.slug == COURSE_DATA["slug"]).first()
    if not course:
        course = Course(
            title=COURSE_DATA["title"],
            slug=COURSE_DATA["slug"],
            description=COURSE_DATA["description"],
            level=COURSE_DATA["level"],
            estimated_hours=COURSE_DATA["estimated_hours"],
            is_published=COURSE_DATA["is_published"],
        )
        db.add(course)
        db.flush()
        stats["courses"] += 1
        logger.info("Created course: %s", course.title)

    # 3. Seed Modules and Topics
    topic_map: dict[str, Topic] = {}

    for mod_data in MODULES_DATA:
        module = (
            db.query(Module)
            .filter(Module.course_id == course.id, Module.slug == mod_data["slug"])
            .first()
        )
        if not module:
            module = Module(
                course_id=course.id,
                title=mod_data["title"],
                slug=mod_data["slug"],
                description=mod_data["description"],
                order_index=mod_data["order_index"],
                difficulty=mod_data["difficulty"],
                is_published=True,
            )
            db.add(module)
            db.flush()
            stats["modules"] += 1

        for idx, (t_title, t_slug, t_desc) in enumerate(mod_data["topics"], start=1):
            topic = (
                db.query(Topic)
                .filter(Topic.module_id == module.id, Topic.slug == t_slug)
                .first()
            )
            extra = TOPIC_METADATA_EXTRAS.get(t_slug, {})
            est_mins = extra.get("estimated_minutes", 30)
            learn_objs = (
                json.dumps(extra.get("learning_objectives", []))
                if extra.get("learning_objectives")
                else None
            )
            sec_rel = extra.get("security_relevance")

            if not topic:
                topic = Topic(
                    module_id=module.id,
                    title=t_title,
                    slug=t_slug,
                    description=t_desc,
                    difficulty=mod_data["difficulty"],
                    order_index=idx,
                    estimated_minutes=est_mins,
                    learning_objectives=learn_objs,
                    security_relevance=sec_rel,
                    is_published=True,
                )
                db.add(topic)
                db.flush()
                stats["topics"] += 1
            else:
                if not topic.security_relevance and sec_rel:
                    topic.security_relevance = sec_rel
                if not topic.learning_objectives and learn_objs:
                    topic.learning_objectives = learn_objs
                if extra.get("estimated_minutes"):
                    topic.estimated_minutes = est_mins

            topic_map[t_slug] = topic

    # Connect topic prerequisites
    for t_slug, prereq_slugs in TOPIC_PREREQUISITES_MAP.items():
        curr_topic = topic_map.get(t_slug)
        if not curr_topic:
            continue
        for p_slug in prereq_slugs:
            p_topic = topic_map.get(p_slug)
            if p_topic and p_topic not in curr_topic.prerequisites:
                curr_topic.prerequisites.append(p_topic)
    db.flush()

    logger.info("Total topics registered: %d", len(topic_map))

    # 4. Seed Comprehensive Lessons
    all_lessons_data = (
        BEGINNER_LESSONS + INTERMEDIATE_LESSONS + ADVANCED_LESSONS + SAMPLE_LESSONS
    )
    for les_data in all_lessons_data:
        parent_topic = topic_map.get(les_data["topic_slug"])
        if not parent_topic:
            continue

        existing_lesson = (
            db.query(Lesson)
            .filter(Lesson.topic_id == parent_topic.id, Lesson.slug == les_data["slug"])
            .first()
        )
        if not existing_lesson:
            lesson = Lesson(
                topic_id=parent_topic.id,
                title=les_data["title"],
                slug=les_data["slug"],
                description=les_data.get("description"),
                content=les_data["content"],
                content_type=les_data.get("content_type", ContentType.LESSON),
                order_index=les_data.get("order_index", 1),
                estimated_minutes=les_data.get("estimated_minutes", 20),
                difficulty=les_data.get("difficulty", parent_topic.difficulty),
                is_published=True,
            )
            db.add(lesson)
            db.flush()
            stats["lessons"] += 1
        else:
            existing_lesson.content = les_data["content"]
            existing_lesson.description = les_data.get("description")
            existing_lesson.estimated_minutes = les_data.get(
                "estimated_minutes", existing_lesson.estimated_minutes
            )
            stats["lessons"] += 1

    # 5. Seed Tags
    tag_map: dict[str, QuestionTag] = {}
    for t_data in TAGS_DATA:
        tag = db.query(QuestionTag).filter(QuestionTag.slug == t_data["slug"]).first()
        if not tag:
            tag = QuestionTag(name=t_data["name"], slug=t_data["slug"])
            db.add(tag)
            db.flush()
            stats["tags"] += 1
        tag_map[t_data["slug"]] = tag

    # 6. Seed Sample Questions
    seeded_questions: list[Question] = []
    for q_data in SAMPLE_QUESTIONS:
        parent_topic = topic_map.get(q_data["topic_slug"])
        if not parent_topic:
            continue

        # Validate question before insertion
        validate_question_structure(
            question_text=q_data["question_text"],
            question_type=q_data["question_type"],
            difficulty=q_data["difficulty"],
            points=q_data["points"],
            explanation=q_data["explanation"],
            options=q_data.get("options", []),
        )

        existing_q = (
            db.query(Question)
            .filter(
                Question.topic_id == parent_topic.id,
                Question.question_text == q_data["question_text"],
            )
            .first()
        )
        if not existing_q:
            question = Question(
                topic_id=parent_topic.id,
                question_text=q_data["question_text"],
                question_type=q_data["question_type"],
                difficulty=q_data["difficulty"],
                cognitive_level=q_data["cognitive_level"],
                explanation=q_data["explanation"],
                learning_objective=q_data.get("learning_objective"),
                points=q_data["points"],
                estimated_seconds=q_data["estimated_seconds"],
            )
            # Associate tags
            for t_slug in q_data.get("tags", []):
                if t_slug in tag_map:
                    question.tags.append(tag_map[t_slug])

            db.add(question)
            db.flush()

            # Add options
            for opt_data in q_data.get("options", []):
                option = QuestionOption(
                    question_id=question.id,
                    option_text=opt_data["option_text"],
                    is_correct=opt_data["is_correct"],
                    order_index=opt_data["order_index"],
                )
                db.add(option)

            db.flush()
            seeded_questions.append(question)
            stats["questions"] += 1
        else:
            seeded_questions.append(existing_q)

    # 7. Seed Sample Mock Tests
    for mt_data in MOCK_TESTS_DATA:
        mock_test = db.query(MockTest).filter(MockTest.slug == mt_data["slug"]).first()
        if not mock_test:
            mock_test = MockTest(
                title=mt_data["title"],
                slug=mt_data["slug"],
                description=mt_data["description"],
                difficulty=mt_data["difficulty"],
                test_type=mt_data.get("test_type", MockTestType.TOPIC),
                duration_minutes=mt_data["duration_minutes"],
                total_questions=mt_data["total_questions"],
                passing_percentage=mt_data["passing_percentage"],
                status=mt_data["status"],
                instructions=mt_data.get("instructions"),
            )
            db.add(mock_test)
            db.flush()
            stats["mock_tests"] += 1
        else:
            mock_test.title = mt_data["title"]
            mock_test.description = mt_data["description"]
            mock_test.difficulty = mt_data["difficulty"]
            mock_test.test_type = mt_data.get("test_type", MockTestType.TOPIC)
            mock_test.duration_minutes = mt_data["duration_minutes"]
            mock_test.total_questions = mt_data["total_questions"]
            mock_test.passing_percentage = mt_data["passing_percentage"]
            mock_test.status = mt_data["status"]
            mock_test.instructions = mt_data.get("instructions")
            # Clear old question links to re-populate
            db.query(MockTestQuestion).filter(MockTestQuestion.mock_test_id == mock_test.id).delete()
            db.flush()

        # Attach question links
        for order_idx, q_idx in enumerate(mt_data["question_indices"], start=1):
            if q_idx < len(seeded_questions):
                target_q = seeded_questions[q_idx]
                mt_question = MockTestQuestion(
                    mock_test_id=mock_test.id,
                    question_id=target_q.id,
                    order_index=order_idx,
                    points=target_q.points,
                )
                db.add(mt_question)

    # 8. Seed Sample Test Blueprints
    for bp_data in SAMPLE_BLUEPRINTS:
        blueprint = (
            db.query(TestBlueprint)
            .filter(TestBlueprint.slug == bp_data["slug"])
            .first()
        )
        if not blueprint:
            blueprint = TestBlueprint(
                title=bp_data["title"],
                slug=bp_data["slug"],
                description=bp_data["description"],
                total_questions=bp_data["total_questions"],
                duration_minutes=bp_data["duration_minutes"],
                difficulty=bp_data["difficulty"],
            )
            db.add(blueprint)
            db.flush()
            stats["blueprints"] += 1
        else:
            blueprint.title = bp_data["title"]
            blueprint.description = bp_data["description"]
            blueprint.total_questions = bp_data["total_questions"]
            blueprint.duration_minutes = bp_data["duration_minutes"]
            blueprint.difficulty = bp_data["difficulty"]
            db.query(TestBlueprintTopic).filter(TestBlueprintTopic.blueprint_id == blueprint.id).delete()
            db.flush()

        for bp_topic_rule in bp_data["topics"]:
            target_topic = topic_map.get(bp_topic_rule["topic_slug"])
            if target_topic:
                rule = TestBlueprintTopic(
                    blueprint_id=blueprint.id,
                    topic_id=target_topic.id,
                    question_count=bp_topic_rule["count"],
                    difficulty=bp_topic_rule.get("difficulty"),
                )
                db.add(rule)

    # 9. Seed Hands-on Labs
    all_labs_data = BEGINNER_LABS + INTERMEDIATE_LABS + ADVANCED_PLANNED_LABS
    for l_data in all_labs_data:
        parent_topic = topic_map.get(l_data["topic_slug"])
        if not parent_topic:
            parent_topic = next(iter(topic_map.values()))

        lab = db.query(Lab).filter(Lab.slug == l_data["slug"]).first()
        lab_status = (
            LabStatus.DRAFT
            if l_data.get("status") == "DRAFT"
            else LabStatus.PUBLISHED
        )
        objs_json = (
            json.dumps(l_data.get("objectives", []))
            if l_data.get("objectives")
            else None
        )
        prereq_json = (
            json.dumps(l_data.get("prerequisites", []))
            if l_data.get("prerequisites")
            else None
        )

        if not lab:
            lab = Lab(
                topic_id=parent_topic.id,
                title=l_data["title"],
                slug=l_data["slug"],
                description=l_data["description"],
                difficulty=DifficultyLevel(l_data["difficulty"]),
                estimated_minutes=l_data.get("estimated_minutes", 20),
                objectives=objs_json,
                prerequisites=prereq_json,
                environment_type=l_data.get("environment_type", "LOCAL_SYSTEM"),
                instructions=l_data.get("instructions"),
                status=lab_status,
                is_published=True,
            )
            db.add(lab)
            db.flush()
            stats["labs"] += 1
        else:
            lab.title = l_data["title"]
            lab.description = l_data["description"]
            lab.difficulty = DifficultyLevel(l_data["difficulty"])
            lab.estimated_minutes = l_data.get("estimated_minutes", 20)
            lab.objectives = objs_json
            lab.prerequisites = prereq_json
            lab.environment_type = l_data.get("environment_type", "LOCAL_SYSTEM")
            lab.instructions = l_data.get("instructions")
            lab.status = lab_status

        # Seed or update steps
        for step_data in l_data.get("steps", []):
            step = (
                db.query(LabStep)
                .filter(
                    LabStep.lab_id == lab.id,
                    LabStep.step_number == step_data["step_number"],
                )
                .first()
            )
            if not step:
                step = LabStep(
                    lab_id=lab.id,
                    step_number=step_data["step_number"],
                    title=step_data["title"],
                    description=step_data.get("description"),
                    instructions=step_data["instructions"],
                    hint=step_data.get("hint"),
                    expected_observation=step_data.get("expected_observation"),
                    validation_type=step_data.get("validation_type", "manual"),
                    points=step_data.get("points", 10),
                    is_required=step_data.get("is_required", True),
                )
                db.add(step)
                db.flush()
                stats["lab_steps"] += 1
            else:
                step.title = step_data["title"]
                step.description = step_data.get("description")
                step.instructions = step_data["instructions"]
                step.hint = step_data.get("hint")
                step.expected_observation = step_data.get("expected_observation")
                step.validation_type = step_data.get("validation_type", "manual")
                step.points = step_data.get("points", 10)
                step.is_required = step_data.get("is_required", True)

            # Seed question if present
            if "question" in step_data:
                q_info = step_data["question"]
                q_data_str = (
                    json.dumps(q_info["answer_data"])
                    if isinstance(q_info["answer_data"], (dict, list))
                    else str(q_info["answer_data"])
                )
                q_type = QuestionType(q_info.get("question_type", "SINGLE_CHOICE"))

                lab_q = (
                    db.query(LabQuestion)
                    .filter(
                        LabQuestion.lab_id == lab.id, LabQuestion.step_id == step.id
                    )
                    .first()
                )
                if not lab_q:
                    lab_q = LabQuestion(
                        lab_id=lab.id,
                        step_id=step.id,
                        question_text=q_info["question_text"],
                        question_type=q_type,
                        answer_data=q_data_str,
                        explanation=q_info.get("explanation"),
                        points=q_info.get("points", step.points),
                        order_index=step.step_number,
                    )
                    db.add(lab_q)
                else:
                    lab_q.question_text = q_info["question_text"]
                    lab_q.question_type = q_type
                    lab_q.answer_data = q_data_str
                    lab_q.explanation = q_info.get("explanation")
                    lab_q.points = q_info.get("points", step.points)

    db.commit()
    return stats


def main() -> None:
    db = SessionLocal()
    try:
        logger.info("Initiating NexoraNet database seed...")
        stats = seed_database(db)
        logger.info("Database seeding successfully completed!")
        for key, val in stats.items():
            logger.info("  %s: %d", key.capitalize(), val)
    except Exception:
        db.rollback()
        logger.exception("Database seeding failed.")
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
