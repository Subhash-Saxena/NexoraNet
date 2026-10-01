"""Admin Content Service - Platform dashboard, content operations, validation, versioning, and audit logging."""

from datetime import datetime, timezone
from typing import Any

from app.models.analytics import AdminAuditLog, ContentVersion
from app.models.challenge import Challenge, ChallengeStage, ChallengeTrack
from app.models.curriculum import Course, Lesson, Module, Topic
from app.models.enums import AdminAuditAction, ContentStatus, QuestionStatus, UserRole
from app.models.lab import Lab
from app.models.mock_test import MockTest
from app.models.question import Question
from app.models.user import User
from sqlalchemy import func
from sqlalchemy.orm import Session


class AdminContentService:
    """Provides authorized administrative inspection, validation, publication, and audit ledger."""

    @staticmethod
    def get_dashboard_metrics(db: Session) -> dict[str, Any]:
        """Aggregate platform-wide content health and learner metrics."""
        total_users = db.query(func.count(User.id)).scalar() or 0
        students_count = db.query(func.count(User.id)).filter(User.role == UserRole.STUDENT).scalar() or 0

        # Content counts
        courses_count = db.query(func.count(Course.id)).scalar() or 0
        modules_count = db.query(func.count(Module.id)).scalar() or 0
        topics_count = db.query(func.count(Topic.id)).scalar() or 0
        lessons_count = db.query(func.count(Lesson.id)).scalar() or 0
        labs_count = db.query(func.count(Lab.id)).scalar() or 0
        questions_count = db.query(func.count(Question.id)).scalar() or 0
        tests_count = db.query(func.count(MockTest.id)).scalar() or 0
        challenges_count = db.query(func.count(Challenge.id)).scalar() or 0
        tracks_count = db.query(func.count(ChallengeTrack.id)).scalar() or 0

        # Publication status breakdown for questions & challenges
        published_questions = (
            db.query(func.count(Question.id))
            .filter(Question.status == QuestionStatus.PUBLISHED)
            .scalar()
            or 0
        )
        draft_questions = (
            db.query(func.count(Question.id))
            .filter(Question.status == QuestionStatus.DRAFT)
            .scalar()
            or 0
        )
        archived_questions = (
            db.query(func.count(Question.id))
            .filter(Question.status == QuestionStatus.ARCHIVED)
            .scalar()
            or 0
        )

        # Recent audit logs
        recent_logs = (
            db.query(AdminAuditLog)
            .order_by(AdminAuditLog.created_at.desc())
            .limit(8)
            .all()
        )

        return {
            "total_users": total_users,
            "active_learners": students_count,
            "catalog_counts": {
                "courses": courses_count,
                "modules": modules_count,
                "topics": topics_count,
                "lessons": lessons_count,
                "labs": labs_count,
                "questions": questions_count,
                "mock_tests": tests_count,
                "challenges": challenges_count,
                "challenge_tracks": tracks_count,
            },
            "publication_status": {
                "published_questions": published_questions,
                "draft_questions": draft_questions,
                "archived_questions": archived_questions,
                "published_challenges": challenges_count,
            },
            "recent_audit_logs": [
                {
                    "id": l.id,
                    "actor_username": l.actor_username,
                    "action": l.action.value if hasattr(l.action, "value") else str(l.action),
                    "target_type": l.target_type,
                    "target_id": l.target_id,
                    "timestamp": l.created_at.isoformat(),
                }
                for l in recent_logs
            ],
        }

    @staticmethod
    def list_content(
        db: Session,
        content_type: str | None = None,
        status: str | None = None,
        search: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """List and search content items across multiple educational modules."""
        items = []

        # 1. Questions
        if not content_type or content_type.upper() == "QUESTION":
            q_query = db.query(Question)
            if status:
                q_query = q_query.filter(Question.status == status.upper())
            if search:
                q_query = q_query.filter(Question.question_text.ilike(f"%{search}%"))
            questions = q_query.limit(limit).offset(offset).all()
            for q in questions:
                items.append({
                    "id": str(q.id),
                    "content_type": "QUESTION",
                    "code_or_slug": q.code or f"Q-{q.id}",
                    "title": q.question_text[:80] + ("..." if len(q.question_text) > 80 else ""),
                    "category": q.question_type.value if hasattr(q.question_type, "value") else str(q.question_type),
                    "difficulty": q.difficulty.value if hasattr(q.difficulty, "value") else str(q.difficulty),
                    "status": q.status.value if hasattr(q.status, "value") else str(q.status),
                    "updated_at": q.updated_at.isoformat() if q.updated_at else q.created_at.isoformat(),
                })

        # 2. Challenges
        if not content_type or content_type.upper() == "CHALLENGE":
            c_query = db.query(Challenge)
            if search:
                c_query = c_query.filter(Challenge.title.ilike(f"%{search}%"))
            challenges = c_query.limit(limit).all()
            for c in challenges:
                items.append({
                    "id": str(c.id),
                    "content_type": "CHALLENGE",
                    "code_or_slug": c.challenge_id,
                    "title": c.title,
                    "category": c.category.value if hasattr(c.category, "value") else str(c.category),
                    "difficulty": c.difficulty.value if hasattr(c.difficulty, "value") else str(c.difficulty),
                    "status": "PUBLISHED",
                    "updated_at": c.updated_at.isoformat() if c.updated_at else c.created_at.isoformat(),
                })

        # 3. Labs
        if not content_type or content_type.upper() == "LAB":
            l_query = db.query(Lab)
            if search:
                l_query = l_query.filter(Lab.title.ilike(f"%{search}%"))
            labs = l_query.limit(limit).all()
            for l in labs:
                items.append({
                    "id": str(l.id),
                    "content_type": "LAB",
                    "code_or_slug": l.slug,
                    "title": l.title,
                    "category": l.environment_type.value if hasattr(l.environment_type, "value") else str(l.environment_type),
                    "difficulty": l.difficulty.value if hasattr(l.difficulty, "value") else str(l.difficulty),
                    "status": l.status.value if hasattr(l.status, "value") else str(l.status),
                    "updated_at": l.updated_at.isoformat() if l.updated_at else l.created_at.isoformat(),
                })

        # 4. Lessons
        if not content_type or content_type.upper() == "LESSON":
            les_query = db.query(Lesson)
            if search:
                les_query = les_query.filter(Lesson.title.ilike(f"%{search}%"))
            lessons = les_query.limit(limit).all()
            for les in lessons:
                items.append({
                    "id": str(les.id),
                    "content_type": "LESSON",
                    "code_or_slug": les.slug,
                    "title": les.title,
                    "category": "CURRICULUM",
                    "difficulty": les.difficulty.value if hasattr(les.difficulty, "value") else str(les.difficulty),
                    "status": "PUBLISHED",
                    "updated_at": les.updated_at.isoformat() if les.updated_at else les.created_at.isoformat(),
                })

        return items

    @staticmethod
    def validate_content(db: Session, content_type: str, content_id: str) -> list[str]:
        """Validate content item integrity before publication; returns list of blocking error messages."""
        errors = []
        c_type = content_type.upper()

        if c_type == "QUESTION":
            q = db.query(Question).filter((Question.id == content_id) | (Question.code == content_id)).first()
            if not q:
                return ["Question does not exist in database."]
            if not q.question_text or len(q.question_text.strip()) < 10:
                errors.append("Question text must be at least 10 characters long.")
            if not q.options:
                errors.append("Question has no answer choices defined.")
            else:
                correct_count = sum(1 for opt in q.options if opt.is_correct)
                if correct_count == 0:
                    errors.append("Question has no marked correct answer.")
                elif q.question_type.value == "SINGLE_CHOICE" and correct_count > 1:
                    errors.append("Single-choice question cannot have multiple correct answers.")

        elif c_type == "CHALLENGE":
            c = db.query(Challenge).filter((Challenge.id == content_id) | (Challenge.challenge_id == content_id)).first()
            if not c:
                return ["Challenge does not exist in database."]
            if not c.title or len(c.title.strip()) < 5:
                errors.append("Challenge title is too short.")
            stages = db.query(ChallengeStage).filter(ChallengeStage.challenge_id == c.id).all()
            if not stages:
                errors.append("Challenge must have at least one stage.")
            for st in stages:
                if not st.flag_hash or not st.flag_salt:
                    errors.append(f"Stage #{st.stage_order} is missing cryptographic flag hash or salt.")

        elif c_type == "LAB":
            lab = db.query(Lab).filter((Lab.id == content_id) | (Lab.slug == content_id)).first()
            if not lab:
                return ["Lab does not exist in database."]
            if not lab.steps:
                errors.append("Lab contains no step blueprints.")

        return errors

    @staticmethod
    def publish_content(db: Session, actor: User, content_type: str, content_id: str) -> dict[str, Any]:
        """Validate and publish content item, incrementing version and writing to audit ledger."""
        errors = AdminContentService.validate_content(db, content_type, content_id)
        if errors:
            raise ValueError(f"Content validation failed: {'; '.join(errors)}")

        now = datetime.now(timezone.utc)
        c_type = content_type.upper()

        if c_type == "QUESTION":
            q = db.query(Question).filter((Question.id == content_id) | (Question.code == content_id)).first()
            if not q:
                raise ValueError("Question not found.")
            q.status = QuestionStatus.PUBLISHED
            q_id_str = str(q.id)
        elif c_type == "LAB":
            lab = db.query(Lab).filter((Lab.id == content_id) | (Lab.slug == content_id)).first()
            if not lab:
                raise ValueError("Lab not found.")
            lab.status = "PUBLISHED"
            q_id_str = str(lab.id)
        else:
            q_id_str = str(content_id)

        # Versioning
        version = (
            db.query(ContentVersion)
            .filter(
                ContentVersion.content_type == c_type,
                ContentVersion.content_id == q_id_str,
            )
            .order_by(ContentVersion.version_number.desc())
            .first()
        )
        new_v_num = (version.version_number + 1) if version else 1
        new_version = ContentVersion(
            content_type=c_type,
            content_id=q_id_str,
            version_number=new_v_num,
            status=ContentStatus.PUBLISHED,
            change_summary="Published by administrator.",
            published_by=actor.username,
            published_at=now,
        )
        db.add(new_version)

        # Audit Log
        AdminContentService.log_audit_action(
            db=db,
            actor=actor,
            action=AdminAuditAction.CONTENT_PUBLISHED,
            target_type=c_type,
            target_id=q_id_str,
            metadata={"version": new_v_num, "status": "PUBLISHED"},
        )

        db.commit()
        return {
            "content_type": c_type,
            "content_id": q_id_str,
            "status": "PUBLISHED",
            "version": new_v_num,
            "published_at": now.isoformat(),
        }

    @staticmethod
    def unpublish_content(db: Session, actor: User, content_type: str, content_id: str) -> dict[str, Any]:
        """Unpublish content item to draft/unpublished state."""
        now = datetime.now(timezone.utc)
        c_type = content_type.upper()

        if c_type == "QUESTION":
            q = db.query(Question).filter((Question.id == content_id) | (Question.code == content_id)).first()
            if not q:
                raise ValueError("Question not found.")
            q.status = QuestionStatus.DRAFT
            q_id_str = str(q.id)
        else:
            q_id_str = str(content_id)

        AdminContentService.log_audit_action(
            db=db,
            actor=actor,
            action=AdminAuditAction.CONTENT_UNPUBLISHED,
            target_type=c_type,
            target_id=q_id_str,
            metadata={"status": "UNPUBLISHED"},
        )

        db.commit()
        return {
            "content_type": c_type,
            "content_id": q_id_str,
            "status": "UNPUBLISHED",
            "updated_at": now.isoformat(),
        }

    @staticmethod
    def archive_content(db: Session, actor: User, content_type: str, content_id: str) -> dict[str, Any]:
        """Archive content item so students no longer encounter it."""
        now = datetime.now(timezone.utc)
        c_type = content_type.upper()

        if c_type == "QUESTION":
            q = db.query(Question).filter((Question.id == content_id) | (Question.code == content_id)).first()
            if not q:
                raise ValueError("Question not found.")
            q.status = QuestionStatus.ARCHIVED
            q_id_str = str(q.id)
        else:
            q_id_str = str(content_id)

        AdminContentService.log_audit_action(
            db=db,
            actor=actor,
            action=AdminAuditAction.CONTENT_ARCHIVED,
            target_type=c_type,
            target_id=q_id_str,
            metadata={"status": "ARCHIVED"},
        )

        db.commit()
        return {
            "content_type": c_type,
            "content_id": q_id_str,
            "status": "ARCHIVED",
            "updated_at": now.isoformat(),
        }

    @staticmethod
    def log_audit_action(
        db: Session,
        actor: User,
        action: AdminAuditAction,
        target_type: str,
        target_id: str,
        metadata: dict[str, Any] | None = None,
    ) -> AdminAuditLog:
        """Append an entry to the immutable administrative audit ledger."""
        now = datetime.now(timezone.utc)
        # Ensure passwords, tokens, flags, or secrets are NEVER in metadata
        safe_meta = {
            k: v
            for k, v in (metadata or {}).items()
            if k not in ("password", "password_hash", "token", "flag", "salt", "secret")
        }

        log = AdminAuditLog(
            actor_id=actor.id,
            actor_username=actor.username,
            action=action,
            target_type=target_type,
            target_id=target_id,
            metadata_json=safe_meta,
            created_at=now,
        )
        db.add(log)
        return log

    @staticmethod
    def list_audit_logs(
        db: Session,
        action: str | None = None,
        target_type: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """Retrieve audit logs with optional filtering."""
        query = db.query(AdminAuditLog)
        if action:
            query = query.filter(AdminAuditLog.action == action.upper())
        if target_type:
            query = query.filter(AdminAuditLog.target_type == target_type.upper())
        logs = query.order_by(AdminAuditLog.created_at.desc()).limit(limit).offset(offset).all()

        return [
            {
                "id": l.id,
                "actor_id": l.actor_id,
                "actor_username": l.actor_username,
                "action": l.action.value if hasattr(l.action, "value") else str(l.action),
                "target_type": l.target_type,
                "target_id": l.target_id,
                "metadata": l.metadata_json,
                "created_at": l.created_at.isoformat(),
            }
            for l in logs
        ]
