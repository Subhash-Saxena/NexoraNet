import json
from datetime import datetime, timezone

from sqlalchemy import func, or_
from sqlalchemy.orm import Session, selectinload

from app.models.curriculum import Lesson, Module, Topic
from app.models.enums import DifficultyLevel, ProgressStatus, UserRole
from app.models.progress import LessonBookmark, LessonProgress, TopicProgress
from app.models.user import User
from app.schemas.curriculum import LessonBrief, TopicBrief
from app.schemas.learning import (
    BookmarkItem,
    ContinueLearningItem,
    LearningProgressResponse,
    LessonBriefWithProgress,
    LessonDetailExtended,
    LevelProgress,
    PrerequisiteTopicBrief,
    RelatedItemBrief,
    SearchResultItem,
    TopicDetailExtended,
)


def get_current_dev_user(db: Session) -> User:
    """Retrieve the development student user.

    Production authentication (JWT/session tokens) will be introduced in a later phase.
    This ensures server-enforced user consistency rather than trusting client parameters.
    """
    user = db.query(User).filter(User.username == "student_dev").first()
    if not user:
        user = db.query(User).filter(User.role == UserRole.STUDENT).first()
    if not user:
        user = User(
            username="student_dev",
            email="student@nexoranet.internal",
            password_hash="argon2_step3_dev_placeholder_hash",
            display_name="Alex Rivera (Cadet)",
            role=UserRole.STUDENT,
            current_level="Cadet Defend-I",
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


def get_next_and_previous_lesson(
    db: Session, current_lesson: Lesson
) -> tuple[LessonBrief | None, LessonBrief | None]:
    """Calculate linear previous and next lessons within the topic, or across topics in the module."""
    # Check within same topic first
    all_topic_lessons = (
        db.query(Lesson)
        .filter(
            Lesson.topic_id == current_lesson.topic_id, Lesson.is_published.is_(True)
        )
        .order_by(Lesson.order_index)
        .all()
    )

    prev_l = None
    next_l = None
    current_idx = -1
    for i, l in enumerate(all_topic_lessons):
        if l.id == current_lesson.id:
            current_idx = i
            break

    if current_idx > 0:
        prev_l = LessonBrief.model_validate(all_topic_lessons[current_idx - 1])
    if current_idx != -1 and current_idx < len(all_topic_lessons) - 1:
        next_l = LessonBrief.model_validate(all_topic_lessons[current_idx + 1])

    # If no next lesson in same topic, check next topic's first lesson
    if not next_l:
        current_topic = current_lesson.topic
        if current_topic:
            next_topic = (
                db.query(Topic)
                .filter(
                    Topic.module_id == current_topic.module_id,
                    Topic.order_index > current_topic.order_index,
                    Topic.is_published.is_(True),
                )
                .order_by(Topic.order_index)
                .first()
            )
            if next_topic:
                first_lesson_next_topic = (
                    db.query(Lesson)
                    .filter(
                        Lesson.topic_id == next_topic.id, Lesson.is_published.is_(True)
                    )
                    .order_by(Lesson.order_index)
                    .first()
                )
                if first_lesson_next_topic:
                    next_l = LessonBrief.model_validate(first_lesson_next_topic)

    # If no previous lesson in same topic, check previous topic's last lesson
    if not prev_l:
        current_topic = current_lesson.topic
        if current_topic:
            prev_topic = (
                db.query(Topic)
                .filter(
                    Topic.module_id == current_topic.module_id,
                    Topic.order_index < current_topic.order_index,
                    Topic.is_published.is_(True),
                )
                .order_by(Topic.order_index.desc())
                .first()
            )
            if prev_topic:
                last_lesson_prev_topic = (
                    db.query(Lesson)
                    .filter(
                        Lesson.topic_id == prev_topic.id, Lesson.is_published.is_(True)
                    )
                    .order_by(Lesson.order_index.desc())
                    .first()
                )
                if last_lesson_prev_topic:
                    prev_l = LessonBrief.model_validate(last_lesson_prev_topic)

    return prev_l, next_l


def recalculate_topic_progress(
    db: Session, user_id: int, topic_id: int
) -> TopicProgress:
    """Recalculate topic progress and persist normalized summary."""
    total_lessons = (
        db.query(func.count(Lesson.id))
        .filter(Lesson.topic_id == topic_id, Lesson.is_published.is_(True))
        .scalar()
        or 0
    )

    completed_lessons = (
        db.query(func.count(LessonProgress.id))
        .join(Lesson, Lesson.id == LessonProgress.lesson_id)
        .filter(
            Lesson.topic_id == topic_id,
            LessonProgress.user_id == user_id,
            LessonProgress.status == ProgressStatus.COMPLETED,
        )
        .scalar()
        or 0
    )

    record = (
        db.query(TopicProgress)
        .filter(TopicProgress.user_id == user_id, TopicProgress.topic_id == topic_id)
        .first()
    )

    percentage = (
        round((completed_lessons / total_lessons * 100.0), 1)
        if total_lessons > 0
        else 0.0
    )
    status = ProgressStatus.NOT_STARTED
    if completed_lessons == total_lessons and total_lessons > 0:
        status = ProgressStatus.COMPLETED
    elif completed_lessons > 0:
        status = ProgressStatus.IN_PROGRESS

    now = datetime.now(timezone.utc)
    if not record:
        record = TopicProgress(
            user_id=user_id,
            topic_id=topic_id,
            status=status,
            completion_percentage=percentage,
            mastery_score=percentage,
            last_activity_at=now,
        )
        db.add(record)
    else:
        record.status = status
        record.completion_percentage = percentage
        record.mastery_score = percentage
        record.last_activity_at = now

    db.commit()
    db.refresh(record)
    return record


def mark_lesson_started(db: Session, user_id: int, lesson_id: int) -> LessonProgress:
    """Set lesson status to IN_PROGRESS and track access time."""
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise ValueError(f"Lesson ID {lesson_id} does not exist.")

    progress = (
        db.query(LessonProgress)
        .filter(
            LessonProgress.user_id == user_id, LessonProgress.lesson_id == lesson_id
        )
        .first()
    )

    now = datetime.now(timezone.utc)
    if not progress:
        progress = LessonProgress(
            user_id=user_id,
            lesson_id=lesson_id,
            status=ProgressStatus.IN_PROGRESS,
            started_at=now,
            last_accessed_at=now,
        )
        db.add(progress)
    else:
        progress.last_accessed_at = now
        if progress.status == ProgressStatus.NOT_STARTED:
            progress.status = ProgressStatus.IN_PROGRESS
            if not progress.started_at:
                progress.started_at = now

    db.commit()
    db.refresh(progress)
    recalculate_topic_progress(db, user_id, lesson.topic_id)
    return progress


def mark_lesson_completed(db: Session, user_id: int, lesson_id: int) -> LessonProgress:
    """Set lesson status to COMPLETED and update topic metrics."""
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise ValueError(f"Lesson ID {lesson_id} does not exist.")

    progress = (
        db.query(LessonProgress)
        .filter(
            LessonProgress.user_id == user_id, LessonProgress.lesson_id == lesson_id
        )
        .first()
    )

    now = datetime.now(timezone.utc)
    if not progress:
        progress = LessonProgress(
            user_id=user_id,
            lesson_id=lesson_id,
            status=ProgressStatus.COMPLETED,
            started_at=now,
            completed_at=now,
            last_accessed_at=now,
        )
        db.add(progress)
    else:
        progress.status = ProgressStatus.COMPLETED
        progress.completed_at = now
        progress.last_accessed_at = now
        if not progress.started_at:
            progress.started_at = now

    db.commit()
    db.refresh(progress)
    recalculate_topic_progress(db, user_id, lesson.topic_id)
    return progress


def toggle_lesson_bookmark(
    db: Session, user_id: int, lesson_id: int, bookmark: bool
) -> bool:
    """Add or remove bookmark for student."""
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise ValueError(f"Lesson ID {lesson_id} does not exist.")

    existing = (
        db.query(LessonBookmark)
        .filter(
            LessonBookmark.user_id == user_id, LessonBookmark.lesson_id == lesson_id
        )
        .first()
    )

    if bookmark:
        if not existing:
            new_bm = LessonBookmark(user_id=user_id, lesson_id=lesson_id)
            db.add(new_bm)
            db.commit()
        return True
    else:
        if existing:
            db.delete(existing)
            db.commit()
        return False


def get_user_bookmarks(db: Session, user_id: int) -> list[BookmarkItem]:
    """Retrieve all bookmarked lessons for user."""
    bookmarks = (
        db.query(LessonBookmark)
        .filter(LessonBookmark.user_id == user_id)
        .order_by(LessonBookmark.created_at.desc())
        .all()
    )

    results = []
    for bm in bookmarks:
        lesson = (
            db.query(Lesson)
            .options(selectinload(Lesson.topic).selectinload(Topic.module))
            .filter(Lesson.id == bm.lesson_id)
            .first()
        )
        if lesson and lesson.topic and lesson.topic.module:
            results.append(
                BookmarkItem(
                    id=bm.id,
                    lesson_id=lesson.id,
                    lesson_title=lesson.title,
                    lesson_slug=lesson.slug,
                    topic_title=lesson.topic.title,
                    topic_slug=lesson.topic.slug,
                    module_title=lesson.topic.module.title,
                    module_slug=lesson.topic.module.slug,
                    difficulty=lesson.difficulty,
                    estimated_minutes=lesson.estimated_minutes,
                    created_at=bm.created_at,
                )
            )
    return results


def get_topic_detail_extended(
    db: Session, user_id: int | None, topic: Topic
) -> TopicDetailExtended:
    """Build comprehensive Topic response including prerequisites, progress, and lessons."""
    module = topic.module
    course = module.course if module else None

    # Lessons with user progress
    lessons = (
        db.query(Lesson)
        .filter(Lesson.topic_id == topic.id, Lesson.is_published.is_(True))
        .order_by(Lesson.order_index)
        .all()
    )

    # User progress & bookmarks for lessons in this topic
    lesson_ids = [l.id for l in lessons]
    user_progress_map = {}
    if lesson_ids and user_id:
        records = (
            db.query(LessonProgress)
            .filter(
                LessonProgress.user_id == user_id,
                LessonProgress.lesson_id.in_(lesson_ids),
            )
            .all()
        )
        for r in records:
            user_progress_map[r.lesson_id] = r.status

    bookmarked_ids = set()
    if lesson_ids and user_id:
        bms = (
            db.query(LessonBookmark.lesson_id)
            .filter(
                LessonBookmark.user_id == user_id,
                LessonBookmark.lesson_id.in_(lesson_ids),
            )
            .all()
        )
        bookmarked_ids = {b[0] for b in bms}

    lessons_payload = []
    completed_count = 0
    for l in lessons:
        p_status = user_progress_map.get(l.id, ProgressStatus.NOT_STARTED)
        if p_status == ProgressStatus.COMPLETED:
            completed_count += 1
        lessons_payload.append(
            LessonBriefWithProgress(
                id=l.id,
                topic_id=l.topic_id,
                title=l.title,
                slug=l.slug,
                content_type=l.content_type,
                order_index=l.order_index,
                estimated_minutes=l.estimated_minutes,
                difficulty=l.difficulty,
                status=p_status,
                is_bookmarked=l.id in bookmarked_ids,
            )
        )

    # Prerequisites status
    prereq_payload = []
    for p in topic.prerequisites:
        # Check if user completed all lessons in prerequisite topic
        p_lessons_count = (
            db.query(func.count(Lesson.id))
            .filter(Lesson.topic_id == p.id, Lesson.is_published.is_(True))
            .scalar()
            or 0
        )
        p_completed = (
            db.query(func.count(LessonProgress.id))
            .join(Lesson, Lesson.id == LessonProgress.lesson_id)
            .filter(
                Lesson.topic_id == p.id,
                LessonProgress.user_id == user_id,
                LessonProgress.status == ProgressStatus.COMPLETED,
            )
            .scalar()
            or 0
        ) if user_id else 0
        is_completed = (p_completed == p_lessons_count) if p_lessons_count > 0 else True
        prereq_payload.append(
            PrerequisiteTopicBrief(
                id=p.id,
                title=p.title,
                slug=p.slug,
                difficulty=p.difficulty,
                is_completed=is_completed,
            )
        )

    # Next / previous topic
    prev_topic = (
        db.query(Topic)
        .filter(
            Topic.module_id == topic.module_id,
            Topic.order_index < topic.order_index,
            Topic.is_published.is_(True),
        )
        .order_by(Topic.order_index.desc())
        .first()
    )
    next_topic = (
        db.query(Topic)
        .filter(
            Topic.module_id == topic.module_id,
            Topic.order_index > topic.order_index,
            Topic.is_published.is_(True),
        )
        .order_by(Topic.order_index)
        .first()
    )

    # Parse learning objectives
    objectives_list: list[str] = []
    if topic.learning_objectives:
        try:
            parsed = json.loads(topic.learning_objectives)
            if isinstance(parsed, list):
                objectives_list = [str(item) for item in parsed]
        except (json.JSONDecodeError, TypeError, ValueError):
            objectives_list = [
                line.strip("- *").strip()
                for line in topic.learning_objectives.splitlines()
                if line.strip()
            ]

    # Related items (placeholders/connected)
    related_labs = [
        RelatedItemBrief(
            id=101,
            title=f"Lab: {topic.title} Sandbox",
            slug=f"lab-{topic.slug}",
            difficulty=topic.difficulty,
            status="coming_soon",
            description=f"Interactive container environment to practice {topic.title}.",
        )
    ]
    related_mock_tests = [
        RelatedItemBrief(
            id=201,
            title=f"Quiz: {topic.title} Diagnostic",
            slug=f"quiz-{topic.slug}",
            difficulty=topic.difficulty,
            status="coming_soon",
            description=f"Targeted examination testing your mastery of {topic.title}.",
        )
    ]

    total_lessons = len(lessons)
    percentage = (
        round((completed_count / total_lessons * 100.0), 1)
        if total_lessons > 0
        else 0.0
    )

    return TopicDetailExtended(
        id=topic.id,
        module_id=topic.module_id,
        module_title=module.title if module else "Curriculum Module",
        module_slug=module.slug if module else "module",
        course_id=course.id if course else 1,
        course_title=course.title if course else "Computer Networking & Cybersecurity",
        course_slug=course.slug if course else "networking-cybersecurity",
        title=topic.title,
        slug=topic.slug,
        description=topic.description,
        difficulty=topic.difficulty,
        order_index=topic.order_index,
        estimated_minutes=topic.estimated_minutes,
        learning_objectives=objectives_list,
        security_relevance=topic.security_relevance,
        prerequisites=prereq_payload,
        lessons=lessons_payload,
        lessons_count=total_lessons,
        completed_lessons_count=completed_count,
        completion_percentage=percentage,
        related_labs=related_labs,
        related_mock_tests=related_mock_tests,
        next_topic=TopicBrief.model_validate(next_topic) if next_topic else None,
        previous_topic=TopicBrief.model_validate(prev_topic) if prev_topic else None,
    )


def get_lesson_detail_extended(
    db: Session, user_id: int | None, lesson: Lesson
) -> LessonDetailExtended:
    """Build full lesson view with navigation, progress, and metadata."""
    topic = lesson.topic
    module = topic.module if topic else None
    course = module.course if module else None

    # User progress
    progress = None
    is_bookmarked = False
    if user_id is not None:
        progress = (
            db.query(LessonProgress)
            .filter(
                LessonProgress.user_id == user_id, LessonProgress.lesson_id == lesson.id
            )
            .first()
        )
        is_bookmarked = (
            db.query(LessonBookmark)
            .filter(
                LessonBookmark.user_id == user_id, LessonBookmark.lesson_id == lesson.id
            )
            .first()
            is not None
        )

    prev_lesson, next_lesson = get_next_and_previous_lesson(db, lesson)

    related_lab = RelatedItemBrief(
        id=101,
        title=f"Lab: {lesson.title} Hands-on",
        slug=f"lab-{lesson.slug}",
        difficulty=lesson.difficulty,
        status="coming_soon",
        description="Containerized Linux lab to apply concepts from this lesson.",
    )

    related_mock_test = RelatedItemBrief(
        id=201,
        title=f"Assessment: {topic.title if topic else 'Networking'} Test",
        slug=f"test-{lesson.slug}",
        difficulty=lesson.difficulty,
        status="coming_soon",
        description="Timed practice questions testing concepts from this lesson.",
    )

    return LessonDetailExtended(
        id=lesson.id,
        topic_id=lesson.topic_id,
        topic_title=topic.title if topic else "Networking Topic",
        topic_slug=topic.slug if topic else "topic",
        module_id=module.id if module else 1,
        module_title=module.title if module else "Curriculum Module",
        module_slug=module.slug if module else "module",
        course_id=course.id if course else 1,
        course_title=course.title if course else "Computer Networking & Cybersecurity",
        course_slug=course.slug if course else "networking-cybersecurity",
        title=lesson.title,
        slug=lesson.slug,
        description=lesson.description,
        content=lesson.content,
        content_type=lesson.content_type,
        order_index=lesson.order_index,
        estimated_minutes=lesson.estimated_minutes,
        difficulty=lesson.difficulty,
        status=progress.status if progress else ProgressStatus.NOT_STARTED,
        started_at=progress.started_at if progress else None,
        completed_at=progress.completed_at if progress else None,
        last_accessed_at=progress.last_accessed_at if progress else None,
        is_bookmarked=is_bookmarked,
        next_lesson=next_lesson,
        previous_lesson=prev_lesson,
        related_lab=related_lab,
        related_mock_test=related_mock_test,
    )


def get_learning_progress(db: Session, user_id: int) -> LearningProgressResponse:
    """Calculate overall, tiered, and continue-learning telemetry."""
    user = db.query(User).filter(User.id == user_id).first()
    current_level_str = user.current_level if user else "Cadet Defend-I"

    total_lessons = (
        db.query(func.count(Lesson.id)).filter(Lesson.is_published.is_(True)).scalar()
        or 0
    )

    user_completed_ids = {
        id_[0]
        for id_ in db.query(LessonProgress.lesson_id)
        .filter(
            LessonProgress.user_id == user_id,
            LessonProgress.status == ProgressStatus.COMPLETED,
        )
        .all()
    }
    user_in_progress_ids = {
        id_[0]
        for id_ in db.query(LessonProgress.lesson_id)
        .filter(
            LessonProgress.user_id == user_id,
            LessonProgress.status == ProgressStatus.IN_PROGRESS,
        )
        .all()
    }

    completed_count = len(user_completed_ids)
    in_progress_count = len(user_in_progress_ids)
    remaining_count = max(0, total_lessons - completed_count)
    overall_pct = (
        round((completed_count / total_lessons * 100.0), 1)
        if total_lessons > 0
        else 0.0
    )

    # Level progress calculations
    def calculate_level_stats(diff: DifficultyLevel) -> LevelProgress:
        tot = (
            db.query(func.count(Lesson.id))
            .filter(Lesson.difficulty == diff, Lesson.is_published.is_(True))
            .scalar()
            or 0
        )
        comp = (
            db.query(func.count(LessonProgress.id))
            .join(Lesson, Lesson.id == LessonProgress.lesson_id)
            .filter(
                Lesson.difficulty == diff,
                LessonProgress.user_id == user_id,
                LessonProgress.status == ProgressStatus.COMPLETED,
            )
            .scalar()
            or 0
        )
        pct = round((comp / tot * 100.0), 1) if tot > 0 else 0.0
        return LevelProgress(
            level=diff, total_lessons=tot, completed_lessons=comp, percentage=pct
        )

    beginner_progress = calculate_level_stats(DifficultyLevel.BEGINNER)
    intermediate_progress = calculate_level_stats(DifficultyLevel.INTERMEDIATE)
    advanced_progress = calculate_level_stats(DifficultyLevel.ADVANCED)

    # Continue learning resolution:
    # 1. Most recently accessed incomplete lesson
    continue_item = None
    recent_progress = (
        db.query(LessonProgress)
        .filter(
            LessonProgress.user_id == user_id,
            LessonProgress.status != ProgressStatus.COMPLETED,
        )
        .order_by(LessonProgress.last_accessed_at.desc())
        .first()
    )

    candidate_lesson = None
    if recent_progress:
        candidate_lesson = (
            db.query(Lesson).filter(Lesson.id == recent_progress.lesson_id).first()
        )

    # 2. Or the first incomplete published lesson
    if not candidate_lesson:
        candidate_lesson = (
            db.query(Lesson)
            .filter(
                Lesson.is_published.is_(True),
                Lesson.id.not_in(user_completed_ids) if user_completed_ids else True,
            )
            .order_by(Lesson.order_index)
            .first()
        )

    if candidate_lesson and candidate_lesson.topic and candidate_lesson.topic.module:
        topic_lessons_count = (
            db.query(func.count(Lesson.id))
            .filter(
                Lesson.topic_id == candidate_lesson.topic_id,
                Lesson.is_published.is_(True),
            )
            .scalar()
            or 1
        )
        continue_item = ContinueLearningItem(
            lesson_id=candidate_lesson.id,
            lesson_title=candidate_lesson.title,
            lesson_slug=candidate_lesson.slug,
            topic_title=candidate_lesson.topic.title,
            topic_slug=candidate_lesson.topic.slug,
            module_title=candidate_lesson.topic.module.title,
            module_slug=candidate_lesson.topic.module.slug,
            difficulty=candidate_lesson.difficulty,
            estimated_minutes=candidate_lesson.estimated_minutes,
            lesson_index=candidate_lesson.order_index + 1,
            total_topic_lessons=topic_lessons_count,
        )

    return LearningProgressResponse(
        overall_percentage=overall_pct,
        total_lessons=total_lessons,
        completed_lessons=completed_count,
        in_progress_lessons=in_progress_count,
        remaining_lessons=remaining_count,
        current_level=current_level_str,
        beginner_progress=beginner_progress,
        intermediate_progress=intermediate_progress,
        advanced_progress=advanced_progress,
        continue_learning=continue_item,
    )


def search_learning_content(
    db: Session,
    query: str,
    difficulty: DifficultyLevel | None = None,
    content_type: str | None = None,
) -> list[SearchResultItem]:
    """Search curriculum hierarchy across courses, modules, topics, and lessons."""
    clean_q = query.strip()
    if not clean_q:
        return []

    pattern = f"%{clean_q}%"
    results: list[SearchResultItem] = []

    # 1. Search Lessons
    lesson_q = (
        db.query(Lesson)
        .options(selectinload(Lesson.topic).selectinload(Topic.module))
        .filter(
            Lesson.is_published.is_(True),
            or_(
                Lesson.title.ilike(pattern),
                Lesson.description.ilike(pattern),
                Lesson.slug.ilike(pattern),
            ),
        )
    )
    if difficulty:
        lesson_q = lesson_q.filter(Lesson.difficulty == difficulty)

    for l in lesson_q.limit(15).all():
        topic_title = l.topic.title if l.topic else "Networking"
        results.append(
            SearchResultItem(
                type="lesson",
                id=l.id,
                title=l.title,
                slug=l.slug,
                description=l.description,
                difficulty=l.difficulty,
                parent_title=f"Topic: {topic_title}",
                url=f"/learning/lessons/{l.slug}",
            )
        )

    # 2. Search Topics
    topic_q = (
        db.query(Topic)
        .options(selectinload(Topic.module))
        .filter(
            Topic.is_published.is_(True),
            or_(
                Topic.title.ilike(pattern),
                Topic.description.ilike(pattern),
                Topic.slug.ilike(pattern),
            ),
        )
    )
    if difficulty:
        topic_q = topic_q.filter(Topic.difficulty == difficulty)

    for t in topic_q.limit(10).all():
        mod_title = t.module.title if t.module else "Module"
        results.append(
            SearchResultItem(
                type="topic",
                id=t.id,
                title=t.title,
                slug=t.slug,
                description=t.description,
                difficulty=t.difficulty,
                parent_title=f"Module: {mod_title}",
                url=f"/learning/topics/{t.slug}",
            )
        )

    # 3. Search Modules
    module_q = db.query(Module).filter(
        Module.is_published.is_(True),
        or_(
            Module.title.ilike(pattern),
            Module.description.ilike(pattern),
            Module.slug.ilike(pattern),
        ),
    )
    if difficulty:
        module_q = module_q.filter(Module.difficulty == difficulty)

    for m in module_q.limit(5).all():
        results.append(
            SearchResultItem(
                type="module",
                id=m.id,
                title=m.title,
                slug=m.slug,
                description=m.description,
                difficulty=m.difficulty,
                parent_title="Course Curriculum",
                url="/learning",
            )
        )

    return results
