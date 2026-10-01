from dataclasses import dataclass
from typing import Any

from app.models.enums import QuestionType
from app.models.mock_test import MockTestAttempt, MockTestQuestion, StudentAnswer
from app.models.question import Question


@dataclass
class TopicScoreDetail:
    topic_id: int
    topic_title: str
    total_questions: int
    correct_questions: int
    points_earned: float
    total_points: float
    percentage: float


@dataclass
class DifficultyScoreDetail:
    difficulty: str
    total_questions: int
    correct_questions: int
    percentage: float


@dataclass
class AttemptScoringResult:
    total_questions: int
    attempted_questions: int
    unanswered_questions: int
    correct_answers: int
    incorrect_answers: int
    total_points: float
    earned_points: float
    score: float
    percentage: float
    passed: bool
    passing_percentage: float
    topic_breakdown: list[dict[str, Any]]
    difficulty_breakdown: list[dict[str, Any]]


class ScoringService:
    """Authoritative server-side evaluation engine for mock examinations."""

    @staticmethod
    def score_single_choice(
        question: Question, selected_option_ids: list[int]
    ) -> tuple[bool, int]:
        """
        Evaluate single choice question.
        Award points only if exactly one option is selected and it is correct.
        """
        if len(selected_option_ids) != 1:
            return False, 0

        selected_id = selected_option_ids[0]
        for opt in question.options:
            if opt.id == selected_id and opt.is_correct:
                return True, question.points

        return False, 0

    @staticmethod
    def score_multiple_choice(
        question: Question, selected_option_ids: list[int]
    ) -> tuple[bool, int]:
        """
        Evaluate multiple choice question.
        Award points only if the selected set of option IDs matches the correct set.
        """
        if not selected_option_ids:
            return False, 0

        correct_ids = {opt.id for opt in question.options if opt.is_correct}
        selected_set = set(selected_option_ids)

        if selected_set == correct_ids:
            return True, question.points

        return False, 0

    @staticmethod
    def score_true_false(
        question: Question, selected_option_ids: list[int]
    ) -> tuple[bool, int]:
        """
        Evaluate true/false question.
        True/False questions are modeled as 2-option choices.
        """
        return ScoringService.score_single_choice(question, selected_option_ids)

    @classmethod
    def score_question(
        cls, question: Question, selected_option_ids: list[int]
    ) -> tuple[bool, int]:
        """Dispatch evaluation based on question type."""
        if question.question_type == QuestionType.SINGLE_CHOICE:
            return cls.score_single_choice(question, selected_option_ids)
        elif question.question_type == QuestionType.MULTIPLE_CHOICE:
            return cls.score_multiple_choice(question, selected_option_ids)
        elif question.question_type == QuestionType.TRUE_FALSE:
            return cls.score_true_false(question, selected_option_ids)
        else:
            # Fallback for choice-based questions
            return cls.score_single_choice(question, selected_option_ids)

    @classmethod
    def score_attempt(
        cls,
        attempt: MockTestAttempt,
        test_questions: list[MockTestQuestion],
        student_answers: list[StudentAnswer],
        passing_percentage: float = 70.0,
    ) -> AttemptScoringResult:
        """
        Score all questions in the test attempt, evaluate student answers,
        and generate topic and difficulty performance summaries.
        """
        answer_map: dict[int, StudentAnswer] = {
            ans.question_id: ans for ans in student_answers
        }

        total_questions = len(test_questions)
        attempted_questions = 0
        unanswered_questions = 0
        correct_answers = 0
        incorrect_answers = 0
        total_points = 0.0
        earned_points = 0.0

        # Topic aggregation: topic_id -> stats
        topic_stats: dict[int, dict[str, Any]] = {}
        # Difficulty aggregation: diff_str -> stats
        diff_stats: dict[str, dict[str, int]] = {}

        import json

        for link in test_questions:
            q = link.question
            points = link.points or (q.points if q else 1)
            total_points += points

            if not q:
                continue

            # Initialize topic tracker
            t_id = q.topic_id
            t_title = q.topic.title if q.topic else f"Topic {t_id}"
            if t_id not in topic_stats:
                topic_stats[t_id] = {
                    "topic_id": t_id,
                    "topic_title": t_title,
                    "total_questions": 0,
                    "correct_questions": 0,
                    "points_earned": 0.0,
                    "total_points": 0.0,
                }
            topic_stats[t_id]["total_questions"] += 1
            topic_stats[t_id]["total_points"] += points

            # Initialize difficulty tracker
            d_val = q.difficulty.value if hasattr(q.difficulty, "value") else str(q.difficulty)
            if d_val not in diff_stats:
                diff_stats[d_val] = {
                    "total_questions": 0,
                    "correct_questions": 0,
                }
            diff_stats[d_val]["total_questions"] += 1

            # Check student answer
            ans = answer_map.get(q.id)
            selected_ids: list[int] = []

            if ans and ans.answer_data:
                try:
                    data = json.loads(ans.answer_data)
                    if isinstance(data, list):
                        selected_ids = [int(x) for x in data]
                    elif isinstance(data, int):
                        selected_ids = [data]
                    elif isinstance(data, str) and data.isdigit():
                        selected_ids = [int(data)]
                except (json.JSONDecodeError, ValueError):
                    if ans.answer_data.isdigit():
                        selected_ids = [int(ans.answer_data)]

            if selected_ids:
                attempted_questions += 1
                is_correct, q_earned = cls.score_question(q, selected_ids)
                if is_correct:
                    correct_answers += 1
                    earned_points += q_earned
                    topic_stats[t_id]["correct_questions"] += 1
                    topic_stats[t_id]["points_earned"] += q_earned
                    diff_stats[d_val]["correct_questions"] += 1
                    if ans:
                        ans.is_correct = True
                        ans.points_earned = q_earned
                else:
                    incorrect_answers += 1
                    if ans:
                        ans.is_correct = False
                        ans.points_earned = 0
            else:
                unanswered_questions += 1
                if ans:
                    ans.is_correct = False
                    ans.points_earned = 0

        # Calculate final percentage
        percentage = (earned_points / total_points * 100.0) if total_points > 0 else 0.0
        percentage = round(percentage, 2)
        passed = percentage >= passing_percentage

        # Compile topic breakdown
        topic_breakdown: list[dict[str, Any]] = []
        for t_info in topic_stats.values():
            t_pct = (
                (t_info["points_earned"] / t_info["total_points"] * 100.0)
                if t_info["total_points"] > 0
                else 0.0
            )
            topic_breakdown.append(
                {
                    "topic_id": t_info["topic_id"],
                    "topic_title": t_info["topic_title"],
                    "total_questions": t_info["total_questions"],
                    "correct_questions": t_info["correct_questions"],
                    "points_earned": t_info["points_earned"],
                    "total_points": t_info["total_points"],
                    "percentage": round(t_pct, 1),
                }
            )

        # Compile difficulty breakdown
        difficulty_breakdown: list[dict[str, Any]] = []
        for diff_name, d_info in diff_stats.items():
            d_pct = (
                (d_info["correct_questions"] / d_info["total_questions"] * 100.0)
                if d_info["total_questions"] > 0
                else 0.0
            )
            difficulty_breakdown.append(
                {
                    "difficulty": diff_name,
                    "total_questions": d_info["total_questions"],
                    "correct_questions": d_info["correct_questions"],
                    "percentage": round(d_pct, 1),
                }
            )

        return AttemptScoringResult(
            total_questions=total_questions,
            attempted_questions=attempted_questions,
            unanswered_questions=unanswered_questions,
            correct_answers=correct_answers,
            incorrect_answers=incorrect_answers,
            total_points=total_points,
            earned_points=earned_points,
            score=earned_points,
            percentage=percentage,
            passed=passed,
            passing_percentage=passing_percentage,
            topic_breakdown=topic_breakdown,
            difficulty_breakdown=difficulty_breakdown,
        )


scoring_service = ScoringService()
