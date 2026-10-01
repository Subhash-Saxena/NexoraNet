"""Scenario Scoring Service for Advanced Educational SOC Scenarios.

Calculates transparent scores across the 9 investigation stages with
partial credit, noise penalties, hint deductions, and actionable feedback.
"""

import json
from typing import Any, ClassVar

from app.models.soc_scenario import SocScenario


class ScenarioScoringService:
    """Evaluates student actions against scenario rubric and generates feedback."""

    STAGE_WEIGHTS: ClassVar[dict[str, float]] = {
        "triage": 15.0,
        "evidence": 20.0,
        "correlation": 20.0,
        "hypothesis": 15.0,
        "mitre": 10.0,
        "response": 15.0,
        "documentation": 5.0,
    }

    HINT_PENALTY_POINTS = 5.0
    MAX_HINT_PENALTY = 15.0

    @classmethod
    def calculate_score(
        cls,
        scenario: SocScenario,
        stage_data: dict[str, Any],
        hints_used: int = 0,
    ) -> dict[str, Any]:
        """Compute transparent breakdown and feedback across all stages."""
        rubric: dict[str, Any] = {}
        if scenario.scoring_rubric_json:
            try:
                rubric = json.loads(scenario.scoring_rubric_json)
            except (json.JSONDecodeError, ValueError, TypeError):
                rubric = {}

        breakdown: dict[str, Any] = {}
        feedback: list[str] = []
        raw_total = 0.0

        # 1. Triage (15 pts)
        triage_data = stage_data.get("triage", {})
        expected_severity = rubric.get("expected_severity")
        selected_severity = triage_data.get("severity")
        triage_score = 0.0
        if expected_severity and selected_severity:
            if str(selected_severity).upper() == str(expected_severity).upper():
                triage_score = cls.STAGE_WEIGHTS["triage"]
                feedback.append("Initial Triage: Correctly identified alert classification and severity.")
            else:
                triage_score = cls.STAGE_WEIGHTS["triage"] * 0.5
                feedback.append(
                    f"Initial Triage: Selected {selected_severity}, but scenario warranted {expected_severity}."
                )
        else:
            triage_score = cls.STAGE_WEIGHTS["triage"] * 0.7
            feedback.append("Initial Triage: Initial review recorded.")
        breakdown["triage"] = round(triage_score, 1)
        raw_total += triage_score

        # 2. Evidence Selection (20 pts)
        selected_evidence = set(stage_data.get("selected_evidence_ids", []))
        expected_evidence = set(rubric.get("correct_evidence_ids", []))
        distractor_evidence = set(rubric.get("distractor_evidence_ids", []))

        evidence_score = 0.0
        if expected_evidence:
            true_positives = len(selected_evidence.intersection(expected_evidence))
            false_positives = len(selected_evidence.intersection(distractor_evidence))

            recall = true_positives / len(expected_evidence) if expected_evidence else 1.0
            precision_penalty = (false_positives / max(len(distractor_evidence), 1)) * 0.4

            evidence_ratio = max(0.0, recall - precision_penalty)
            evidence_score = cls.STAGE_WEIGHTS["evidence"] * evidence_ratio

            if recall >= 0.9 and false_positives == 0:
                feedback.append("Evidence Selection: Excellent precision. Gathered all key evidence without noise.")
            elif false_positives > 0:
                feedback.append(
                    f"Evidence Selection: Included {false_positives} irrelevant distractor item(s)."
                )
            else:
                feedback.append(
                    f"Evidence Selection: Missed {len(expected_evidence) - true_positives} key evidence artifacts."
                )
        else:
            evidence_score = cls.STAGE_WEIGHTS["evidence"]
            feedback.append("Evidence Selection: Artifact review confirmed.")
        breakdown["evidence"] = round(evidence_score, 1)
        raw_total += evidence_score

        # 3. Correlation (20 pts)
        selected_correlations = set(stage_data.get("selected_correlations", []))
        expected_correlations = set(rubric.get("correct_correlations", []))
        correlation_score = 0.0
        if expected_correlations:
            corr_matches = len(selected_correlations.intersection(expected_correlations))
            corr_ratio = corr_matches / len(expected_correlations)
            correlation_score = cls.STAGE_WEIGHTS["correlation"] * corr_ratio
            if corr_ratio >= 1.0:
                feedback.append("Correlation: Identified all root-cause event linkages across logs.")
            else:
                feedback.append(f"Correlation: Matched {corr_matches}/{len(expected_correlations)} key correlations.")
        else:
            correlation_score = cls.STAGE_WEIGHTS["correlation"]
            feedback.append("Correlation: Event telemetry linked.")
        breakdown["correlation"] = round(correlation_score, 1)
        raw_total += correlation_score

        # 4. Hypothesis (15 pts)
        selected_hypothesis = stage_data.get("selected_hypothesis_id")
        correct_hypothesis = rubric.get("correct_hypothesis_id")
        hypo_score = 0.0
        if correct_hypothesis:
            if str(selected_hypothesis) == str(correct_hypothesis):
                hypo_score = cls.STAGE_WEIGHTS["hypothesis"]
                feedback.append("Hypothesis: Formulated the accurate attack vector hypothesis.")
            else:
                hypo_score = cls.STAGE_WEIGHTS["hypothesis"] * 0.3
                feedback.append("Hypothesis: Selected plausible but incorrect primary hypothesis.")
        else:
            hypo_score = cls.STAGE_WEIGHTS["hypothesis"]
            feedback.append("Hypothesis: Hypothesis verified.")
        breakdown["hypothesis"] = round(hypo_score, 1)
        raw_total += hypo_score

        # 5. MITRE Mapping (10 pts)
        selected_mitre = set(stage_data.get("selected_mitre_techniques", []))
        expected_mitre = set(rubric.get("correct_mitre_techniques", []))
        mitre_score = 0.0
        if expected_mitre:
            mitre_matches = len(selected_mitre.intersection(expected_mitre))
            mitre_ratio = mitre_matches / len(expected_mitre)
            mitre_score = cls.STAGE_WEIGHTS["mitre"] * mitre_ratio
            if mitre_ratio >= 1.0:
                feedback.append("MITRE ATT&CK: 100% accuracy in adversary technique attribution.")
            else:
                feedback.append(f"MITRE ATT&CK: Mapped {mitre_matches}/{len(expected_mitre)} adversary techniques.")
        else:
            mitre_score = cls.STAGE_WEIGHTS["mitre"]
            feedback.append("MITRE ATT&CK: Technique mapping recorded.")
        breakdown["mitre"] = round(mitre_score, 1)
        raw_total += mitre_score

        # 6. Response Decision (15 pts)
        selected_responses = set(stage_data.get("selected_responses", []))
        optimal_responses = set(rubric.get("optimal_responses", []))
        harmful_responses = set(rubric.get("harmful_responses", []))
        response_score = 0.0
        if optimal_responses:
            resp_matches = len(selected_responses.intersection(optimal_responses))
            resp_harmful = len(selected_responses.intersection(harmful_responses))
            base_ratio = resp_matches / len(optimal_responses)
            penalty = (resp_harmful * 0.5)
            final_resp_ratio = max(0.0, base_ratio - penalty)
            response_score = cls.STAGE_WEIGHTS["response"] * final_resp_ratio

            if final_resp_ratio >= 1.0:
                feedback.append("Response Action: Deployed optimal containment strategy without collateral damage.")
            elif resp_harmful > 0:
                feedback.append("Response Action: Executed premature or disruptive response actions.")
            else:
                feedback.append("Response Action: Contained partially; critical containment action omitted.")
        else:
            response_score = cls.STAGE_WEIGHTS["response"]
            feedback.append("Response Action: Response containment executed.")
        breakdown["response"] = round(response_score, 1)
        raw_total += response_score

        # 7. Documentation & Lessons Learned (5 pts)
        notes = stage_data.get("lessons_learned", "")
        doc_score = min(cls.STAGE_WEIGHTS["documentation"], max(1.0, len(str(notes).strip()) / 20.0))
        breakdown["documentation"] = round(doc_score, 1)
        raw_total += doc_score
        feedback.append("Documentation: Post-incident review and lessons learned recorded.")

        # Hint penalty
        penalty = min(hints_used * cls.HINT_PENALTY_POINTS, cls.MAX_HINT_PENALTY)
        breakdown["hint_penalty"] = round(penalty, 1)
        if penalty > 0:
            feedback.append(f"Hints: Deducted {penalty:.0f} pts for utilizing {hints_used} progressive hint(s).")

        final_score = max(0.0, min(100.0, round(raw_total - penalty, 1)))

        return {
            "score": final_score,
            "max_score": 100.0,
            "breakdown": breakdown,
            "feedback": feedback,
            "passed": final_score >= 70.0,
        }
