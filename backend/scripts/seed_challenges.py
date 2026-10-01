"""Master Seed Script for Step 19: CTF / Challenges & Advanced Cybersecurity Training Engine.

Seeds:
1. 40 Synthetic Challenges across 4 difficulties (10 Beginner, 12 Intermediate, 12 Advanced, 6 Expert)
2. 5 Structured Challenge Curriculum Tracks
3. Interactive CTF methodology lessons
4. Question Bank challenge questions
"""

import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.db.session import SessionLocal
from app.services.challenges.seed_challenges import seed_challenges
from app.services.challenges.seed_learning_and_questions import (
    seed_challenge_lessons_and_questions,
)


def main() -> None:
    print("=" * 70)
    print("NexoraNet Step 19: Seeding CTF Challenges & Advanced Training Engine...")
    print("=" * 70)

    db = SessionLocal()
    try:
        # 1. Challenges and Tracks
        print("\n--- Seeding 40 Challenges and 5 Tracks ---")
        seed_challenges(db)

        # 2. Lessons and Questions
        print("\n--- Seeding CTF Lessons and Question Bank Items ---")
        stats = seed_challenge_lessons_and_questions(db)
        print(f"Added {stats['lessons_added']} lessons and {stats['questions_added']} questions.")

        print("\n" + "=" * 70)
        print("Step 19 Seeding Completed Successfully!")
        print("=" * 70)
    except Exception as e:
        db.rollback()
        print(f"Error during seeding: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
