"""Deterministic Training Priority Calculation Service.

Computes explainable P1-P4 priorities based on severity, confidence,
evidence volume, and packet frequency without black-box heuristics.
"""


from typing import ClassVar

from app.models.enums import AlertConfidence, AlertSeverity, TrainingPriority


class PrioritizationService:
    """Calculates deterministic training priority for SOC alerts."""

    SEVERITY_WEIGHTS: ClassVar[dict[str, int]] = {
        AlertSeverity.CRITICAL.value: 40,
        AlertSeverity.HIGH.value: 30,
        AlertSeverity.MEDIUM.value: 20,
        AlertSeverity.LOW.value: 10,
        AlertSeverity.INFO.value: 5,
    }

    CONFIDENCE_WEIGHTS: ClassVar[dict[str, int]] = {
        AlertConfidence.HIGH.value: 20,
        AlertConfidence.MEDIUM.value: 10,
        AlertConfidence.LOW.value: 5,
    }

    @classmethod
    def calculate_priority(
        cls,
        severity: str,
        confidence: str,
        evidence_count: int = 1,
        packet_count: int = 1,
    ) -> tuple[TrainingPriority, str]:
        """Compute training priority and an explainable technical justification."""
        sev_score = cls.SEVERITY_WEIGHTS.get(severity.upper(), 15)
        conf_score = cls.CONFIDENCE_WEIGHTS.get(confidence.upper(), 10)

        # Evidence volume score (up to 15 points)
        if evidence_count >= 10:
            ev_score = 15
        elif evidence_count >= 5:
            ev_score = 10
        elif evidence_count >= 1:
            ev_score = 5
        else:
            ev_score = 0

        # Frequency/packet activity score (up to 10 points)
        if packet_count >= 25:
            freq_score = 10
        elif packet_count >= 5:
            freq_score = 5
        else:
            freq_score = 2

        total_score = sev_score + conf_score + ev_score + freq_score

        if total_score >= 65:
            priority = TrainingPriority.P1
            reason = (
                f"P1 (Score {total_score}/85): Requires immediate analyst attention within this training scenario. "
                f"Derived from {severity} severity ({sev_score}pts), {confidence} confidence ({conf_score}pts), "
                f"and {evidence_count} evidence items."
            )
        elif total_score >= 50:
            priority = TrainingPriority.P2
            reason = (
                f"P2 (Score {total_score}/85): High-priority investigation. "
                f"Substantial corroborating evidence ({evidence_count} items) with {severity} severity."
            )
        elif total_score >= 30:
            priority = TrainingPriority.P3
            reason = (
                f"P3 (Score {total_score}/85): Normal investigation. "
                f"Standard detection threshold match requiring routine validation."
            )
        else:
            priority = TrainingPriority.P4
            reason = (
                f"P4 (Score {total_score}/85): Low-priority / noteworthy pattern. "
                f"Low severity or limited evidence volume."
            )

        return priority, reason


prioritization_service = PrioritizationService()
