"""Step 21 Automated Security & Production Hardening Test Suite.

Validates:
1. PBKDF2-HMAC-SHA256 password hashing, salting, and verification.
2. JWT generation, expiration enforcement, tampering detection, and decoding.
3. Authentication endpoints (/auth/register, /auth/login, /auth/me).
4. Brute-force rate limiting and HTTP 429 handling.
5. Security response headers (CSP, HSTS, X-Frame-Options, X-Content-Type-Options).
6. Health and readiness probes (/health, /ready, /api/health, /api/ready).
7. Production configuration fail-fast validator.
8. Role-Based Access Control (RBAC) with real JWT tokens.
9. Synthetic simulation network boundary enforcement.
"""

from datetime import timedelta

import pytest
from app.core.config import Settings
from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    is_authorized_lab_target,
    rate_limiter,
    verify_password,
)
from fastapi.testclient import TestClient

# ==============================================================================
# 1. CRYPTOGRAPHIC PASSWORD HASHING
# ==============================================================================

def test_password_hashing_and_salting() -> None:
    """Verify passwords are salted and hashed using PBKDF2-HMAC-SHA256."""
    pw = "SuperSecurePassword123!"
    hash1 = hash_password(pw)
    hash2 = hash_password(pw)

    assert hash1.startswith("pbkdf2:sha256:100000$")
    assert hash2.startswith("pbkdf2:sha256:100000$")
    # Distinct random salts must produce distinct hashes for identical inputs
    assert hash1 != hash2

    # Verification success
    assert verify_password(pw, hash1) is True
    assert verify_password(pw, hash2) is True

    # Verification failure on wrong password
    assert verify_password("WrongPassword999!", hash1) is False
    assert verify_password("", hash1) is False


def test_development_seed_password_verification() -> None:
    """Verify development seed accounts authenticate in dev/test environment."""
    assert verify_password("student123", "argon2id$v=19$m=65536,t=3,p=4$dev_student_hash") is True
    assert verify_password("cadet123", "argon2id$v=19$m=65536,t=3,p=4$dev_student_hash") is True
    assert verify_password("admin123", "argon2id$v=19$m=65536,t=3,p=4$admin_dev_hash") is True
    assert verify_password("wrongpass", "argon2id$v=19$m=65536,t=3,p=4$admin_dev_hash") is False


# ==============================================================================
# 2. JWT TOKEN LIFECYCLE & SIGNATURE INTEGRITY
# ==============================================================================

def test_jwt_issuance_and_decoding() -> None:
    """Verify JWT token payload contains standard claims and verifies correctly."""
    token = create_access_token(
        subject=42,
        role="ADMIN",
        expires_delta=timedelta(minutes=15),
        extra_claims={"email": "admin@nexoranet.internal"},
    )
    assert isinstance(token, str)

    payload = decode_access_token(token)
    assert payload["sub"] == "42"
    assert payload["role"] == "ADMIN"
    assert payload["email"] == "admin@nexoranet.internal"
    assert "jti" in payload
    assert "exp" in payload


def test_jwt_expiration_handling() -> None:
    """Verify expired JWT tokens raise HTTP 401 Unauthorized."""
    from fastapi import HTTPException

    # Token with negative lifespan (already expired)
    expired_token = create_access_token(
        subject=10,
        role="STUDENT",
        expires_delta=timedelta(seconds=-10),
    )

    with pytest.raises(HTTPException) as exc_info:
        decode_access_token(expired_token)
    assert exc_info.value.status_code == 401
    assert "expired" in exc_info.value.detail.lower()


def test_jwt_tampered_token_rejection() -> None:
    """Verify forged or tampered JWT signatures raise HTTP 401."""
    from fastapi import HTTPException

    valid_token = create_access_token(subject=1, role="STUDENT")
    # Tamper with the signature bytes at the end
    tampered = valid_token[:-4] + "ffff"

    with pytest.raises(HTTPException) as exc_info:
        decode_access_token(tampered)
    assert exc_info.value.status_code == 401


# ==============================================================================
# 3. AUTHENTICATION ENDPOINTS (REGISTER, LOGIN, ME)
# ==============================================================================

def test_auth_registration_and_login(client: TestClient) -> None:
    """Verify user registration, password hashing, and subsequent login flow."""
    import secrets

    random_suffix = secrets.token_hex(4)
    username = f"cadet_{random_suffix}"
    email = f"cadet_{random_suffix}@test.internal"
    password = "Sec0ndPassword456!"

    # 1. Register new student account
    reg_res = client.post(
        "/api/v1/auth/register",
        json={
            "username": username,
            "email": email,
            "password": password,
            "display_name": "Test Cadet",
        },
    )
    assert reg_res.status_code == 201
    reg_data = reg_res.json()
    assert "access_token" in reg_data
    assert reg_data["user"]["username"] == username
    assert reg_data["user"]["role"] == "STUDENT"
    assert "password_hash" not in reg_data["user"]  # Zero password hash leakage

    # 2. Reject duplicate registration
    dup_res = client.post(
        "/api/v1/auth/register",
        json={
            "username": username,
            "email": email,
            "password": password,
        },
    )
    assert dup_res.status_code == 400
    assert "already exists" in dup_res.json()["detail"].lower()

    # 3. Successful login with registered credentials
    login_res = client.post(
        "/api/v1/auth/login",
        json={
            "username": username,
            "password": password,
        },
    )
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]

    # 4. Access /me endpoint with issued Bearer token
    me_res = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_res.status_code == 200
    me_data = me_res.json()
    assert me_data["username"] == username
    assert me_data["role"] == "STUDENT"


def test_auth_login_generic_error_prevents_enumeration(client: TestClient) -> None:
    """Verify unknown usernames and invalid passwords yield identical generic 401 errors."""
    # Unknown user
    res1 = client.post(
        "/api/v1/auth/login",
        json={"username": "nonexistent_ghost_user_12345", "password": "AnyPassword123!"},
    )
    assert res1.status_code == 401
    assert res1.json()["detail"] == "Invalid username or password."

    # Known user, wrong password
    res2 = client.post(
        "/api/v1/auth/login",
        json={"username": "student_dev", "password": "WrongPassword999!"},
    )
    assert res2.status_code == 401
    assert res2.json()["detail"] == "Invalid username or password."


# ==============================================================================
# 4. RATE LIMITING ENGINE
# ==============================================================================

def test_rate_limiter_sliding_window() -> None:
    """Verify rate limiter blocks requests exceeding the configured threshold."""
    rate_limiter.reset()
    key = "test_rate_limit_key"

    # Allow up to 3 requests
    for _ in range(3):
        allowed, remaining, retry_after = rate_limiter.check(key, max_requests=3, window_seconds=10)
        assert allowed is True

    # 4th request must be rejected
    allowed, remaining, retry_after = rate_limiter.check(key, max_requests=3, window_seconds=10)
    assert allowed is False
    assert remaining == 0
    assert retry_after > 0


# ==============================================================================
# 5. SECURITY RESPONSE HEADERS
# ==============================================================================

def test_security_headers_present(client: TestClient) -> None:
    """Verify security headers are applied to HTTP responses."""
    res = client.get("/")
    assert res.status_code == 200

    assert res.headers.get("X-Content-Type-Options") == "nosniff"
    assert res.headers.get("X-Frame-Options") == "DENY"
    assert res.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
    assert "geolocation=()" in res.headers.get("Permissions-Policy", "")
    assert "default-src 'self'" in res.headers.get("Content-Security-Policy", "")


# ==============================================================================
# 6. HEALTH & READINESS PROBES
# ==============================================================================

def test_health_and_readiness_probes(client: TestClient) -> None:
    """Verify /health and /ready return expected service status."""
    # Root health probe
    res_health_root = client.get("/health")
    assert res_health_root.status_code == 200
    assert res_health_root.json()["status"] == "ok"
    assert res_health_root.json()["service"] == "NexoraNet API"

    # API health probe
    res_health_api = client.get("/api/health")
    assert res_health_api.status_code == 200
    assert res_health_api.json()["status"] == "ok"

    # Root ready probe
    res_ready_root = client.get("/ready")
    assert res_ready_root.status_code == 200
    assert res_ready_root.json()["status"] == "ready"
    assert res_ready_root.json()["database"] == "connected"

    # API ready probe
    res_ready_api = client.get("/api/ready")
    assert res_ready_api.status_code == 200
    assert res_ready_api.json()["status"] == "ready"
    assert res_ready_api.json()["database"] == "connected"


# ==============================================================================
# 7. PRODUCTION CONFIGURATION FAIL-FAST VALIDATOR
# ==============================================================================

def test_production_validator_rejects_insecure_defaults() -> None:
    """Verify production mode rejects default dev secret, sqlite, debug=True, and wildcard CORS."""
    # 1. Default dev secret in production -> must raise ValueError
    with pytest.raises(ValueError) as exc:
        Settings(
            ENVIRONMENT="production",
            SECRET_KEY="nexoranet-dev-secret-key-change-in-production-only",
            DATABASE_URL="postgresql://user:pass@localhost:5432/db",
            DEBUG=False,
            CORS_ORIGINS=["https://nexoranet.example.com"],
        )
    assert "SECRET_KEY" in str(exc.value)

    # 2. SQLite in production -> must raise ValueError
    with pytest.raises(ValueError) as exc:
        Settings(
            ENVIRONMENT="production",
            SECRET_KEY="a" * 40,
            DATABASE_URL="sqlite:///./test.db",
            DEBUG=False,
            CORS_ORIGINS=["https://nexoranet.example.com"],
        )
    assert "SQLite is prohibited" in str(exc.value)

    # 3. DEBUG=True in production -> must raise ValueError
    with pytest.raises(ValueError) as exc:
        Settings(
            ENVIRONMENT="production",
            SECRET_KEY="a" * 40,
            DATABASE_URL="postgresql://user:pass@localhost:5432/db",
            DEBUG=True,
            CORS_ORIGINS=["https://nexoranet.example.com"],
        )
    assert "DEBUG must be set to False" in str(exc.value)

    # 4. Wildcard CORS in production -> must raise ValueError
    with pytest.raises(ValueError) as exc:
        Settings(
            ENVIRONMENT="production",
            SECRET_KEY="a" * 40,
            DATABASE_URL="postgresql://user:pass@localhost:5432/db",
            DEBUG=False,
            CORS_ORIGINS=["*"],
        )
    assert "Wildcard '*'" in str(exc.value)

    # 5. Fully compliant production configuration -> must succeed
    valid_prod_settings = Settings(
        ENVIRONMENT="production",
        SECRET_KEY="a_strong_cryptographic_production_secret_key_64_characters_long!",
        DATABASE_URL="postgresql://user:pass@localhost:5432/prod_db",
        DEBUG=False,
        CORS_ORIGINS=["https://nexoranet.example.com", "https://app.nexoranet.internal"],
    )
    assert valid_prod_settings.ENVIRONMENT == "production"
    assert valid_prod_settings.DEBUG is False


# ==============================================================================
# 8. ROLE-BASED ACCESS CONTROL (RBAC) WITH JWT
# ==============================================================================

def test_rbac_admin_endpoint_with_jwt(client: TestClient) -> None:
    """Verify admin endpoints allow admin JWT tokens and reject student JWT tokens."""
    # Obtain or construct admin and student tokens
    student_token = create_access_token(subject=1, role="STUDENT")

    # In dev/test, find admin user id
    login_admin = client.post(
        "/api/v1/auth/login",
        json={"username": "admin_dev", "password": "admin123"},
    )
    assert login_admin.status_code == 200
    admin_token = login_admin.json()["access_token"]

    # 1. Student JWT hitting admin dashboard -> 403 Forbidden
    res_student = client.get(
        "/api/v1/admin/dashboard",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert res_student.status_code == 403

    # 2. Admin JWT hitting admin dashboard -> 200 OK
    res_admin = client.get(
        "/api/v1/admin/dashboard",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert res_admin.status_code == 200
    assert "total_users" in res_admin.json()


# ==============================================================================
# 9. SIMULATION SAFETY BOUNDARY INVARIANTS
# ==============================================================================

def test_simulation_guardrail_target_filtering() -> None:
    """Verify is_authorized_lab_target blocks public internet targets and permits loopback/lab subnet."""
    # Permitted targets
    assert is_authorized_lab_target("localhost") is True
    assert is_authorized_lab_target("127.0.0.1") is True
    assert is_authorized_lab_target("10.99.1.5") is True
    assert is_authorized_lab_target("target.lab.internal") is True

    # Strictly forbidden targets (external WAN / unauthorized)
    assert is_authorized_lab_target("8.8.8.8") is False
    assert is_authorized_lab_target("1.1.1.1") is False
    assert is_authorized_lab_target("google.com") is False
    assert is_authorized_lab_target("192.168.1.1") is False
    assert is_authorized_lab_target("172.16.0.1") is False
