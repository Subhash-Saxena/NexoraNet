"""
NexoraNet Adaptive Testing & Personalized Practice Engine Configuration.

This module centralizes all statistical thresholds, recency weights, sample size
confidences, and distribution policies. No scattered magic numbers exist in the codebase.
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class AdaptiveConfig:
    """Configurable hyperparameters for the rule-based adaptive engine."""

    # Sample Size & Confidence Thresholds
    ADAPTIVE_MIN_QUESTIONS: int = 5  # < 5 is INSUFFICIENT_DATA
    ADAPTIVE_PRELIMINARY_LIMIT: int = 9  # 5-9 is PRELIMINARY
    ADAPTIVE_DEVELOPING_LIMIT: int = 19  # 10-19 is DEVELOPING signal; 20+ is STRONG signal

    # Performance Window Limits
    ADAPTIVE_RECENT_ATTEMPTS: int = 5  # Window of recent completed mock attempts
    ADAPTIVE_RECENT_QUESTION_LIMIT: int = 100  # Max questions evaluated in recent window

    # Topic Performance State Accuracy Thresholds (in percentage)
    # < 60.0: NEEDS_PRACTICE
    # 60.0 - 79.99: DEVELOPING
    # 80.0 - 89.99: SOLID
    # >= 90.0: STRONG
    ADAPTIVE_NEEDS_PRACTICE_THRESHOLD: float = 60.0
    ADAPTIVE_DEVELOPING_THRESHOLD: float = 80.0
    ADAPTIVE_SOLID_THRESHOLD: float = 90.0
    ADAPTIVE_STRONG_THRESHOLD: float = 90.0

    # Difficulty Recommendation Thresholds
    ADAPTIVE_BEGINNER_LOWER_THRESHOLD: float = 60.0
    ADAPTIVE_BEGINNER_UPPER_THRESHOLD: float = 80.0
    ADAPTIVE_INTERMEDIATE_LOWER_THRESHOLD: float = 60.0
    ADAPTIVE_INTERMEDIATE_UPPER_THRESHOLD: float = 80.0
    ADAPTIVE_ADVANCED_THRESHOLD: float = 60.0

    # Default Practice Session Sizing
    ADAPTIVE_DEFAULT_QUESTION_COUNT: int = 20
    ADAPTIVE_DEFAULT_DURATION_MINUTES: int = 20

    # Recency Exponentially Decaying Weights (most recent attempt at index 0)
    ADAPTIVE_RECENCY_WEIGHTS: list[float] = field(
        default_factory=lambda: [1.00, 0.85, 0.70, 0.55, 0.40]
    )

    # Adaptive Question Selection Distribution (Target topic allocation)
    ADAPTIVE_TOPIC_TARGET_DISTRIBUTION: dict[str, float] = field(
        default_factory=lambda: {
            "NEEDS_PRACTICE": 0.50,  # 50% weak topics
            "DEVELOPING": 0.30,  # 30% developing topics
            "SOLID": 0.15,  # 15% solid reinforcement
            "STRONG": 0.05,  # 5% strong topic maintenance
        }
    )

    # Repetition Suppression
    ADAPTIVE_NO_REPEAT_ATTEMPTS_COUNT: int = 2  # Suppress questions seen in last 2 attempts

    # Performance Decay Window (days without practice before suggesting a quick review)
    ADAPTIVE_DECAY_DAYS: int = 14

    def get_recency_weight(self, chronological_idx: int) -> float:
        """
        Get weight for an attempt where chronological_idx=0 is the most recent attempt.
        """
        if chronological_idx < len(self.ADAPTIVE_RECENCY_WEIGHTS):
            return self.ADAPTIVE_RECENCY_WEIGHTS[chronological_idx]
        return 0.30  # Floor weight for older attempts in window


adaptive_config = AdaptiveConfig()
