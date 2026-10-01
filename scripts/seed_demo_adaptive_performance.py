"""
Seed Script: Realistic Student Performance Profile for Adaptive Engine Demonstrations.

Simulates authentic student attempt history:
- Strong Topics: OSI Model, Networking Fundamentals (~90% accuracy)
- Weak Topics: IPv4 Subnetting, Firewalls (~50% accuracy -> NEEDS_PRACTICE)
- Developing Topics: DNS & DHCP, TCP/UDP (~70% accuracy -> DEVELOPING)
- Decayed Topic: TCP Mechanics (practiced 18 days ago)

Usage:
    backend\\.venv\\Scripts\\python.exe scripts/seed_demo_adaptive_performance.py
"""

from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys

# Ensure backend is on sys.path
backend_dir = Path(__file__).resolve().parents[1] / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.db.session import SessionLocal
from app.models.enums import AttemptStatus, DifficultyLevel, MockTestType, QuestionStatus
from app.models.mock_test import MockTest, MockTestAttempt, MockTestQuestion, StudentAnswer, TestResult
from app.models.question import Question
from app.models.user import User


def seed_demo_performance():
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == "student_dev").first()
        if not user:
            user = db.query(User).first()
        if not user:
            print("No users found. Please seed initial platform data first.")
            return

        print(f"[*] Seeding demo adaptive performance for student user: {user.username} (ID: {user.id})")

        now = datetime.now(timezone.utc)

        # 1. Clean previous demo adaptive mock tests for clean state
        old_tests = db.query(MockTest).filter(MockTest.slug.like("demo-perf-%")).all()
        for ot in old_tests:
            db.delete(ot)
        db.commit()

        # Helper to create an attempt
        def create_attempt(title, slug, diff, topic_slugs, accuracy_pct, days_ago, q_count=10):
            attempt_time = now - timedelta(days=days_ago)

            mt = MockTest(
                title=title,
                slug=f"demo-perf-{slug}-{int(now.timestamp())}",
                description=f"Demo diagnostic examination for {title}",
                test_type=MockTestType.TOPIC,
                difficulty=diff,
                duration_minutes=20,
                total_questions=q_count,
                passing_percentage=70.0,
                status=QuestionStatus.PUBLISHED,
            )
            db.add(mt)
            db.flush()

            # Find questions from topic_slugs
            candidate_qs = (
                db.query(Question)
                .join(Question.topic)
                .filter(
                    Question.status == QuestionStatus.PUBLISHED,
                    Question.topic.has(Question.topic.property.mapper.class_.slug.in_(topic_slugs)),
                )
                .limit(q_count)
                .all()
            )

            if len(candidate_qs) < q_count:
                existing_ids = [q.id for q in candidate_qs]
                # Backfill from any published
                more = (
                    db.query(Question)
                    .filter(
                        Question.status == QuestionStatus.PUBLISHED,
                        ~Question.id.in_(existing_ids) if existing_ids else True,
                    )
                    .limit(q_count - len(candidate_qs))
                    .all()
                )
                candidate_qs.extend(more)

            attempt = MockTestAttempt(
                mock_test_id=mt.id,
                user_id=user.id,
                started_at=attempt_time - timedelta(minutes=15),
                submitted_at=attempt_time,
                expires_at=attempt_time + timedelta(minutes=5),
                status=AttemptStatus.SUBMITTED,
                score=0.0,
                percentage=0.0,
            )
            db.add(attempt)
            db.flush()

            correct_count = 0
            for idx, q in enumerate(candidate_qs):
                link = MockTestQuestion(
                    mock_test_id=mt.id,
                    question_id=q.id,
                    order_index=idx,
                    points=q.points,
                )
                db.add(link)

                # Determine correctness based on target accuracy percentage
                is_correct = (idx / len(candidate_qs)) < (accuracy_pct / 100.0)
                if is_correct:
                    correct_count += 1

                ans = StudentAnswer(
                    attempt_id=attempt.id,
                    question_id=q.id,
                    answer_data=str([1]),  # simulated selection
                    is_correct=is_correct,
                    points_earned=q.points if is_correct else 0,
                    is_marked_for_review=False,
                    answered_at=attempt_time,
                )
                db.add(ans)

            pct = (correct_count / len(candidate_qs)) * 100.0
            attempt.score = float(correct_count)
            attempt.percentage = pct

            res = TestResult(
                attempt_id=attempt.id,
                correct_answers=correct_count,
                incorrect_answers=len(candidate_qs) - correct_count,
                unanswered=0,
                total_questions=len(candidate_qs),
                score=float(correct_count),
                total_points=float(len(candidate_qs)),
                earned_points=float(correct_count),
                percentage=pct,
                passing_percentage=70.0,
                passed=pct >= 70.0,
                time_taken_seconds=900,
            )
            db.add(res)
            db.commit()
            print(f"  [+] Created attempt: {title} | Accuracy: {pct:.1f}% ({days_ago} days ago)")

        # Create 4 realistic historical attempts:
        # Attempt 1: OSI 7-Layer Reference Model (1 day ago, 90% accuracy -> STRONG)
        create_attempt(
            title="OSI Model Fundamentals Quiz",
            slug="osi-quiz",
            diff=DifficultyLevel.BEGINNER,
            topic_slugs=["osi-model", "networking-fundamentals"],
            accuracy_pct=90.0,
            days_ago=1,
            q_count=10,
        )

        # Attempt 2: IPv4 Subnetting Practice (2 days ago, 50% accuracy -> NEEDS_PRACTICE)
        create_attempt(
            title="IPv4 Subnetting Drill",
            slug="subnet-drill",
            diff=DifficultyLevel.INTERMEDIATE,
            topic_slugs=["ipv4-subnetting", "subnetting"],
            accuracy_pct=50.0,
            days_ago=2,
            q_count=10,
        )

        # Attempt 3: DNS & DHCP Services (3 days ago, 70% accuracy -> DEVELOPING)
        create_attempt(
            title="DNS & DHCP Assessment",
            slug="dns-dhcp-quiz",
            diff=DifficultyLevel.INTERMEDIATE,
            topic_slugs=["dns-fundamentals", "dhcp-operations", "dns-dhcp"],
            accuracy_pct=70.0,
            days_ago=3,
            q_count=10,
        )

        # Attempt 4: TCP Protocol Mechanics (18 days ago, 90% accuracy -> Decayed Refresher trigger)
        create_attempt(
            title="TCP Transport Protocol Exam",
            slug="tcp-exam",
            diff=DifficultyLevel.BEGINNER,
            topic_slugs=["tcp-udp", "tcp-ip-model"],
            accuracy_pct=90.0,
            days_ago=18,
            q_count=10,
        )

        print("\n[*] Demo performance successfully seeded!")
        print("[*] Open http://localhost:5173/adaptive-test to view the active adaptive dashboard.")

    finally:
        db.close()


if __name__ == "__main__":
    seed_demo_performance()
