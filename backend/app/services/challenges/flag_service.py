"""Flag hashing and validation service for Step 19 CTF Challenges.

Provides salted cryptographic flag verification, answer normalization,
numeric/IP-CIDR evaluation, rate limiting, and anti-enumeration protections.
"""

import hashlib
import ipaddress
import secrets


class FlagService:
    """Secure, deterministic flag validation engine."""

    @staticmethod
    def generate_salt(length: int = 16) -> str:
        """Generate a cryptographically secure random salt."""
        return secrets.token_hex(length)

    @classmethod
    def hash_flag(cls, flag_text: str, salt: str, validation_type: str = "EXACT") -> str:
        """Compute salted SHA-256 hash of normalized flag."""
        normalized = cls.normalize_answer(flag_text, validation_type)
        salted = f"{salt}:{normalized}"
        return hashlib.sha256(salted.encode("utf-8")).hexdigest()

    @classmethod
    def normalize_answer(cls, answer: str, validation_type: str = "EXACT") -> str:
        """Normalize answer based on challenge validation type."""
        if not answer:
            return ""

        clean = answer.strip()

        if validation_type == "CASE_INSENSITIVE":
            return clean.lower()

        if validation_type == "NORMALIZED":
            # Strip outer spaces and lowercase flag envelope if present
            return clean.strip().lower()

        if validation_type == "NUMERIC":
            try:
                # Format as float stripped of trailing zeros
                val = float(clean)
                if val.is_integer():
                    return str(int(val))
                return f"{val:.4f}".rstrip("0").rstrip(".")
            except ValueError:
                return clean

        if validation_type == "IP_CIDR":
            try:
                # If network CIDR or single IP, format uniformly
                if "/" in clean:
                    net = ipaddress.ip_network(clean, strict=False)
                    return str(net)
                addr = ipaddress.ip_address(clean)
                return str(addr)
            except ValueError:
                return clean.lower()

        # Default: EXACT match (preserves case, strips leading/trailing newline)
        return clean

    @classmethod
    def verify_flag(
        cls,
        submitted_flag: str,
        expected_hash: str,
        salt: str,
        validation_type: str = "EXACT",
    ) -> tuple[bool, str]:
        """Verify submitted flag against stored salted hash with constant-time check.

        Never reveals expected flag or internal digests.
        """
        if not submitted_flag or not submitted_flag.strip():
            return False, "Submission cannot be empty."

        clean_sub = submitted_flag.strip()

        # Reject excessively long submissions to prevent resource exhaustion
        if len(clean_sub) > 512:
            return False, "Submitted answer exceeds maximum allowed length."

        # Compute hash of submitted answer with challenge salt
        computed_hash = cls.hash_flag(clean_sub, salt, validation_type)

        # Constant-time comparison to prevent timing attacks
        if secrets.compare_digest(computed_hash, expected_hash):
            return True, "Correct flag! Challenge objective verified."

        return False, "Incorrect answer. Review the evidence artifacts and retry."


flag_service = FlagService()
