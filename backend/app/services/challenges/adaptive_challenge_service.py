"""Adaptive recommendation engine for Step 19 CTF Challenges.

Integrates challenge solving telemetry with curriculum lessons and hands-on labs.
"""

from typing import Any

from app.models.challenge import Challenge, ChallengeAttempt
from app.models.enums import (
    ChallengeDifficulty,
)
from sqlalchemy import select
from sqlalchemy.orm import Session


class AdaptiveChallengeService:
    """Generates explainable, pedagogical recommendations for challenge practice."""

    @classmethod
    def get_recommendations(
        cls,
        db: Session,
        user_id: int | None = None,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        """Compute personalized next actions based on attempt history."""
        recommendations = []

        if not user_id:
            # Cold start: recommend foundational beginner challenges
            beginner_challenges = db.scalars(
                select(Challenge)
                .where(
                    Challenge.difficulty == ChallengeDifficulty.BEGINNER,
                    Challenge.is_active == True,
                )
                .limit(limit)
            ).all()

            for ch in beginner_challenges:
                recommendations.append({
                    "type": "CHALLENGE",
                    "title": ch.title,
                    "challenge_id": ch.challenge_id,
                    "category": ch.category,
                    "difficulty": ch.difficulty,
                    "points": ch.points,
                    "reason": "Foundational beginner challenge to start your defensive skill journey.",
                    "action_url": f"/challenges/{ch.challenge_id}",
                    "related_lesson_slug": ch.related_lesson_slug,
                    "related_lab_slug": ch.related_lab_slug,
                })
            return recommendations

        # Analyze user's solved and in-progress challenges
        attempts = db.scalars(
            select(ChallengeAttempt)
            .where(ChallengeAttempt.user_id == user_id)
            .order_by(ChallengeAttempt.last_activity_at.desc())
        ).all()

        solved_ids = {a.challenge_id for a in attempts if a.solved}
        revealed_attempts = [a for a in attempts if a.revealed_solution or (a.attempts_count > 3 and not a.solved)]

        # 1. Remediation recommendation if student struggled on recent challenge
        if revealed_attempts:
            struggled_ch = db.get(Challenge, revealed_attempts[0].challenge_id)
            if struggled_ch and (struggled_ch.related_lesson_slug or struggled_ch.related_lab_slug):
                recommendations.append({
                    "type": "REINFORCE_CONCEPTS",
                    "title": f"Review Concepts for {struggled_ch.title}",
                    "challenge_id": struggled_ch.challenge_id,
                    "category": struggled_ch.category,
                    "difficulty": struggled_ch.difficulty,
                    "points": 0,
                    "reason": f"Reinforce core {struggled_ch.category.replace('_', ' ').lower()} principles to master upcoming challenges.",
                    "action_url": f"/learning/lessons/{struggled_ch.related_lesson_slug}" if struggled_ch.related_lesson_slug else f"/labs/{struggled_ch.related_lab_slug}",
                    "related_lesson_slug": struggled_ch.related_lesson_slug,
                    "related_lab_slug": struggled_ch.related_lab_slug,
                })

        # 2. Progression recommendation: next unsolved challenge in highest practiced category
        unsolved_query = select(Challenge).where(
            Challenge.is_active == True,
            ~Challenge.id.in_(solved_ids) if solved_ids else True,
        ).order_by(Challenge.difficulty.asc(), Challenge.points.asc()).limit(limit - len(recommendations))

        unsolved_challenges = db.scalars(unsolved_query).all()
        for ch in unsolved_challenges:
            recommendations.append({
                "type": "CHALLENGE",
                "title": ch.title,
                "challenge_id": ch.challenge_id,
                "category": ch.category,
                "difficulty": ch.difficulty,
                "points": ch.points,
                "reason": f"Next challenge in {ch.category.replace('_', ' ').lower()} track to advance your defensive competency.",
                "action_url": f"/challenges/{ch.challenge_id}",
                "related_lesson_slug": ch.related_lesson_slug,
                "related_lab_slug": ch.related_lab_slug,
            })

        return recommendations[:limit]


adaptive_challenge_service = AdaptiveChallengeService()
