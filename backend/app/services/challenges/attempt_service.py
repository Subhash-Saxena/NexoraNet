"""Attempt lifecycle, progressive hints, flag submissions, and solution reveals for Step 19.

Maintains student sandbox isolation and prevents flag enumeration attacks.
"""

import json
import uuid
from datetime import datetime, timezone
from typing import Any

from app.models.challenge import (
    Challenge,
    ChallengeAttempt,
    ChallengeHint,
    ChallengeSubmission,
)
from app.models.enums import ChallengeAttemptStatus
from app.services.challenges.flag_service import flag_service
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload


class AttemptService:
    """Manages active challenge solving attempts and submissions."""

    RATE_LIMIT_SECONDS = 2  # Minimum seconds between flag submissions per attempt
    MAX_ATTEMPTS_PER_CHALLENGE = 25  # Limit brute force flag guessing

    @classmethod
    def start_or_resume_attempt(
        cls,
        db: Session,
        challenge_id: int,
        user_id: int | None = None,
    ) -> ChallengeAttempt:
        """Start a new attempt or resume existing in-progress attempt."""
        challenge = db.get(Challenge, challenge_id)
        if not challenge or not challenge.is_active:
            raise ValueError("Challenge is not available or inactive.")

        existing = None
        if user_id:
            existing = db.scalars(
                select(ChallengeAttempt)
                .where(
                    ChallengeAttempt.challenge_id == challenge_id,
                    ChallengeAttempt.user_id == user_id,
                    ChallengeAttempt.status == ChallengeAttemptStatus.IN_PROGRESS,
                )
            ).first()

        if existing:
            existing.last_activity_at = datetime.now(timezone.utc)
            db.commit()
            db.refresh(existing)
            return existing

        attempt_id = f"ATT-CHAL-{uuid.uuid4().hex[:12].upper()}"
        new_attempt = ChallengeAttempt(
            attempt_id=attempt_id,
            challenge_id=challenge_id,
            user_id=user_id,
            status=ChallengeAttemptStatus.IN_PROGRESS,
            current_stage_order=1,
            stage_progress_json=json.dumps({"stage_1": "IN_PROGRESS"}),
            hints_unlocked=0,
            hints_penalty=0.0,
            attempts_count=0,
            score=0.0,
            max_score=float(challenge.points),
            solved=False,
            revealed_solution=False,
            started_at=datetime.now(timezone.utc),
            last_activity_at=datetime.now(timezone.utc),
            notes="",
        )
        db.add(new_attempt)
        db.commit()
        db.refresh(new_attempt)
        return new_attempt

    @classmethod
    def unlock_hint(
        cls,
        db: Session,
        attempt_id: str,
        user_id: int | None = None,
    ) -> dict[str, Any]:
        """Unlock next progressive hint and apply score penalty."""
        attempt = db.scalars(
            select(ChallengeAttempt).where(ChallengeAttempt.attempt_id == attempt_id)
        ).first()

        if not attempt:
            raise ValueError("Attempt not found.")
        if attempt.solved:
            raise ValueError("Challenge is already solved.")
        if attempt.revealed_solution:
            raise ValueError("Solution has already been revealed.")

        hints = list(db.scalars(
            select(ChallengeHint)
            .where(ChallengeHint.challenge_id == attempt.challenge_id)
            .order_by(ChallengeHint.hint_number.asc())
        ).all())
        next_hint_index = attempt.hints_unlocked

        if next_hint_index >= len(hints):
            return {
                "message": "All hints for this challenge are already unlocked.",
                "hint_number": attempt.hints_unlocked,
                "hint_text": hints[-1].hint_text if hints else None,
                "penalty_applied": 0.0,
                "total_penalty": attempt.hints_penalty,
                "remaining_hints": 0,
            }

        hint_to_unlock = hints[next_hint_index]

        # Calculate penalty
        penalty = float(hint_to_unlock.penalty_points)
        if hint_to_unlock.penalty_percent > 0:
            penalty = max(penalty, attempt.max_score * (hint_to_unlock.penalty_percent / 100.0))

        attempt.hints_unlocked += 1
        attempt.hints_penalty += penalty
        attempt.last_activity_at = datetime.now(timezone.utc)
        db.commit()

        return {
            "message": f"Hint #{hint_to_unlock.hint_number} unlocked.",
            "hint_number": hint_to_unlock.hint_number,
            "hint_text": hint_to_unlock.hint_text,
            "penalty_applied": penalty,
            "total_penalty": attempt.hints_penalty,
            "remaining_hints": len(hints) - attempt.hints_unlocked,
        }

    @classmethod
    def submit_flag(
        cls,
        db: Session,
        attempt_id: str,
        submitted_flag: str,
        user_id: int | None = None,
    ) -> dict[str, Any]:
        """Validate submitted flag, record attempt submission, and calculate score."""
        attempt = db.scalars(
            select(ChallengeAttempt)
            .where(ChallengeAttempt.attempt_id == attempt_id)
            .options(
                joinedload(ChallengeAttempt.challenge).joinedload(Challenge.stages)
            )
        ).first()

        if not attempt:
            raise ValueError("Attempt not found.")
        ch = attempt.challenge
        if attempt.solved:
            return {
                "is_correct": True,
                "solved": True,
                "points_awarded": 0.0,
                "current_score": attempt.score,
                "current_stage": attempt.current_stage_order,
                "feedback": "This challenge was already solved successfully.",
                "attempts_used": attempt.attempts_count,
                "solution_explanation": ch.solution_explanation,
            }
        if attempt.revealed_solution:
            return {
                "is_correct": False,
                "solved": False,
                "points_awarded": 0.0,
                "current_score": 0.0,
                "current_stage": attempt.current_stage_order,
                "feedback": "Solution was previously revealed. Submission no longer awarded points.",
                "attempts_used": attempt.attempts_count,
                "solution_explanation": ch.solution_explanation,
            }

        # Anti-enumeration & velocity limit check
        now = datetime.now(timezone.utc)
        if attempt.attempts_count >= cls.MAX_ATTEMPTS_PER_CHALLENGE:
            raise ValueError(
                f"Maximum attempts exceeded ({cls.MAX_ATTEMPTS_PER_CHALLENGE}). "
                "Consider unlocking a hint or reviewing the solution walkthrough."
            )

        # Recent submission rate limiting
        last_sub = db.scalars(
            select(ChallengeSubmission)
            .where(ChallengeSubmission.attempt_id == attempt.id)
            .order_by(ChallengeSubmission.submitted_at.desc())
        ).first()

        if last_sub and (now - last_sub.submitted_at.replace(tzinfo=timezone.utc)).total_seconds() < cls.RATE_LIMIT_SECONDS:
            raise ValueError("Submission rate limit exceeded. Please wait a moment before trying again.")

        ch = attempt.challenge

        # Handle multi-stage vs single-stage verification
        if ch.is_multi_stage and ch.stages:
            stages = sorted(ch.stages, key=lambda s: s.stage_order)
            curr_stage = next((s for s in stages if s.stage_order == attempt.current_stage_order), None)
            if not curr_stage:
                curr_stage = stages[0]

            is_correct, feedback = flag_service.verify_flag(
                submitted_flag=submitted_flag,
                expected_hash=curr_stage.flag_hash,
                salt=curr_stage.flag_salt,
                validation_type=ch.validation_type,
            )

            is_terminal = curr_stage.is_terminal or (curr_stage.stage_order >= len(stages))
        else:
            is_correct, feedback = flag_service.verify_flag(
                submitted_flag=submitted_flag,
                expected_hash=ch.flag_hash,
                salt=ch.flag_salt,
                validation_type=ch.validation_type,
            )
            is_terminal = True

        attempt.attempts_count += 1
        attempt.last_activity_at = now

        points_awarded = 0.0
        if is_correct:
            if is_terminal:
                attempt.solved = True
                attempt.status = ChallengeAttemptStatus.SOLVED
                attempt.completed_at = now
                earned_score = max(attempt.max_score - attempt.hints_penalty, 10.0)  # minimum 10 pts for correct solve
                attempt.score = earned_score
                points_awarded = earned_score
                feedback = "Congratulations! Flag verified. Challenge completed successfully!"
            else:
                # Advance stage
                next_stage_num = attempt.current_stage_order + 1
                attempt.current_stage_order = next_stage_num
                progress = json.loads(attempt.stage_progress_json or "{}")
                progress[f"stage_{next_stage_num}"] = "IN_PROGRESS"
                attempt.stage_progress_json = json.dumps(progress)
                feedback = f"Stage {curr_stage.stage_order} complete! Advanced to Stage {next_stage_num}."
        else:
            # Minor negative attempt penalty (1 point deduction, capped)
            if attempt.attempts_count > 3:
                attempt.hints_penalty = min(attempt.hints_penalty + 1.0, attempt.max_score * 0.5)

        # Record submission log
        submission = ChallengeSubmission(
            attempt_id=attempt.id,
            challenge_id=ch.id,
            user_id=user_id or attempt.user_id,
            submitted_flag=submitted_flag[:128],  # truncate to prevent DB blowup
            is_correct=is_correct,
            points_awarded=points_awarded,
            feedback=feedback,
            submitted_at=now,
        )
        db.add(submission)
        db.commit()

        return {
            "is_correct": is_correct,
            "solved": attempt.solved,
            "points_awarded": points_awarded,
            "current_score": attempt.score,
            "current_stage": attempt.current_stage_order,
            "feedback": feedback,
            "attempts_used": attempt.attempts_count,
            "solution_explanation": ch.solution_explanation if attempt.solved else None,
        }

    @classmethod
    def reveal_solution(
        cls,
        db: Session,
        attempt_id: str,
        user_id: int | None = None,
    ) -> dict[str, Any]:
        """Reveal solution walkthrough when student gives up. Awards 0 points."""
        attempt = db.scalars(
            select(ChallengeAttempt)
            .where(ChallengeAttempt.attempt_id == attempt_id)
            .options(joinedload(ChallengeAttempt.challenge))
        ).first()

        if not attempt:
            raise ValueError("Attempt not found.")

        attempt.revealed_solution = True
        attempt.status = ChallengeAttemptStatus.ABANDONED
        attempt.score = 0.0
        attempt.completed_at = datetime.now(timezone.utc)
        attempt.last_activity_at = datetime.now(timezone.utc)
        db.commit()

        ch = attempt.challenge
        return {
            "revealed": True,
            "score": 0.0,
            "solution_explanation": ch.solution_explanation,
            "common_mistakes": ch.common_mistakes,
            "message": "Solution walkthrough revealed for educational review.",
        }

    @classmethod
    def save_notes(
        cls,
        db: Session,
        attempt_id: str,
        notes_text: str,
    ) -> ChallengeAttempt:
        """Autosave student private notes safely."""
        attempt = db.scalars(
            select(ChallengeAttempt).where(ChallengeAttempt.attempt_id == attempt_id)
        ).first()

        if not attempt:
            raise ValueError("Attempt not found.")

        # Sanitize plain text (truncate to max 20,000 chars)
        attempt.notes = notes_text[:20000] if notes_text else ""
        attempt.last_activity_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(attempt)
        return attempt


attempt_service = AttemptService()
