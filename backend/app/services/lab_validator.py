"""NexoraNet Lab Answer Validation Engine.

Provides secure, deterministic, server-side validation for hands-on networking
and defensive cybersecurity lab submissions. Enforces zero-knowledge answer
shielding to ensure answer keys never leak to frontend clients before grading.
"""

from __future__ import annotations

import ipaddress
import json
import logging
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger("nexoranet.lab_validator")


@dataclass
class ValidationResult:
    """Evaluation result for a student step or question submission."""

    is_correct: bool
    points_earned: float
    max_points: float
    feedback: str
    explanation: str | None = None


def _parse_answer_data(raw_data: str | dict[str, Any]) -> dict[str, Any]:
    """Safely parse answer data dictionary from JSON or dict."""
    if isinstance(raw_data, dict):
        return raw_data
    try:
        return json.loads(raw_data)
    except (json.JSONDecodeError, TypeError, ValueError):
        logger.warning("Failed to parse answer_data as JSON: %s", raw_data)
        return {"raw": str(raw_data)}


def validate_single_choice(
    submitted_answer: Any,
    rule: dict[str, Any],
    max_points: float = 10.0,
) -> ValidationResult:
    """Validate single choice selection against correct option."""
    student_choice = str(submitted_answer).strip()
    correct_option = str(rule.get("correct_option", rule.get("correct_answer", ""))).strip()

    explanation = rule.get("explanation")
    correct_option = str(rule.get("correct_option", rule.get("correct_answer", ""))).strip()
    correct_options = [str(x).strip().lower() for x in rule.get("correct_options", [])]
    if correct_option:
        correct_options.append(correct_option.lower())

    options = rule.get("options", [])

    # If student submitted option index (e.g. "1")
    if student_choice.isdigit() and options:
        idx = int(student_choice)
        if 1 <= idx <= len(options):
            opt_val = options[idx - 1]
            student_choice = opt_val if isinstance(opt_val, str) else opt_val.get("text", str(opt_val))

    if student_choice.lower() in correct_options or (correct_option and student_choice.lower() == correct_option.lower()):
        return ValidationResult(
            is_correct=True,
            points_earned=max_points,
            max_points=max_points,
            feedback="Correct! Exactly the expected networking choice.",
            explanation=explanation,
        )

    return ValidationResult(
        is_correct=False,
        points_earned=0.0,
        max_points=max_points,
        feedback=rule.get("incorrect_feedback", "Incorrect option selected. Review the concept and try again."),
        explanation=explanation,
    )


def validate_multiple_choice(
    submitted_answer: Any,
    rule: dict[str, Any],
    max_points: float = 10.0,
) -> ValidationResult:
    """Validate multi-selection options with optional partial credit."""
    if isinstance(submitted_answer, list):
        student_set = {str(x).strip().lower() for x in submitted_answer}
    elif isinstance(submitted_answer, str):
        try:
            parsed = json.loads(submitted_answer)
            if isinstance(parsed, list):
                student_set = {str(x).strip().lower() for x in parsed}
            else:
                student_set = {s.strip().lower() for s in submitted_answer.split(",")}
        except (json.JSONDecodeError, TypeError, ValueError):
            student_set = {s.strip().lower() for s in submitted_answer.split(",")}
    else:
        student_set = set()

    raw_correct = rule.get("correct_options", rule.get("correct_answers", []))
    correct_set = {str(x).strip().lower() for x in raw_correct}
    explanation = rule.get("explanation")

    if not correct_set:
        return ValidationResult(
            is_correct=False,
            points_earned=0.0,
            max_points=max_points,
            feedback="Assessment rule is missing correct options configuration.",
        )

    # Exact match
    if student_set == correct_set:
        return ValidationResult(
            is_correct=True,
            points_earned=max_points,
            max_points=max_points,
            feedback="Correct! All matching options selected.",
            explanation=explanation,
        )

    # Calculate partial credit if enabled
    allow_partial = rule.get("allow_partial_credit", True)
    correct_selected = len(student_set & correct_set)
    incorrect_selected = len(student_set - correct_set)

    if allow_partial and correct_selected > 0 and incorrect_selected == 0:
        partial_ratio = correct_selected / len(correct_set)
        partial_points = round(max_points * partial_ratio, 1)
        return ValidationResult(
            is_correct=False,
            points_earned=partial_points,
            max_points=max_points,
            feedback=f"Partially correct ({correct_selected}/{len(correct_set)} correct options selected, no incorrect choices). Select all applicable options to earn full points.",
            explanation=explanation,
        )

    return ValidationResult(
        is_correct=False,
        points_earned=0.0,
        max_points=max_points,
        feedback=rule.get("incorrect_feedback", "Incorrect selection. Ensure all applicable criteria are satisfied."),
        explanation=explanation,
    )


def validate_text(
    submitted_answer: Any,
    rule: dict[str, Any],
    max_points: float = 10.0,
) -> ValidationResult:
    """Validate text input with controlled whitespace trimming and case normalization."""
    student_text = str(submitted_answer or "").strip()
    case_sensitive = rule.get("case_sensitive", False)
    explanation = rule.get("explanation")

    accepted_answers: list[str] = rule.get("accepted_answers", [])
    if "exact_answer" in rule:
        accepted_answers.append(str(rule["exact_answer"]))

    norm_student = student_text if case_sensitive else student_text.lower()
    norm_accepted = [
        ans.strip() if case_sensitive else ans.strip().lower()
        for ans in accepted_answers
    ]

    if norm_student in norm_accepted:
        return ValidationResult(
            is_correct=True,
            points_earned=max_points,
            max_points=max_points,
            feedback="Correct observation verified!",
            explanation=explanation,
        )

    # Check keyword presence if specified
    contains_all: list[str] = rule.get("contains_all", [])
    if contains_all:
        norm_req = [c if case_sensitive else c.lower() for c in contains_all]
        if all(c in norm_student for c in norm_req):
            return ValidationResult(
                is_correct=True,
                points_earned=max_points,
                max_points=max_points,
                feedback="Correct! All necessary concepts and identifiers are present.",
                explanation=explanation,
            )

    return ValidationResult(
        is_correct=False,
        points_earned=0.0,
        max_points=max_points,
        feedback=rule.get("incorrect_feedback", f"'{student_text}' does not match the expected network parameter."),
        explanation=explanation,
    )


def validate_numerical(
    submitted_answer: Any,
    rule: dict[str, Any],
    max_points: float = 10.0,
) -> ValidationResult:
    """Validate numeric input with optional tolerance."""
    explanation = rule.get("explanation")
    try:
        val = float(str(submitted_answer).strip())
    except (ValueError, TypeError):
        return ValidationResult(
            is_correct=False,
            points_earned=0.0,
            max_points=max_points,
            feedback="Please enter a valid numeric value.",
            explanation=explanation,
        )

    target = float(rule.get("expected_value", rule.get("correct_answer", 0)))
    tolerance = float(rule.get("tolerance", 0.0001))

    if abs(val - target) <= tolerance:
        return ValidationResult(
            is_correct=True,
            points_earned=max_points,
            max_points=max_points,
            feedback="Accurate calculation verified!",
            explanation=explanation,
        )

    return ValidationResult(
        is_correct=False,
        points_earned=0.0,
        max_points=max_points,
        feedback=rule.get("incorrect_feedback", f"Calculated value {val} is incorrect."),
        explanation=explanation,
    )


def validate_ip_address(
    submitted_answer: Any,
    rule: dict[str, Any],
    max_points: float = 10.0,
) -> ValidationResult:
    """Validate IPv4 or IPv6 address with RFC syntax checking and range constraints."""
    raw_ip = str(submitted_answer or "").strip()
    explanation = rule.get("explanation")

    try:
        parsed_ip = ipaddress.ip_address(raw_ip)
    except ValueError:
        return ValidationResult(
            is_correct=False,
            points_earned=0.0,
            max_points=max_points,
            feedback=f"'{raw_ip}' is not a valid IPv4 or IPv6 address syntax (e.g. 192.168.1.1).",
            explanation=explanation,
        )

    # Check version constraint
    expected_version = rule.get("expected_version")
    if expected_version and parsed_ip.version != int(expected_version):
        return ValidationResult(
            is_correct=False,
            points_earned=0.0,
            max_points=max_points,
            feedback=f"Expected an IPv{expected_version} address, but received IPv{parsed_ip.version}.",
            explanation=explanation,
        )

    # Check specific IP match
    expected_ip_str = rule.get("expected_ip", rule.get("correct_answer"))
    if expected_ip_str:
        expected_ip = ipaddress.ip_address(str(expected_ip_str).strip())
        if parsed_ip == expected_ip:
            return ValidationResult(
                is_correct=True,
                points_earned=max_points,
                max_points=max_points,
                feedback=f"Correct! {parsed_ip} matches the target address.",
                explanation=explanation,
            )
        return ValidationResult(
            is_correct=False,
            points_earned=0.0,
            max_points=max_points,
            feedback=rule.get("incorrect_feedback", f"Address {parsed_ip} does not match expected destination {expected_ip}."),
            explanation=explanation,
        )

    # Check accepted list of IPs
    accepted_ips = rule.get("accepted_ips")
    if accepted_ips:
        norm_accepted = [ipaddress.ip_address(str(x).strip()) for x in accepted_ips]
        if parsed_ip in norm_accepted:
            return ValidationResult(
                is_correct=True,
                points_earned=max_points,
                max_points=max_points,
                feedback=f"Valid address {parsed_ip} confirmed.",
                explanation=explanation,
            )

    # Check property constraints (e.g. private, loopback)
    if rule.get("require_private", False) and not parsed_ip.is_private:
        return ValidationResult(
            is_correct=False,
            points_earned=0.0,
            max_points=max_points,
            feedback=f"{parsed_ip} is a public routable address, but an RFC 1918 private address (10.x.x.x, 172.16-31.x.x, 192.168.x.x) was expected.",
            explanation=explanation,
        )

    if rule.get("require_loopback", False) and not parsed_ip.is_loopback:
        return ValidationResult(
            is_correct=False,
            points_earned=0.0,
            max_points=max_points,
            feedback=f"{parsed_ip} is not a loopback address (e.g. 127.0.0.1 or ::1).",
            explanation=explanation,
        )

    # Check within subnet range
    within_subnet = rule.get("within_subnet")
    if within_subnet:
        net = ipaddress.ip_network(within_subnet, strict=False)
        if parsed_ip not in net:
            return ValidationResult(
                is_correct=False,
                points_earned=0.0,
                max_points=max_points,
                feedback=f"{parsed_ip} is outside expected network prefix {within_subnet}.",
                explanation=explanation,
            )

    return ValidationResult(
        is_correct=True,
        points_earned=max_points,
        max_points=max_points,
        feedback=f"Valid network address {parsed_ip} accepted!",
        explanation=explanation,
    )


def validate_cidr(
    submitted_answer: Any,
    rule: dict[str, Any],
    max_points: float = 10.0,
) -> ValidationResult:
    """Validate CIDR network prefix notation (e.g. 192.168.10.0/24)."""
    raw_cidr = str(submitted_answer or "").strip()
    explanation = rule.get("explanation")

    # If asking specifically for just the prefix length (e.g., /26 or 26)
    if rule.get("prefix_only", False):
        clean_prefix = raw_cidr.lstrip("/")
        expected_prefix = str(rule.get("expected_prefix_length", rule.get("expected_value", ""))).lstrip("/")
        if clean_prefix == expected_prefix:
            return ValidationResult(
                is_correct=True,
                points_earned=max_points,
                max_points=max_points,
                feedback=f"Correct CIDR prefix /{clean_prefix}!",
                explanation=explanation,
            )
        return ValidationResult(
            is_correct=False,
            points_earned=0.0,
            max_points=max_points,
            feedback=f"/{clean_prefix} is incorrect. Expected /{expected_prefix}.",
            explanation=explanation,
        )

    try:
        parsed_net = ipaddress.ip_network(raw_cidr, strict=False)
    except ValueError:
        return ValidationResult(
            is_correct=False,
            points_earned=0.0,
            max_points=max_points,
            feedback=f"'{raw_cidr}' is not a valid CIDR network notation (e.g. 192.168.1.0/24).",
            explanation=explanation,
        )

    expected_cidr_str = rule.get("expected_cidr", rule.get("correct_answer"))
    if expected_cidr_str:
        expected_net = ipaddress.ip_network(str(expected_cidr_str).strip(), strict=False)
        if parsed_net == expected_net:
            return ValidationResult(
                is_correct=True,
                points_earned=max_points,
                max_points=max_points,
                feedback=f"Correct CIDR network {parsed_net} verified!",
                explanation=explanation,
            )
        return ValidationResult(
            is_correct=False,
            points_earned=0.0,
            max_points=max_points,
            feedback=rule.get("incorrect_feedback", f"Calculated CIDR {parsed_net} does not match expected {expected_net}."),
            explanation=explanation,
        )

    return ValidationResult(
        is_correct=True,
        points_earned=max_points,
        max_points=max_points,
        feedback=f"Valid CIDR network {parsed_net} confirmed.",
        explanation=explanation,
    )


def validate_subnet(
    submitted_answer: Any,
    rule: dict[str, Any],
    max_points: float = 10.0,
) -> ValidationResult:
    """Validate subnet parameters: network address, broadcast address, mask, or multi-field subnet map."""
    explanation = rule.get("explanation")

    # If submission is a dictionary of subnet parameters
    if isinstance(submitted_answer, dict) or (
        isinstance(submitted_answer, str) and submitted_answer.strip().startswith("{")
    ):
        try:
            sub_dict = (
                submitted_answer
                if isinstance(submitted_answer, dict)
                else json.loads(submitted_answer)
            )
        except (json.JSONDecodeError, TypeError, ValueError):
            sub_dict = {}

        expected_map = rule.get("expected_subnet_map", {})
        if not expected_map:
            expected_map = {
                k: rule[k]
                for k in ["network_address", "broadcast_address", "first_host", "last_host", "subnet_mask"]
                if k in rule
            }

        total_keys = len(expected_map)
        matched_keys = 0
        mismatch_details = []

        for key, exp_val in expected_map.items():
            stu_val = str(sub_dict.get(key, "")).strip().lower()
            exp_clean = str(exp_val).strip().lower()
            if stu_val == exp_clean:
                matched_keys += 1
            else:
                mismatch_details.append(f"{key.replace('_', ' ').title()}: expected '{exp_clean}', got '{stu_val}'")

        if total_keys > 0 and matched_keys == total_keys:
            return ValidationResult(
                is_correct=True,
                points_earned=max_points,
                max_points=max_points,
                feedback="All subnet boundary parameters (network, broadcast, host range) are mathematically correct!",
                explanation=explanation,
            )

        if total_keys > 0 and matched_keys > 0:
            earned = round(max_points * (matched_keys / total_keys), 1)
            return ValidationResult(
                is_correct=False,
                points_earned=earned,
                max_points=max_points,
                feedback=f"Partially correct ({matched_keys}/{total_keys} fields verified). Mismatches: {'; '.join(mismatch_details)}",
                explanation=explanation,
            )

        return ValidationResult(
            is_correct=False,
            points_earned=0.0,
            max_points=max_points,
            feedback=f"Subnet boundaries incorrect. {'; '.join(mismatch_details)}",
            explanation=explanation,
        )

    # Single subnet property check (e.g. broadcast or network)
    student_val = str(submitted_answer or "").strip()
    target_property = rule.get("target_property", "network_address")
    expected_val = str(rule.get("expected_value", rule.get(target_property, ""))).strip()

    if student_val.lower() == expected_val.lower():
        return ValidationResult(
            is_correct=True,
            points_earned=max_points,
            max_points=max_points,
            feedback=f"Correct {target_property.replace('_', ' ')}: {student_val}!",
            explanation=explanation,
        )

    return ValidationResult(
        is_correct=False,
        points_earned=0.0,
        max_points=max_points,
        feedback=rule.get("incorrect_feedback", f"'{student_val}' is not the correct {target_property.replace('_', ' ')}."),
        explanation=explanation,
    )


def validate_port(
    submitted_answer: Any,
    rule: dict[str, Any],
    max_points: float = 10.0,
) -> ValidationResult:
    """Validate TCP/UDP port number (1-65535)."""
    raw_port = str(submitted_answer or "").strip()
    explanation = rule.get("explanation")

    try:
        port_num = int(raw_port)
    except ValueError:
        return ValidationResult(
            is_correct=False,
            points_earned=0.0,
            max_points=max_points,
            feedback=f"'{raw_port}' is not a valid integer port number.",
            explanation=explanation,
        )

    if not (1 <= port_num <= 65535):
        return ValidationResult(
            is_correct=False,
            points_earned=0.0,
            max_points=max_points,
            feedback=f"Port {port_num} is outside the valid 16-bit range (1 to 65535).",
            explanation=explanation,
        )

    expected_ports = rule.get("expected_ports")
    if expected_ports:
        exp_list = [int(p) for p in expected_ports]
        if port_num in exp_list:
            return ValidationResult(
                is_correct=True,
                points_earned=max_points,
                max_points=max_points,
                feedback=f"Port {port_num} matches a valid service port!",
                explanation=explanation,
            )
        return ValidationResult(
            is_correct=False,
            points_earned=0.0,
            max_points=max_points,
            feedback=rule.get("incorrect_feedback", f"Port {port_num} does not match the expected protocol service."),
            explanation=explanation,
        )

    expected_port = int(rule.get("expected_port", rule.get("correct_answer", 0)))
    if port_num == expected_port:
        return ValidationResult(
            is_correct=True,
            points_earned=max_points,
            max_points=max_points,
            feedback=f"Correct port {port_num} identified!",
            explanation=explanation,
        )

    return ValidationResult(
        is_correct=False,
        points_earned=0.0,
        max_points=max_points,
        feedback=rule.get("incorrect_feedback", f"Port {port_num} is incorrect. Expected port {expected_port}."),
        explanation=explanation,
    )


def validate_lab_answer(
    validation_type: str,
    submitted_answer: Any,
    answer_data: str | dict[str, Any],
    points: int = 10,
) -> ValidationResult:
    """
    Central dispatcher for validating lab submissions across supported question types.
    """
    rule = _parse_answer_data(answer_data)
    vtype = str(validation_type).upper().strip()

    if vtype == "SINGLE_CHOICE":
        return validate_single_choice(submitted_answer, rule, max_points=float(points))
    elif vtype == "MULTIPLE_CHOICE":
        return validate_multiple_choice(submitted_answer, rule, max_points=float(points))
    elif vtype in ("TEXT", "SHORT_ANSWER"):
        return validate_text(submitted_answer, rule, max_points=float(points))
    elif vtype == "NUMERICAL":
        return validate_numerical(submitted_answer, rule, max_points=float(points))
    elif vtype == "IP_ADDRESS":
        return validate_ip_address(submitted_answer, rule, max_points=float(points))
    elif vtype == "CIDR":
        return validate_cidr(submitted_answer, rule, max_points=float(points))
    elif vtype in ("SUBNET", "SUBNETTING"):
        return validate_subnet(submitted_answer, rule, max_points=float(points))
    elif vtype == "PORT":
        return validate_port(submitted_answer, rule, max_points=float(points))
    else:
        # Fallback to text comparison
        return validate_text(submitted_answer, rule, max_points=float(points))


def shield_answer_data_for_student(
    validation_type: str,
    raw_answer_data: str | dict[str, Any],
) -> dict[str, Any]:
    """
    Sanitize answer data to present client-side input requirements without
    exposing secret answer keys, correct choices, or target values.
    """
    data = _parse_answer_data(raw_answer_data)
    vtype = str(validation_type).upper().strip()

    safe: dict[str, Any] = {
        "validation_type": vtype,
        "input_type": data.get("input_type", vtype.lower()),
        "placeholder": data.get("placeholder", ""),
        "label": data.get("label", "Your Observation / Answer"),
        "helper_text": data.get("helper_text", ""),
    }

    # For choices, expose options without 'is_correct' or answer markings
    if vtype in ("SINGLE_CHOICE", "MULTIPLE_CHOICE"):
        options = data.get("options", [])
        safe["options"] = [
            {
                "id": opt.get("id", idx) if isinstance(opt, dict) else idx,
                "text": (
                    opt.get("text", opt.get("option_text", str(opt)))
                    if isinstance(opt, dict)
                    else str(opt)
                ),
            }
            for idx, opt in enumerate(options, start=1)
        ]

    # For structured subnet input
    if vtype in ("SUBNET", "SUBNETTING") and "fields" in data:
        safe["fields"] = data["fields"]

    return safe
