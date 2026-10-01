"""Core Security Utilities for NexoraNet:

Authentication, Authorization, Rate Limiting, and Simulation Guardrails.
"""

import hashlib
import ipaddress
import re
import secrets
import threading
import time
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from fastapi import HTTPException, status

from app.core.config import get_settings

settings = get_settings()

# ==============================================================================
# 1. SIMULATION & NETWORK LAB GUARD RAILS
# ==============================================================================

# Explicit loopback targets
LOOPBACK_HOSTS: set[str] = {"localhost", "127.0.0.1", "::1"}

# Regex for valid hostnames and domain labels
HOSTNAME_REGEX = re.compile(
    r"^([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,6}$"
)


def is_authorized_lab_target(
    target: str, allowed_subnet_cidr: str = "10.99.0.0/16"
) -> bool:
    """Validate that an IP or hostname target is restricted strictly to:

    1. Localhost / Loopback
    2. Designated internal lab subnet (e.g., 10.99.0.0/16)

    CRITICAL SECURITY GUARD RAIL:
    NexoraNet will never permit arbitrary network scanning or execution against
    external/WAN targets or unauthorized private infrastructure.
    """
    clean_target = target.strip().lower()

    if clean_target in LOOPBACK_HOSTS:
        return True

    # Try parsing as IP address
    try:
        ip = ipaddress.ip_address(clean_target)
        if ip.is_loopback:
            return True

        # Check if target falls within designated safe virtual lab network
        lab_subnet = ipaddress.ip_network(allowed_subnet_cidr, strict=False)
        return ip in lab_subnet
    except ValueError:
        pass

    # If it is a virtual lab domain name (e.g., lab-target-1.local, host.internal)
    return (
        clean_target.endswith(".lab.internal") or clean_target == "host.docker.internal"
    )


# ==============================================================================
# 2. CRYPTOGRAPHIC PASSWORD HASHING (PBKDF2-HMAC-SHA256)
# ==============================================================================

PBKDF2_ITERATIONS = 100_000
HASH_PREFIX = "pbkdf2:sha256"


def hash_password(password: str) -> str:
    """Hash a password using PBKDF2-HMAC-SHA256 with a cryptographically secure random salt."""
    salt = secrets.token_hex(16)
    derived = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        PBKDF2_ITERATIONS,
    )
    return f"{HASH_PREFIX}:{PBKDF2_ITERATIONS}${salt}${derived.hex()}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hashed value using constant-time comparison.

    Also handles seed test users in development environments.
    """
    if not hashed_password or not plain_password:
        return False

    if hashed_password.startswith(f"{HASH_PREFIX}:"):
        try:
            prefix_and_iter, salt, expected_hex = hashed_password.split("$")
            iterations = int(prefix_and_iter.split(":")[2])
            derived = hashlib.pbkdf2_hmac(
                "sha256",
                plain_password.encode("utf-8"),
                salt.encode("utf-8"),
                iterations,
            )
            return secrets.compare_digest(derived.hex(), expected_hex)
        except (ValueError, TypeError, IndexError):
            return False

    # Development fallback for seed placeholder accounts (e.g. cadet_student, student_dev, admin_dev)
    if settings.ENVIRONMENT in ("development", "testing"):
        dev_map = {
            "dev_student_hash": {"student123", "cadet123", "password123", "dev_student_hash"},
            "dummy_hash_placeholder_step2": {"cadet123", "password123"},
            "admin_dev_hash": {"admin123", "password123", "admin_dev_hash"},
            "instructor_dev_hash": {"instructor123", "password123", "instructor_dev_hash"},
        }
        for token, valid_pw_set in dev_map.items():
            if token in hashed_password and plain_password in valid_pw_set:
                return True

    return False


# ==============================================================================
# 3. JSON WEB TOKENS (JWT) FOR STATELESS RBAC AUTHENTICATION
# ==============================================================================


def create_access_token(
    subject: str | int,
    role: str,
    expires_delta: timedelta | None = None,
    extra_claims: dict[str, Any] | None = None,
) -> str:
    """Generate a signed JWT token containing subject, role, issuance, and expiration."""
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    payload: dict[str, Any] = {
        "sub": str(subject),
        "role": str(role).upper(),
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
        "jti": secrets.token_hex(12),
    }

    if extra_claims:
        payload.update(extra_claims)

    return jwt.encode(
        payload,
        settings.effective_jwt_secret,
        algorithm=settings.JWT_ALGORITHM,
    )


def decode_access_token(token: str) -> dict[str, Any]:
    """Decode and validate a JWT access token.

    Raises HTTP 401 if invalid or expired.
    """
    try:
        payload = jwt.decode(
            token,
            settings.effective_jwt_secret,
            algorithms=[settings.JWT_ALGORITHM],
        )
        jti = payload.get("jti")
        if token_revocation_registry.is_revoked(jti):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication token has been revoked. Please log in again.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token has expired. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ==============================================================================
# 4. IN-MEMORY THREAD-SAFE RATE LIMITER
# ==============================================================================


class InMemoryRateLimiter:
    """Thread-safe sliding-window rate limiter for sensitive authentication & flag endpoints."""

    def __init__(self) -> None:
        self._history: dict[str, list[float]] = {}
        self._lock = threading.Lock()

    def check(
        self,
        key: str,
        max_requests: int,
        window_seconds: int = 60,
    ) -> tuple[bool, int, int]:
        """Check if an action is allowed for the given key.

        Returns: (is_allowed, remaining_requests, retry_after_seconds)
        """
        now = time.time()
        cutoff = now - window_seconds

        with self._lock:
            timestamps = self._history.get(key, [])
            # Prune timestamps older than the sliding window
            timestamps = [ts for ts in timestamps if ts > cutoff]

            if len(timestamps) >= max_requests:
                oldest = timestamps[0]
                retry_after = max(1, int(oldest + window_seconds - now))
                self._history[key] = timestamps
                return False, 0, retry_after

            timestamps.append(now)
            self._history[key] = timestamps
            remaining = max(0, max_requests - len(timestamps))
            return True, remaining, 0

    def reset(self) -> None:
        """Reset all rate limiter records (useful for test isolation)."""
        with self._lock:
            self._history.clear()


rate_limiter = InMemoryRateLimiter()


# ==============================================================================
# 5. SERVER-SIDE TOKEN REVOCATION REGISTRY (JTI BLOCKLIST)
# ==============================================================================


class TokenRevocationRegistry:
    """Thread-safe in-memory store for revoked JWT token identifiers (JTI).

    Automatically prunes entries once the token's original expiration time has passed.
    """

    def __init__(self) -> None:
        self._revoked: dict[str, float] = {}  # jti -> exp_timestamp
        self._lock = threading.Lock()

    def revoke(self, jti: str, exp: float) -> None:
        """Add a token identifier to the revocation registry."""
        with self._lock:
            self._prune_expired()
            self._revoked[jti] = float(exp)

    def is_revoked(self, jti: str | None) -> bool:
        """Check if a token identifier has been explicitly revoked."""
        if not jti:
            return False
        with self._lock:
            self._prune_expired()
            return jti in self._revoked

    def _prune_expired(self) -> None:
        """Remove entries whose expiration timestamp is in the past."""
        now = time.time()
        self._revoked = {jti: exp for jti, exp in self._revoked.items() if exp > now}

    def reset(self) -> None:
        """Reset registry (for test isolation)."""
        with self._lock:
            self._revoked.clear()


token_revocation_registry = TokenRevocationRegistry()
