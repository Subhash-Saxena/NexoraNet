"""IOC Normalization and Validation Service.

Provides secure canonicalization, defanging neutralization, and format validation
for IP addresses, domains, URLs, file hashes, and email addresses.
Strictly treats all indicators as passive text data without execution or network lookups.
"""

import ipaddress
import re
from typing import Any, ClassVar
from urllib.parse import urlsplit, urlunsplit

from app.models.enums import HashType, IndicatorType


class NormalizationService:
    """Canonicalizes and validates Indicators of Compromise (IOC)."""

    MAX_VALUE_LENGTH = 2048

    # Hex length maps for hashes
    HASH_LENGTHS: ClassVar[dict[int, HashType]] = {
        32: HashType.MD5,
        40: HashType.SHA1,
        64: HashType.SHA256,
        128: HashType.SHA512,
    }

    @classmethod
    def strip_defanging(cls, raw_val: str) -> str:
        """Neutralize common defensive defanging conventions safely.

        Examples:
        - hxxp:// or hxxps:// -> http:// or https://
        - [.] or (dot) -> .
        - [:] -> :
        - [at] or (@) -> @
        """
        val = raw_val.strip()

        # Defanged protocols
        if val.lower().startswith("hxxp://"):
            val = "http://" + val[7:]
        elif val.lower().startswith("hxxps://"):
            val = "https://" + val[8:]
        elif val.lower().startswith("fxp://"):
            val = "ftp://" + val[6:]

        # Defanged dots, colons, at-signs
        val = val.replace("[.]", ".").replace("(.)", ".").replace("{\\.}", ".")
        val = val.replace("[:]", ":").replace("(:)", ":")
        val = val.replace("[at]", "@").replace("(@)", "@").replace("[AT]", "@")
        return val.strip()

    @classmethod
    def detect_type(cls, raw_val: str) -> tuple[IndicatorType, HashType | None]:
        """Infer the indicator type from the raw value format."""
        cleaned = cls.strip_defanging(raw_val)

        # 1. IP Address
        try:
            ipaddress.ip_address(cleaned)
            return IndicatorType.IP_ADDRESS, None
        except ValueError:
            pass

        # 2. File Hash (hexadecimal check)
        hex_match = re.fullmatch(r"[a-fA-F0-9]+", cleaned)
        if hex_match and len(cleaned) in cls.HASH_LENGTHS:
            return IndicatorType.FILE_HASH, cls.HASH_LENGTHS[len(cleaned)]

        # 3. URL
        if cleaned.lower().startswith(("http://", "https://", "ftp://")):
            return IndicatorType.URL, None

        # 4. Email Address
        if "@" in cleaned and re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", cleaned):
            return IndicatorType.EMAIL_ADDRESS, None

        # 5. Domain / FQDN
        domain_pattern = r"^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$"
        if re.fullmatch(domain_pattern, cleaned):
            return IndicatorType.DOMAIN, None

        # Default fallback if contains dot
        if "." in cleaned and "/" not in cleaned and " " not in cleaned:
            return IndicatorType.DOMAIN, None

        return IndicatorType.DOMAIN, None

    @classmethod
    def normalize_ip(cls, val: str) -> str:
        """Normalize IPv4 or IPv6 into canonical format."""
        cleaned = cls.strip_defanging(val)
        try:
            ip_obj = ipaddress.ip_address(cleaned)
            return ip_obj.compressed.lower()
        except ValueError as e:
            raise ValueError(f"Invalid IP address format: {val}") from e

    @classmethod
    def normalize_domain(cls, val: str) -> str:
        """Normalize domain name to lowercase, trimmed, trailing-dot-free representation."""
        cleaned = cls.strip_defanging(val).lower()
        # Remove protocol prefix if accidentally included
        if "://" in cleaned:
            cleaned = cleaned.split("://", 1)[1]
        # Remove trailing path or port if accidentally pasted
        if "/" in cleaned:
            cleaned = cleaned.split("/", 1)[0]
        if ":" in cleaned:
            cleaned = cleaned.split(":", 1)[0]
        cleaned = cleaned.rstrip(".")

        if not cleaned or len(cleaned) > 253 or " " in cleaned:
            raise ValueError(f"Invalid domain name: {val}")

        # IDNA encoding validation
        try:
            ascii_domain = cleaned.encode("idna").decode("ascii")
            return ascii_domain
        except Exception as e:
            raise ValueError(f"Domain IDNA normalization failed: {val}") from e

    @classmethod
    def normalize_url(cls, val: str) -> str:
        """Safely normalize URL, redacting any embedded credentials and lowercasing host."""
        cleaned = cls.strip_defanging(val)
        if not (cleaned.lower().startswith("http://") or cleaned.lower().startswith("https://") or cleaned.lower().startswith("ftp://")):
            cleaned = "http://" + cleaned

        try:
            parts = urlsplit(cleaned)
            scheme = parts.scheme.lower()
            netloc = parts.netloc

            # Redact credentials if user:pass@host is provided
            if "@" in netloc:
                _, host_part = netloc.split("@", 1)
                netloc = host_part

            netloc = netloc.lower()

            # Normalize standard ports
            if scheme == "http" and netloc.endswith(":80"):
                netloc = netloc[:-3]
            elif scheme == "https" and netloc.endswith(":443"):
                netloc = netloc[:-4]

            path = parts.path or "/"
            # Reconstruct normalized URL
            normalized = urlunsplit((scheme, netloc, path, parts.query, ""))
            return normalized
        except Exception as e:
            raise ValueError(f"Invalid URL structure: {val}") from e

    @classmethod
    def normalize_hash(cls, val: str) -> tuple[str, HashType]:
        """Normalize cryptographic hash to lowercase hex and determine algorithm."""
        cleaned = cls.strip_defanging(val).lower().strip()
        length = len(cleaned)

        if not re.fullmatch(r"[a-f0-9]+", cleaned):
            raise ValueError(f"Invalid hexadecimal hash string: {val}")

        if length not in cls.HASH_LENGTHS:
            raise ValueError(f"Hash length {length} does not match supported algorithms (MD5=32, SHA1=40, SHA256=64, SHA512=128).")

        return cleaned, cls.HASH_LENGTHS[length]

    @classmethod
    def normalize_email(cls, val: str) -> str:
        """Normalize email address to lowercase user@domain format."""
        cleaned = cls.strip_defanging(val).lower().strip()
        if "@" not in cleaned:
            raise ValueError(f"Invalid email address: {val}")
        user_part, domain_part = cleaned.split("@", 1)
        domain_normalized = cls.normalize_domain(domain_part)
        return f"{user_part}@{domain_normalized}"

    @classmethod
    def normalize(cls, raw_val: str, expected_type: IndicatorType | None = None) -> dict[str, Any]:
        """Canonicalize and validate an indicator of compromise.

        Returns:
            dict containing:
            - indicator_type: IndicatorType
            - hash_type: HashType | None
            - value: original raw input
            - normalized_value: canonicalized string
            - display_value: safe string for UI presentation
        """
        if not raw_val or not isinstance(raw_val, str):
            raise ValueError("Indicator value must be a non-empty string.")

        if len(raw_val) > cls.MAX_VALUE_LENGTH:
            raise ValueError(f"Indicator value exceeds maximum permitted length ({cls.MAX_VALUE_LENGTH} characters).")

        # Neutralize control characters
        cleaned = re.sub(r"[\x00-\x1f\x7f]", "", raw_val).strip()
        if not cleaned:
            raise ValueError("Indicator contains only control characters or whitespace.")

        inferred_type, _ = cls.detect_type(cleaned)
        target_type = expected_type or inferred_type

        norm_val: str
        hash_type: HashType | None = None

        if target_type == IndicatorType.IP_ADDRESS:
            norm_val = cls.normalize_ip(cleaned)
            disp_val = norm_val
        elif target_type == IndicatorType.DOMAIN:
            norm_val = cls.normalize_domain(cleaned)
            disp_val = norm_val
        elif target_type == IndicatorType.URL:
            norm_val = cls.normalize_url(cleaned)
            disp_val = norm_val
        elif target_type == IndicatorType.FILE_HASH:
            norm_val, hash_type = cls.normalize_hash(cleaned)
            disp_val = norm_val
        elif target_type == IndicatorType.EMAIL_ADDRESS:
            norm_val = cls.normalize_email(cleaned)
            disp_val = norm_val
        else:
            norm_val = cleaned.lower()
            disp_val = cleaned

        return {
            "indicator_type": target_type.value if hasattr(target_type, "value") else str(target_type),
            "hash_type": hash_type.value if hash_type and hasattr(hash_type, "value") else (str(hash_type) if hash_type else None),
            "value": raw_val.strip(),
            "normalized_value": norm_val,
            "display_value": disp_val,
        }


normalization_service = NormalizationService()
