import pytest
from app.models.enums import DifficultyLevel, QuestionType
from app.services.question_validator import (
    QuestionValidationError,
    validate_question_structure,
)


def test_valid_single_choice_question():
    """Verify standard single choice validation succeeds."""
    validate_question_structure(
        question_text="What is the default port for HTTPS?",
        question_type=QuestionType.SINGLE_CHOICE,
        difficulty=DifficultyLevel.BEGINNER,
        points=1,
        explanation="Port 443 is assigned to TLS-encrypted HTTP by IANA.",
        options=[
            {"option_text": "80", "is_correct": False},
            {"option_text": "443", "is_correct": True},
            {"option_text": "22", "is_correct": False},
        ],
    )


def test_single_choice_invalid_correct_count():
    """Verify single choice fails if 0 or >1 options are marked correct."""
    with pytest.raises(
        QuestionValidationError, match="must have exactly 1 correct option"
    ):
        validate_question_structure(
            question_text="Sample text",
            question_type=QuestionType.SINGLE_CHOICE,
            difficulty=DifficultyLevel.BEGINNER,
            points=1,
            explanation="Explanation",
            options=[
                {"option_text": "Option A", "is_correct": False},
                {"option_text": "Option B", "is_correct": False},
            ],
        )

    with pytest.raises(
        QuestionValidationError, match="must have exactly 1 correct option"
    ):
        validate_question_structure(
            question_text="Sample text",
            question_type=QuestionType.SINGLE_CHOICE,
            difficulty=DifficultyLevel.BEGINNER,
            points=1,
            explanation="Explanation",
            options=[
                {"option_text": "Option A", "is_correct": True},
                {"option_text": "Option B", "is_correct": True},
            ],
        )


def test_true_false_option_count_validation():
    """Verify true/false must have exactly two options."""
    with pytest.raises(QuestionValidationError, match="must contain exactly 2 options"):
        validate_question_structure(
            question_text="Sample statement",
            question_type=QuestionType.TRUE_FALSE,
            difficulty=DifficultyLevel.BEGINNER,
            points=1,
            explanation="Explanation",
            options=[
                {"option_text": "True", "is_correct": True},
            ],
        )


def test_negative_points_rejection():
    """Verify question points must be strictly greater than zero."""
    with pytest.raises(QuestionValidationError, match="positive integer"):
        validate_question_structure(
            question_text="Sample text",
            question_type=QuestionType.SINGLE_CHOICE,
            difficulty=DifficultyLevel.BEGINNER,
            points=0,
            explanation="Explanation",
            options=[
                {"option_text": "A", "is_correct": True},
                {"option_text": "B", "is_correct": False},
            ],
        )


def test_empty_explanation_rejection():
    """Verify an authoritative explanation is required for all questions."""
    with pytest.raises(QuestionValidationError, match="explanation must be provided"):
        validate_question_structure(
            question_text="Sample text",
            question_type=QuestionType.SINGLE_CHOICE,
            difficulty=DifficultyLevel.BEGINNER,
            points=1,
            explanation="",
            options=[
                {"option_text": "A", "is_correct": True},
                {"option_text": "B", "is_correct": False},
            ],
        )
