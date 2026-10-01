"""Challenge catalog, track, and metrics service for Step 19 CTF Engine.

Enforces zero-knowledge student safety: flag hashes and salts are never leaked
in API outputs.
"""

from typing import Any

from app.models.challenge import (
    Challenge,
    ChallengeAttempt,
    ChallengeTrack,
    ChallengeTrackItem,
)
from app.models.enums import (
    ChallengeAttemptStatus,
    ChallengeCategory,
    ChallengeDifficulty,
)
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload


class ChallengeService:
    """Read-side service for challenges, tracks, and performance metrics."""

    @staticmethod
    def list_challenges(
        db: Session,
        category: ChallengeCategory | None = None,
        difficulty: ChallengeDifficulty | None = None,
        search: str | None = None,
        user_id: int | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """List active challenges with optional filtering and user completion flag."""
        query = select(Challenge).where(Challenge.is_active == True)

        if category:
            query = query.where(Challenge.category == category)
        if difficulty:
            query = query.where(Challenge.difficulty == difficulty)
        if search:
            search_clean = f"%{search.strip().lower()}%"
            query = query.where(
                or_(
                    func.lower(Challenge.title).like(search_clean),
                    func.lower(Challenge.challenge_id).like(search_clean),
                    func.lower(Challenge.description).like(search_clean),
                )
            )

        query = query.order_by(Challenge.points.asc(), Challenge.id.asc()).offset(skip).limit(limit)
        challenges = db.scalars(query).all()

        # Check user solved status if user_id provided
        solved_ids = set()
        in_progress_ids = set()
        if user_id:
            user_attempts = db.scalars(
                select(ChallengeAttempt).where(ChallengeAttempt.user_id == user_id)
            ).all()
            for att in user_attempts:
                if att.solved:
                    solved_ids.add(att.challenge_id)
                elif att.status == ChallengeAttemptStatus.IN_PROGRESS:
                    in_progress_ids.add(att.challenge_id)

        result = []
        for ch in challenges:
            status = "NOT_STARTED"
            if ch.id in solved_ids:
                status = "SOLVED"
            elif ch.id in in_progress_ids:
                status = "IN_PROGRESS"

            result.append({
                "id": ch.id,
                "challenge_id": ch.challenge_id,
                "title": ch.title,
                "category": ch.category,
                "difficulty": ch.difficulty,
                "challenge_type": ch.challenge_type,
                "points": ch.points,
                "estimated_minutes": ch.estimated_minutes,
                "description": ch.description,
                "is_multi_stage": ch.is_multi_stage,
                "flag_format": ch.flag_format,
                "status": status,
                "created_at": ch.created_at,
            })
        return result

    @staticmethod
    def get_challenge_detail(
        db: Session,
        challenge_id_or_code: str | int,
        user_id: int | None = None,
    ) -> dict[str, Any] | None:
        """Retrieve complete challenge specifications without exposing flag hashes."""
        query = select(Challenge).options(
            joinedload(Challenge.stages),
            joinedload(Challenge.hints),
            joinedload(Challenge.evidence),
        )

        if isinstance(challenge_id_or_code, int) or str(challenge_id_or_code).isdigit():
            query = query.where(Challenge.id == int(challenge_id_or_code))
        else:
            query = query.where(Challenge.challenge_id == challenge_id_or_code)

        ch = db.scalars(query).first()
        if not ch:
            return None

        # Check user attempt status
        user_attempt = None
        if user_id:
            user_attempt = db.scalars(
                select(ChallengeAttempt).where(
                    ChallengeAttempt.challenge_id == ch.id,
                    ChallengeAttempt.user_id == user_id,
                )
            ).first()

        is_solved = user_attempt.solved if user_attempt else False
        is_revealed = user_attempt.revealed_solution if user_attempt else False

        # Only reveal solution walkthrough if solved or revealed
        explanation = ch.solution_explanation if (is_solved or is_revealed) else None
        mistakes = ch.common_mistakes if (is_solved or is_revealed) else "[]"

        # Safe hints presentation: only text of unlocked hints is shown
        hints_data = []
        unlocked_count = user_attempt.hints_unlocked if user_attempt else 0
        for h in sorted(ch.hints, key=lambda x: x.hint_number):
            is_unlocked = h.hint_number <= unlocked_count
            hints_data.append({
                "id": h.id,
                "hint_number": h.hint_number,
                "penalty_percent": h.penalty_percent,
                "penalty_points": h.penalty_points,
                "is_unlocked": is_unlocked,
                "hint_text": h.hint_text if is_unlocked else None,
            })

        evidence_data = [
            {
                "id": ev.id,
                "evidence_type": ev.evidence_type,
                "title": ev.title,
                "description": ev.description,
                "order_index": ev.order_index,
                "content_json": ev.content_json,
            }
            for ev in sorted(ch.evidence, key=lambda x: x.order_index)
        ]

        stages_data = [
            {
                "id": st.id,
                "stage_order": st.stage_order,
                "title": st.title,
                "description": st.description,
                "tasks_json": st.tasks_json,
                "points": st.points,
                "is_terminal": st.is_terminal,
            }
            for st in sorted(ch.stages, key=lambda x: x.stage_order)
        ]

        return {
            "id": ch.id,
            "challenge_id": ch.challenge_id,
            "title": ch.title,
            "category": ch.category,
            "difficulty": ch.difficulty,
            "challenge_type": ch.challenge_type,
            "points": ch.points,
            "estimated_minutes": ch.estimated_minutes,
            "description": ch.description,
            "scenario": ch.scenario,
            "learning_objectives": ch.learning_objectives,
            "prerequisites": ch.prerequisites,
            "environment_description": ch.environment_description,
            "tasks_json": ch.tasks_json,
            "skills_tested_json": ch.skills_tested_json,
            "related_lesson_slug": ch.related_lesson_slug,
            "related_lab_slug": ch.related_lab_slug,
            "related_mitre_technique": ch.related_mitre_technique,
            "flag_format": ch.flag_format,
            "is_multi_stage": ch.is_multi_stage,
            "simulation_only": ch.simulation_only,
            "stages": stages_data,
            "hints": hints_data,
            "evidence": evidence_data,
            "solution_explanation": explanation,
            "common_mistakes": mistakes,
            "is_solved": is_solved,
            "revealed_solution": is_revealed,
            "active_attempt_id": user_attempt.attempt_id if user_attempt else None,
        }

    @staticmethod
    def list_tracks(db: Session) -> list[dict[str, Any]]:
        """List active challenge curriculum tracks with challenges count."""
        tracks = db.scalars(
            select(ChallengeTrack)
            .where(ChallengeTrack.is_active == True)
            .options(joinedload(ChallengeTrack.items))
            .order_by(ChallengeTrack.order_index.asc())
        ).unique().all()

        return [
            {
                "id": t.id,
                "track_id": t.track_id,
                "title": t.title,
                "description": t.description,
                "target_role": t.target_role,
                "difficulty": t.difficulty,
                "badge_name": t.badge_name,
                "challenges_count": len(t.items),
            }
            for t in tracks
        ]

    @staticmethod
    def get_track_detail(db: Session, track_id: str) -> dict[str, Any] | None:
        """Retrieve track with sequential challenge items."""
        track = db.scalars(
            select(ChallengeTrack)
            .where(ChallengeTrack.track_id == track_id)
            .options(
                joinedload(ChallengeTrack.items).joinedload(ChallengeTrackItem.challenge)
            )
        ).unique().first()

        if not track:
            return None

        items_data = []
        for item in sorted(track.items, key=lambda x: x.order_index):
            ch = item.challenge
            items_data.append({
                "order_index": item.order_index,
                "is_required": item.is_required,
                "challenge": {
                    "id": ch.id,
                    "challenge_id": ch.challenge_id,
                    "title": ch.title,
                    "category": ch.category,
                    "difficulty": ch.difficulty,
                    "points": ch.points,
                    "estimated_minutes": ch.estimated_minutes,
                },
            })

        return {
            "id": track.id,
            "track_id": track.track_id,
            "title": track.title,
            "description": track.description,
            "target_role": track.target_role,
            "difficulty": track.difficulty,
            "badge_name": track.badge_name,
            "items": items_data,
        }

    @staticmethod
    def get_challenge_metrics(db: Session, user_id: int | None = None) -> dict[str, Any]:
        """Aggregate platform KPI metrics and student solving progress."""
        total_challenges = db.scalar(
            select(func.count(Challenge.id)).where(Challenge.is_active == True)
        ) or 0

        # Difficulties count
        diff_query = (
            select(Challenge.difficulty, func.count(Challenge.id))
            .where(Challenge.is_active == True)
            .group_by(Challenge.difficulty)
        )
        diff_counts = dict(db.execute(diff_query).all())

        # Category count
        cat_query = (
            select(Challenge.category, func.count(Challenge.id))
            .where(Challenge.is_active == True)
            .group_by(Challenge.category)
        )
        cat_counts = dict(db.execute(cat_query).all())

        # Student progress
        user_solved = 0
        user_in_progress = 0
        total_score_earned = 0.0
        if user_id:
            attempts = db.scalars(
                select(ChallengeAttempt).where(ChallengeAttempt.user_id == user_id)
            ).all()
            for att in attempts:
                if att.solved:
                    user_solved += 1
                    total_score_earned += att.score
                elif att.status == ChallengeAttemptStatus.IN_PROGRESS:
                    user_in_progress += 1

        return {
            "total_challenges": total_challenges,
            "difficulty_distribution": {
                str(k): v for k, v in diff_counts.items()
            },
            "category_distribution": {
                str(k): v for k, v in cat_counts.items()
            },
            "user_solved": user_solved,
            "user_in_progress": user_in_progress,
            "total_points_earned": total_score_earned,
            "completion_rate_percent": round((user_solved / max(total_challenges, 1)) * 100, 1),
        }


challenge_service = ChallengeService()
