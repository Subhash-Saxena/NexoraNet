import json
import logging
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session, selectinload

from app.models.curriculum import Topic
from app.models.enums import (
    CognitiveLevel,
    DifficultyLevel,
    QuestionStatus,
    QuestionType,
)
from app.models.question import Question, QuestionOption, QuestionTag
from app.services.question_validator import QuestionValidator

logger = logging.getLogger(__name__)


class QuestionImporter:
    """
    Ingests and safely upserts question bank files (JSON/JSONL).
    Guarantees idempotency via stable unique question codes.
    """

    @classmethod
    def load_questions_from_directory(
        cls, base_dir: Path
    ) -> list[tuple[Path, list[dict[str, Any]]]]:
        """
        Recursively scan directory for JSON/JSONL files and return parsed question lists.
        """
        results: list[tuple[Path, list[dict[str, Any]]]] = []
        if not base_dir.exists():
            return results

        # Sort files for deterministic loading
        json_files = sorted(list(base_dir.rglob("*.json")) + list(base_dir.rglob("*.jsonl")))
        for file_path in json_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    if not content:
                        continue
                    if file_path.suffix == ".jsonl":
                        q_list = [json.loads(line) for line in content.splitlines() if line.strip()]
                    else:
                        parsed = json.loads(content)
                        q_list = parsed if isinstance(parsed, list) else [parsed]
                    results.append((file_path, q_list))
            except Exception as e:
                logger.error(f"Failed to read question file {file_path}: {e}")
                raise ValueError(f"Error reading file {file_path}: {e}") from e

        return results

    @classmethod
    def import_all(
        cls,
        db: Session,
        base_dir: Path,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        """
        Validate, duplicate-check, and safely upsert all questions found in base_dir.
        """
        file_entries = cls.load_questions_from_directory(base_dir)

        # 1. Gather all questions into flat list
        all_questions: list[dict[str, Any]] = []
        file_map: list[tuple[Path, dict[str, Any]]] = []
        for file_path, q_list in file_entries:
            for q in q_list:
                all_questions.append(q)
                file_map.append((file_path, q))

        # 2. Check for duplicate codes and identical normalized texts across all files
        duplicate_report = QuestionValidator.check_duplicate_questions(all_questions)

        # 3. Resolve topics cache from database
        topics = db.query(Topic).all()
        topic_slug_map = {t.slug: t.id for t in topics}
        topic_id_set = {t.id for t in topics}

        # 4. Validate each question
        validation_errors: list[dict[str, Any]] = []
        for file_path, q in file_map:
            errs = QuestionValidator.validate_question_dict(
                q,
                valid_topic_slugs=set(topic_slug_map.keys()),
                valid_topic_ids=topic_id_set,
            )
            if errs:
                validation_errors.append({
                    "file": str(file_path.name),
                    "code": q.get("code", "UNKNOWN"),
                    "errors": errs,
                })

        if validation_errors:
            return {
                "success": False,
                "total_files": len(file_entries),
                "total_questions": len(all_questions),
                "created_count": 0,
                "updated_count": 0,
                "duplicates_detected": duplicate_report,
                "validation_errors": validation_errors,
            }

        # 5. Compute stats
        diff_stats = {"BEGINNER": 0, "INTERMEDIATE": 0, "ADVANCED": 0}
        cog_stats = {"REMEMBER": 0, "UNDERSTAND": 0, "APPLY": 0, "ANALYZE": 0}
        type_stats: dict[str, int] = {}
        status_stats: dict[str, int] = {}

        for _, q_data in file_map:
            diff_val = str(q_data.get("difficulty", "BEGINNER")).upper()
            cog_val = str(q_data.get("cognitive_level", "UNDERSTAND")).upper()
            type_val = str(q_data.get("question_type", "SINGLE_CHOICE")).upper()
            stat_val = str(q_data.get("status", "PUBLISHED")).upper()

            diff_stats[diff_val] = diff_stats.get(diff_val, 0) + 1
            cog_stats[cog_val] = cog_stats.get(cog_val, 0) + 1
            type_stats[type_val] = type_stats.get(type_val, 0) + 1
            status_stats[stat_val] = status_stats.get(stat_val, 0) + 1

        # 6. Stop if dry_run
        if dry_run:
            return {
                "success": True,
                "dry_run": True,
                "total_files": len(file_entries),
                "total_questions": len(all_questions),
                "created_count": 0,
                "updated_count": 0,
                "duplicates_detected": duplicate_report,
                "validation_errors": [],
                "by_difficulty": diff_stats,
                "by_cognitive_level": cog_stats,
                "by_question_type": type_stats,
                "by_status": status_stats,
                "difficulty_breakdown": diff_stats,
                "cognitive_breakdown": cog_stats,
                "type_breakdown": type_stats,
                "status_breakdown": status_stats,
            }

        # 7. Upsert tags cache
        tag_cache: dict[str, QuestionTag] = {tag.slug: tag for tag in db.query(QuestionTag).all()}

        # 8. Safe upsert questions
        created_count = 0
        updated_count = 0

        for _, q_data in file_map:
            code = q_data.get("code")
            topic_id = q_data.get("topic_id")
            if topic_id is None and "topic_slug" in q_data:
                topic_id = topic_slug_map[q_data["topic_slug"]]

            difficulty = DifficultyLevel(str(q_data["difficulty"]).upper())
            cognitive_level = CognitiveLevel(str(q_data.get("cognitive_level", "UNDERSTAND")).upper())
            question_type = QuestionType(str(q_data.get("question_type", "SINGLE_CHOICE")).upper())
            status = QuestionStatus(str(q_data.get("status", "PUBLISHED")).upper())

            # Resolve tags
            resolved_tags: list[QuestionTag] = []
            for tag_slug in q_data.get("tags", []):
                cleaned_slug = tag_slug.strip().lower()
                if cleaned_slug not in tag_cache:
                    new_tag = QuestionTag(name=cleaned_slug.replace("-", " ").title(), slug=cleaned_slug)
                    db.add(new_tag)
                    db.flush()
                    tag_cache[cleaned_slug] = new_tag
                resolved_tags.append(tag_cache[cleaned_slug])

            # Query existing question by code
            existing_q = None
            if code:
                existing_q = (
                    db.query(Question)
                    .options(selectinload(Question.options), selectinload(Question.tags))
                    .filter(Question.code == code)
                    .first()
                )

            if existing_q:
                # Update attributes
                existing_q.question_text = q_data["question_text"]
                existing_q.question_type = question_type
                existing_q.topic_id = topic_id
                existing_q.difficulty = difficulty
                existing_q.cognitive_level = cognitive_level
                existing_q.explanation = q_data.get("explanation", "")
                existing_q.learning_objective = q_data.get("learning_objective")
                existing_q.points = q_data.get("points", 1)
                existing_q.estimated_seconds = q_data.get("estimated_seconds", 60)
                existing_q.status = status
                existing_q.tags = resolved_tags

                # Safe option in-place sync
                raw_options = q_data.get("options", [])
                existing_options = sorted(existing_q.options, key=lambda o: o.order_index)
                for idx, opt_data in enumerate(raw_options):
                    if idx < len(existing_options):
                        # Update in-place
                        existing_options[idx].option_text = opt_data["option_text"]
                        existing_options[idx].is_correct = opt_data.get("is_correct", False)
                        existing_options[idx].order_index = opt_data.get("order_index", idx)
                        existing_options[idx].explanation = opt_data.get("explanation")
                    else:
                        # Append new option
                        new_opt = QuestionOption(
                            question_id=existing_q.id,
                            option_text=opt_data["option_text"],
                            is_correct=opt_data.get("is_correct", False),
                            order_index=opt_data.get("order_index", idx),
                            explanation=opt_data.get("explanation"),
                        )
                        db.add(new_opt)

                # If raw_options had fewer options than existing, delete extra unreferenced options
                if len(raw_options) < len(existing_options):
                    for extra_opt in existing_options[len(raw_options):]:
                        db.delete(extra_opt)

                updated_count += 1
            else:
                # Create brand new question
                new_q = Question(
                    code=code,
                    question_text=q_data["question_text"],
                    question_type=question_type,
                    topic_id=topic_id,
                    difficulty=difficulty,
                    cognitive_level=cognitive_level,
                    explanation=q_data.get("explanation", ""),
                    learning_objective=q_data.get("learning_objective"),
                    points=q_data.get("points", 1),
                    estimated_seconds=q_data.get("estimated_seconds", 60),
                    status=status,
                    tags=resolved_tags,
                )
                db.add(new_q)
                db.flush()

                for idx, opt_data in enumerate(q_data.get("options", [])):
                    new_opt = QuestionOption(
                        question_id=new_q.id,
                        option_text=opt_data["option_text"],
                        is_correct=opt_data.get("is_correct", False),
                        order_index=opt_data.get("order_index", idx),
                        explanation=opt_data.get("explanation"),
                    )
                    db.add(new_opt)

                created_count += 1

        db.commit()

        return {
            "success": True,
            "dry_run": False,
            "total_files": len(file_entries),
            "total_questions": len(all_questions),
            "created_count": created_count,
            "updated_count": updated_count,
            "by_difficulty": diff_stats,
            "by_cognitive_level": cog_stats,
            "by_question_type": type_stats,
            "by_status": status_stats,
            "duplicates_detected": duplicate_report,
            "validation_errors": [],
        }
