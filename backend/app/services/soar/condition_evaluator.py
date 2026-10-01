"""Safe Whitelist-Based Condition Evaluator for SOAR Automation.

Strictly non-executable: evaluated entirely via pure Python comparison logic.
Zero eval(), zero exec(), zero dynamic code execution.
"""

from typing import Any, ClassVar


class SafeConditionEvaluator:
    """Restricted AST/Rule evaluator for automated playbook branching."""

    VALID_OPERATORS: ClassVar[set[str]] = {
        "equals",
        "eq",
        "==",
        "not_equals",
        "neq",
        "!=",
        "contains",
        "starts_with",
        "startswith",
        "ends_with",
        "endswith",
        "greater_than",
        "gt",
        ">",
        "less_than",
        "lt",
        "<",
        "greater_than_or_equal",
        "gte",
        ">=",
        "less_than_or_equal",
        "lte",
        "<=",
        "in",
        "not_in",
        "exists",
        "not_exists",
    }

    @classmethod
    def evaluate(cls, condition: dict[str, Any] | None, context: dict[str, Any]) -> bool:
        """Evaluate a condition dictionary against an execution context.

        Returns True if condition is empty/None (unconditional execution).
        """
        if not condition:
            return True

        # Grouping: "and"
        if "and" in condition:
            sub_conds = condition.get("and", [])
            if not isinstance(sub_conds, list):
                return False
            return all(cls.evaluate(sc, context) for sc in sub_conds)

        # Grouping: "or"
        if "or" in condition:
            sub_conds = condition.get("or", [])
            if not isinstance(sub_conds, list):
                return False
            return any(cls.evaluate(sc, context) for sc in sub_conds)

        # Single clause evaluation
        field = condition.get("field")
        op = str(condition.get("operator", "equals")).lower().strip()
        expected = condition.get("value")

        if not field:
            return False

        # Extract nested field values (e.g., "alert.severity" or "severity")
        actual = cls._get_field_value(field, context)

        return cls._compare(actual, op, expected)

    @classmethod
    def _get_field_value(cls, field_path: str, context: dict[str, Any]) -> Any:
        """Safely traverse dot-separated paths in context dictionary."""
        parts = field_path.split(".")
        current = context

        for part in parts:
            if isinstance(current, dict):
                current = current.get(part)
            else:
                return None
            if current is None:
                return None

        return current

    @classmethod
    def _compare(cls, actual: Any, operator: str, expected: Any) -> bool:
        """Execute strictly allowlisted comparison without dynamic code."""
        if operator in ("exists",):
            return actual is not None and actual != ""

        if operator in ("not_exists",):
            return actual is None or actual == ""

        # Handle None gracefully
        if actual is None:
            if operator in ("equals", "eq", "=="):
                return expected is None
            if operator in ("not_equals", "neq", "!="):
                return expected is not None
            return False

        # Normalize string values for case-insensitive matching
        if isinstance(actual, str) and isinstance(expected, str):
            actual_norm = actual.strip().lower()
            expected_norm = expected.strip().lower()
        else:
            actual_norm = actual
            expected_norm = expected

        if operator in ("equals", "eq", "=="):
            return actual_norm == expected_norm

        if operator in ("not_equals", "neq", "!="):
            return actual_norm != expected_norm

        if operator == "contains":
            if isinstance(actual, (list, tuple, set)):
                return expected in actual or (isinstance(expected, str) and any(str(x).lower() == expected.lower() for x in actual))
            return str(expected).lower() in str(actual).lower()

        if operator in ("starts_with", "startswith"):
            return str(actual).lower().startswith(str(expected).lower())

        if operator in ("ends_with", "endswith"):
            return str(actual).lower().endswith(str(expected).lower())

        # Numeric comparisons
        if operator in ("greater_than", "gt", ">"):
            try:
                return float(actual) > float(expected)
            except (ValueError, TypeError):
                return False

        if operator in ("less_than", "lt", "<"):
            try:
                return float(actual) < float(expected)
            except (ValueError, TypeError):
                return False

        if operator in ("greater_than_or_equal", "gte", ">="):
            try:
                return float(actual) >= float(expected)
            except (ValueError, TypeError):
                return False

        if operator in ("less_than_or_equal", "lte", "<="):
            try:
                return float(actual) <= float(expected)
            except (ValueError, TypeError):
                return False

        # Set membership
        if operator == "in":
            if isinstance(expected, (list, tuple, set)):
                return actual in expected or (isinstance(actual, str) and any(str(x).lower() == actual.lower() for x in expected))
            return str(actual).lower() in str(expected).lower()

        if operator == "not_in":
            if isinstance(expected, (list, tuple, set)):
                return not (actual in expected or (isinstance(actual, str) and any(str(x).lower() == actual.lower() for x in expected)))
            return str(actual).lower() not in str(expected).lower()

        return False
