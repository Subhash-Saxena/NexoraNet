import ipaddress
import re
from typing import Any

from app.models.enums import (
    CognitiveLevel,
    DifficultyLevel,
    QuestionStatus,
    QuestionType,
)


class QuestionValidationError(ValueError):
    """Custom exception raised when question bank items fail validation."""

    def __init__(self, message: str, code: str | None = None, errors: list[str] | None = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.errors = errors or [message]


def validate_question_structure(
    question_text: str,
    question_type: QuestionType,
    difficulty: DifficultyLevel,
    points: int,
    explanation: str,
    options: list[dict[str, Any]],
) -> None:
    """Backwards-compatible helper for testing question structure."""
    if points <= 0:
        raise QuestionValidationError("Question points must be a positive integer.")
    if not explanation or not explanation.strip():
        raise QuestionValidationError("An authoritative explanation must be provided.")
    if question_type == QuestionType.TRUE_FALSE and len(options) != 2:
        raise QuestionValidationError("TRUE_FALSE questions must contain exactly 2 options.")
    if not options or len(options) < 2:
        raise QuestionValidationError("Question must contain at least 2 options.")
    correct_count = sum(1 for o in options if o.get("is_correct") is True)
    if question_type in (QuestionType.SINGLE_CHOICE, QuestionType.TRUE_FALSE) and correct_count != 1:
        raise QuestionValidationError(f"{question_type.value} must have exactly 1 correct option, found {correct_count}.")


class QuestionValidator:
    """
    Robust validator for question bank items.
    Enforces taxonomic consistency, distractor integrity, duplicate detection,
    and programmatic mathematical/subnetting verification.
    """

    @staticmethod
    def normalize_text(text: str) -> str:
        """
        Normalize text for duplicate detection:
        - Lowercase
        - Strip punctuation
        - Collapse whitespace
        """
        if not text:
            return ""
        # Lowercase
        lowered = text.lower()
        # Remove markdown symbols and punctuation except alphanumerics
        cleaned = re.sub(r"[^a-z0-9\s]", " ", lowered)
        # Collapse multiple whitespace
        return re.sub(r"\s+", " ", cleaned).strip()

    @staticmethod
    def sanitize_content(text: str) -> str:
        """
        Guard against malicious HTML/XSS inside question content.
        Disallows script tags, javascript: URIs, and dangerous onload/onerror attributes.
        """
        if not text:
            return ""
        # Reject explicit script tags
        if re.search(r"<\s*script[^>]*>", text, re.IGNORECASE):
            raise ValueError("Dangerous script tag detected in question text or explanation.")
        # Reject javascript: protocol in links or attributes
        if re.search(r"javascript\s*:", text, re.IGNORECASE):
            raise ValueError("Dangerous javascript: URI detected in question content.")
        # Reject common event handler injections
        if re.search(r"\bon\w+\s*=", text, re.IGNORECASE):
            raise ValueError("Dangerous inline event handler detected in question content.")
        return text

    @classmethod
    def validate_question_dict(
        cls,
        q_data: dict[str, Any],
        valid_topic_slugs: set[str] | None = None,
        valid_topic_ids: set[int] | None = None,
    ) -> list[str]:
        """
        Validate a question dictionary (e.g. from JSON import or API payload).
        Returns a list of error strings (empty if valid).
        """
        errors: list[str] = []
        code = q_data.get("code")
        question_text = q_data.get("question_text")

        # 1. Basic text checks
        if not question_text or not isinstance(question_text, str) or len(question_text.strip()) < 5:
            errors.append("question_text must be a non-empty string with at least 5 characters.")
        else:
            try:
                cls.sanitize_content(question_text)
            except ValueError as e:
                errors.append(f"question_text sanitization error: {e}")

        # 2. Code format
        if code is not None and (not isinstance(code, str) or not re.match(r"^[A-Z0-9\-_]{3,64}$", code)):
            errors.append(f"Invalid code '{code}'. Must be alphanumeric with hyphens/underscores (3-64 chars).")

        # 3. Topic validation
        topic_slug = q_data.get("topic_slug")
        topic_id = q_data.get("topic_id")
        if topic_id is None and not topic_slug:
            errors.append("Question must specify either 'topic_slug' or 'topic_id'.")
        if topic_slug and valid_topic_slugs is not None and topic_slug not in valid_topic_slugs:
            errors.append(f"topic_slug '{topic_slug}' does not match any recognized curriculum topic.")
        if topic_id and valid_topic_ids is not None and topic_id not in valid_topic_ids:
            errors.append(f"topic_id {topic_id} does not exist in curriculum topics.")

        # 4. Difficulty validation
        diff_val = q_data.get("difficulty")
        if not diff_val:
            errors.append("difficulty is required.")
        else:
            try:
                DifficultyLevel(str(diff_val).upper())
            except ValueError:
                errors.append(f"Invalid difficulty '{diff_val}'. Must be BEGINNER, INTERMEDIATE, or ADVANCED.")

        # 5. Cognitive Level validation
        cog_val = q_data.get("cognitive_level", "UNDERSTAND")
        try:
            CognitiveLevel(str(cog_val).upper())
        except ValueError:
            errors.append(f"Invalid cognitive_level '{cog_val}'. Must be REMEMBER, UNDERSTAND, APPLY, or ANALYZE.")

        # 6. Question Type validation
        qt_val = q_data.get("question_type", "SINGLE_CHOICE")
        try:
            parsed_qt = QuestionType(str(qt_val).upper())
        except ValueError:
            errors.append(f"Invalid question_type '{qt_val}'.")
            parsed_qt = None

        # 7. Status validation
        status_val = q_data.get("status", "PUBLISHED")
        try:
            parsed_status = QuestionStatus(str(status_val).upper())
        except ValueError:
            errors.append(f"Invalid status '{status_val}'.")
            parsed_status = QuestionStatus.PUBLISHED

        # 8. Explanation validation for published questions
        explanation = q_data.get("explanation", "")
        if parsed_status == QuestionStatus.PUBLISHED:
            if not explanation or not isinstance(explanation, str) or len(explanation.strip()) < 8:
                errors.append("Published questions must provide a substantive explanation (at least 8 characters).")
            else:
                try:
                    cls.sanitize_content(explanation)
                except ValueError as e:
                    errors.append(f"explanation sanitization error: {e}")

        # 9. Points & Time
        points = q_data.get("points", 1)
        if not isinstance(points, int) or points <= 0:
            errors.append(f"points must be a positive integer, got {points}.")

        est_sec = q_data.get("estimated_seconds", 60)
        if not isinstance(est_sec, int) or est_sec <= 0:
            errors.append(f"estimated_seconds must be a positive integer, got {est_sec}.")

        # 10. Options validation
        options = q_data.get("options", [])
        if parsed_qt in (
            QuestionType.SINGLE_CHOICE,
            QuestionType.MULTIPLE_CHOICE,
            QuestionType.TRUE_FALSE,
            QuestionType.SUBNETTING,
            QuestionType.SCENARIO,
            QuestionType.PACKET_ANALYSIS,
        ):
            if not isinstance(options, list) or len(options) < 2:
                errors.append(f"Question type '{parsed_qt}' requires at least 2 options.")
            else:
                correct_count = sum(1 for opt in options if opt.get("is_correct") is True)
                option_texts = [str(opt.get("option_text", "")).strip().lower() for opt in options]

                # Check duplicate options within question
                if len(option_texts) != len(set(option_texts)):
                    errors.append("Question contains duplicate option choices.")

                # Check for empty option text
                if any(len(txt) == 0 for txt in option_texts):
                    errors.append("Option text cannot be empty.")

                # Choice type rules
                if parsed_qt == QuestionType.SINGLE_CHOICE and correct_count != 1:
                    errors.append(f"SINGLE_CHOICE question must have exactly 1 correct option, found {correct_count}.")
                elif parsed_qt == QuestionType.MULTIPLE_CHOICE and correct_count < 1:
                    errors.append("MULTIPLE_CHOICE question must have at least 1 correct option.")
                elif parsed_qt == QuestionType.TRUE_FALSE:
                    if len(options) != 2:
                        errors.append(f"TRUE_FALSE question must have exactly 2 options, found {len(options)}.")
                    if correct_count != 1:
                        errors.append(f"TRUE_FALSE question must have exactly 1 correct option, found {correct_count}.")

        return errors

    @staticmethod
    def verify_subnet_calculation(
        cidr_str: str,
        property_name: str,
        expected_value: str | int,
    ) -> tuple[bool, str]:
        """
        Programmatically verify IPv4 subnet calculation.
        Supports: 'network_address', 'broadcast_address', 'netmask',
        'usable_hosts', 'first_host', 'last_host', 'total_hosts'.
        """
        try:
            net = ipaddress.IPv4Network(cidr_str, strict=False)
        except (ValueError, ipaddress.AddressValueError, ipaddress.NetmaskValueError) as e:
            return False, f"Invalid CIDR '{cidr_str}': {e}"

        actual: Any
        if property_name in ("network_address", "network"):
            actual = str(net.network_address)
        elif property_name in ("broadcast_address", "broadcast"):
            actual = str(net.broadcast_address)
        elif property_name in ("netmask", "subnet_mask"):
            actual = str(net.netmask)
        elif property_name in ("usable_hosts", "num_hosts"):
            # For /31 and /32, usable hosts is 0 or 2 depending on RFC 3021; standard net.num_addresses - 2
            actual = max(0, net.num_addresses - 2) if net.prefixlen < 31 else net.num_addresses
        elif property_name in ("first_host", "first_usable"):
            if net.prefixlen >= 31:
                actual = str(net.network_address)
            else:
                actual = str(net.network_address + 1)
        elif property_name in ("last_host", "last_usable"):
            if net.prefixlen >= 31:
                actual = str(net.broadcast_address)
            else:
                actual = str(net.broadcast_address - 1)
        else:
            return False, f"Unknown subnet property '{property_name}'."

        is_match = str(actual).strip() == str(expected_value).strip()
        message = f"Property '{property_name}' for {cidr_str}: expected '{expected_value}', calculated '{actual}'."
        return is_match, message

    @classmethod
    def check_duplicate_questions(
        cls, questions: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """
        Scan a list of question dictionaries and return duplicate groupings.
        Detects:
        - Duplicate stable codes
        - Identical normalized question text
        - Same question text with identical options
        """
        seen_codes: dict[str, str] = {}
        seen_normalized_text: dict[str, str] = {}
        duplicates: list[dict[str, Any]] = []

        for q in questions:
            code = q.get("code") or "NO_CODE"
            text = q.get("question_text", "")
            norm_text = cls.normalize_text(text)

            # Check duplicate code
            if code != "NO_CODE":
                if code in seen_codes:
                    duplicates.append({
                        "type": "DUPLICATE_CODE",
                        "code": code,
                        "conflict_with": seen_codes[code],
                        "question_text": text[:80],
                    })
                else:
                    seen_codes[code] = text[:80]

            # Check duplicate normalized text
            if norm_text:
                if norm_text in seen_normalized_text:
                    duplicates.append({
                        "type": "DUPLICATE_TEXT",
                        "code": code,
                        "conflict_with_code": seen_normalized_text[norm_text],
                        "question_text": text[:80],
                    })
                else:
                    seen_normalized_text[norm_text] = code

        return duplicates
