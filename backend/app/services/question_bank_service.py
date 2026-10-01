
from sqlalchemy import func
from sqlalchemy.orm import Session, selectinload

from app.models.curriculum import Topic
from app.models.enums import (
    CognitiveLevel,
    DifficultyLevel,
    QuestionStatus,
    QuestionType,
)
from app.models.question import Question, QuestionOption, QuestionTag
from app.schemas.question import (
    AdminQuestionCreate,
    AdminQuestionUpdate,
    QuestionBankStatistics,
)
from app.services.question_validator import QuestionValidator


class QuestionBankService:
    """Service layer for question bank statistics, authoring, and advanced search."""

    @staticmethod
    def get_statistics(db: Session) -> QuestionBankStatistics:
        """
        Aggregate total questions, difficulty distributions, topic distributions,
        question types, cognitive levels, and status breakdown.
        """
        total = db.query(func.count(Question.id)).scalar() or 0

        # By difficulty
        diff_rows = (
            db.query(Question.difficulty, func.count(Question.id))
            .group_by(Question.difficulty)
            .all()
        )
        by_difficulty = {row[0].value if hasattr(row[0], "value") else str(row[0]): row[1] for row in diff_rows}

        # By topic (using topic title)
        topic_rows = (
            db.query(Topic.title, func.count(Question.id))
            .join(Question, Question.topic_id == Topic.id)
            .group_by(Topic.title)
            .all()
        )
        by_topic = {row[0]: row[1] for row in topic_rows}

        # By question type
        type_rows = (
            db.query(Question.question_type, func.count(Question.id))
            .group_by(Question.question_type)
            .all()
        )
        by_question_type = {row[0].value if hasattr(row[0], "value") else str(row[0]): row[1] for row in type_rows}

        # By cognitive level
        cog_rows = (
            db.query(Question.cognitive_level, func.count(Question.id))
            .group_by(Question.cognitive_level)
            .all()
        )
        by_cognitive_level = {row[0].value if hasattr(row[0], "value") else str(row[0]): row[1] for row in cog_rows}

        # By status
        status_rows = (
            db.query(Question.status, func.count(Question.id))
            .group_by(Question.status)
            .all()
        )
        by_status = {row[0].value if hasattr(row[0], "value") else str(row[0]): row[1] for row in status_rows}

        return QuestionBankStatistics(
            total_questions=total,
            by_difficulty=by_difficulty,
            by_topic=by_topic,
            by_question_type=by_question_type,
            by_cognitive_level=by_cognitive_level,
            by_status=by_status,
        )

    @staticmethod
    def search_questions(
        db: Session,
        topic_id: int | None = None,
        difficulty: str | None = None,
        question_type: str | None = None,
        cognitive_level: str | None = None,
        tag: str | None = None,
        search_query: str | None = None,
        status: QuestionStatus | None = QuestionStatus.PUBLISHED,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Question]:
        """
        Filtered query across questions.
        If status is provided (defaults to PUBLISHED for student safety), filters by status.
        """
        query = (
            db.query(Question)
            .options(
                selectinload(Question.options),
                selectinload(Question.tags),
            )
        )

        if status is not None:
            query = query.filter(Question.status == status)

        if topic_id is not None:
            query = query.filter(Question.topic_id == topic_id)

        if difficulty:
            try:
                diff_enum = DifficultyLevel(difficulty.upper())
                query = query.filter(Question.difficulty == diff_enum)
            except ValueError:
                return []

        if question_type:
            try:
                qt_enum = QuestionType(question_type.upper())
                query = query.filter(Question.question_type == qt_enum)
            except ValueError:
                return []

        if cognitive_level:
            try:
                cog_enum = CognitiveLevel(cognitive_level.upper())
                query = query.filter(Question.cognitive_level == cog_enum)
            except ValueError:
                return []

        if tag:
            query = query.join(Question.tags).filter(QuestionTag.slug == tag.lower())

        if search_query and search_query.strip():
            clean_term = f"%{search_query.strip().lower()}%"
            query = query.filter(func.lower(Question.question_text).like(clean_term))

        return query.order_by(Question.id).offset(offset).limit(limit).all()

    @staticmethod
    def create_admin_question(db: Session, payload: AdminQuestionCreate) -> Question:
        """Create a question with full options and tags (Admin endpoint)."""
        # Validate payload dictionary
        raw_dict = payload.model_dump()
        errs = QuestionValidator.validate_question_dict(raw_dict)
        if errs:
            raise ValueError("; ".join(errs))

        # Check unique code
        if payload.code:
            existing = db.query(Question).filter(Question.code == payload.code).first()
            if existing:
                raise ValueError(f"Question with code '{payload.code}' already exists.")

        # Resolve tags
        resolved_tags: list[QuestionTag] = []
        for tag_name in payload.tags:
            slug = tag_name.strip().lower()
            tag = db.query(QuestionTag).filter(QuestionTag.slug == slug).first()
            if not tag:
                tag = QuestionTag(name=tag_name, slug=slug)
                db.add(tag)
                db.flush()
            resolved_tags.append(tag)

        new_q = Question(
            code=payload.code,
            question_text=payload.question_text,
            question_type=payload.question_type,
            topic_id=payload.topic_id,
            difficulty=payload.difficulty,
            cognitive_level=payload.cognitive_level,
            explanation=payload.explanation,
            learning_objective=payload.learning_objective,
            points=payload.points,
            estimated_seconds=payload.estimated_seconds,
            status=payload.status,
            tags=resolved_tags,
        )
        db.add(new_q)
        db.flush()

        for idx, opt in enumerate(payload.options):
            new_opt = QuestionOption(
                question_id=new_q.id,
                option_text=opt.option_text,
                is_correct=opt.is_correct,
                order_index=opt.order_index or idx,
                explanation=opt.explanation,
            )
            db.add(new_opt)

        db.commit()
        db.refresh(new_q)
        return new_q

    @staticmethod
    def update_admin_question(db: Session, question_id: int, payload: AdminQuestionUpdate) -> Question:
        """Update an existing question (Admin endpoint)."""
        q = (
            db.query(Question)
            .options(selectinload(Question.options), selectinload(Question.tags))
            .filter(Question.id == question_id)
            .first()
        )
        if not q:
            raise ValueError(f"Question ID {question_id} not found.")

        if payload.code is not None and payload.code != q.code:
            existing = db.query(Question).filter(Question.code == payload.code).first()
            if existing:
                raise ValueError(f"Question with code '{payload.code}' already exists.")
            q.code = payload.code

        if payload.question_text is not None:
            QuestionValidator.sanitize_content(payload.question_text)
            q.question_text = payload.question_text
        if payload.question_type is not None:
            q.question_type = payload.question_type
        if payload.topic_id is not None:
            q.topic_id = payload.topic_id
        if payload.difficulty is not None:
            q.difficulty = payload.difficulty
        if payload.cognitive_level is not None:
            q.cognitive_level = payload.cognitive_level
        if payload.explanation is not None:
            QuestionValidator.sanitize_content(payload.explanation)
            q.explanation = payload.explanation
        if payload.learning_objective is not None:
            q.learning_objective = payload.learning_objective
        if payload.points is not None:
            q.points = payload.points
        if payload.estimated_seconds is not None:
            q.estimated_seconds = payload.estimated_seconds
        if payload.status is not None:
            q.status = payload.status

        if payload.options is not None:
            # Sync options
            existing_options = sorted(q.options, key=lambda o: o.order_index)
            for idx, opt_data in enumerate(payload.options):
                if idx < len(existing_options):
                    existing_options[idx].option_text = opt_data.option_text
                    existing_options[idx].is_correct = opt_data.is_correct
                    existing_options[idx].order_index = opt_data.order_index
                    existing_options[idx].explanation = opt_data.explanation
                else:
                    new_opt = QuestionOption(
                        question_id=q.id,
                        option_text=opt_data.option_text,
                        is_correct=opt_data.is_correct,
                        order_index=opt_data.order_index,
                        explanation=opt_data.explanation,
                    )
                    db.add(new_opt)
            if len(payload.options) < len(existing_options):
                for extra in existing_options[len(payload.options):]:
                    db.delete(extra)

        db.commit()
        db.refresh(q)
        return q
