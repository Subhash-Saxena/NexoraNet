# NexoraNet Production Security Verification Checklist

This checklist confirms verification of all security controls and hardening measures for NexoraNet Step 21.

---

## 1. Authentication & Credential Security
- [x] Passwords hashed using PBKDF2-HMAC-SHA256 with 100,000 iterations.
- [x] Cryptographically random 16-byte salt generated per password (`secrets.token_hex(16)`).
- [x] Constant-time password comparison via `secrets.compare_digest` to defeat timing attacks.
- [x] Password complexity requirements enforced on registration (min 8 characters, non-trivial).
- [x] Zero password hashes exposed in responses (`UserOut` schema excludes `password_hash`).
- [x] Generic error messages on login failure (`"Invalid username or password."`) preventing username enumeration.
- [x] Brute-force rate limiting enforced on `/api/v1/auth/login` (HTTP 429 upon threshold breach).
- [x] Rate limiting enforced on user registration `/api/v1/auth/register`.
- [x] Rate limiting enforced on CTF flag submissions `/api/v1/challenges/{id}/submit`.

## 2. Token & Session Management (JWT)
- [x] Stateless JWT issued using HMAC-SHA256 (`HS256`).
- [x] Separate `JWT_SECRET_KEY` support with fallback to `SECRET_KEY`.
- [x] Token payload includes `sub`, `role`, `iat`, `exp`, and unique `jti`.
- [x] Expiration strictly checked (`ACCESS_TOKEN_EXPIRE_MINUTES`).
- [x] Expired tokens rejected with HTTP 401 Unauthorized.
- [x] Tampered signatures and corrupted tokens rejected with HTTP 401.

## 3. Authorization & Access Control (RBAC)
- [x] Server-side authorization enforced via FastAPI dependencies (`CurrentUser`, `AdminUser`, `StaffUser`).
- [x] Administrative endpoints (`/api/v1/admin/*`) strictly reject non-admin users with HTTP 403 Forbidden.
- [x] Instructor endpoints require `INSTRUCTOR` or `ADMIN` role.
- [x] IDOR protection enforced via `verify_resource_ownership()` for personal student records.
- [x] In `production`, unauthenticated access is strictly blocked (development fallback header disabled).

## 4. Educational Simulation Guardrails (Safety Invariants)
- [x] Zero calls to `eval()`, `exec()`, or dynamic code runners in backend codebase.
- [x] Zero dynamic OS command execution or subprocess invocations.
- [x] Zero outbound HTTP requests to user-supplied targets (zero SSRF risk).
- [x] Network target validation (`is_authorized_lab_target`) blocks public IPs (`8.8.8.8`, WAN hosts).
- [x] Network target validation permits only loopback and designated internal lab subnet (`10.99.0.0/16`).
- [x] Deterministic AST query parsers employed for PCAP, SIEM, and Threat Hunting.
- [x] All challenges and attack telemetry remain 100% synthetic and safe.

## 5. API & HTTP Transport Security
- [x] `X-Content-Type-Options: nosniff` header applied to all responses.
- [x] `X-Frame-Options: DENY` header applied to eliminate clickjacking.
- [x] `Referrer-Policy: strict-origin-when-cross-origin` applied.
- [x] `Permissions-Policy: geolocation=(), camera=(), microphone=(), payment=()` applied.
- [x] Defense-in-depth `Content-Security-Policy` header applied.
- [x] `Strict-Transport-Security: max-age=31536000; includeSubDomains` applied in production.
- [x] CORS origins strictly restrict allowed domains without wildcard `*` in production.

## 6. Database Security & Connection Pooling
- [x] PostgreSQL support fully tested with `psycopg2-binary`.
- [x] Connection pooling configured (`pool_size`, `max_overflow`, `pool_timeout`, `pool_recycle`).
- [x] Pre-ping enabled (`pool_pre_ping=True`) to handle dropped connections safely.
- [x] Automatic normalization of cloud host URLs (`postgres://` -> `postgresql://`).
- [x] Parameterized SQL queries via SQLAlchemy 2.0 ORM (zero raw SQL injection points).

## 7. Container & Docker Hardening
- [x] Multi-stage backend build reduces attack surface and discards build tools.
- [x] Backend runs under unprivileged non-root user `appuser` (UID 10001).
- [x] Multi-stage frontend build serves static files via minimal Nginx Alpine.
- [x] Container healthcheck probes defined for backend, frontend, and database.
- [x] Uvicorn configured for multi-worker execution without auto-reload in production.

## 8. Health, Readiness & Observability
- [x] Fast liveness probe `/health` and `/api/health` available.
- [x] Database connectivity readiness probe `/ready` and `/api/ready` available.
- [x] Fail-fast startup validator halts boot if insecure configurations detected in production.
- [x] Error responses sanitize stack traces and internal secrets in non-debug mode.
