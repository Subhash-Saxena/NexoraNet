# NexoraNet Production Security & Architectural Hardening Guide

> **Tagline**: *"Learn. Simulate. Analyze. Defend."*  
> **Status**: Step 21 Production Hardened

This document outlines the security architecture, authentication hardening, threat model mitigations, and simulation boundary invariants implemented for production-ready deployment of NexoraNet.

---

## 1. Architectural Threat Model & Security Invariants

NexoraNet is a cybersecurity educational platform designed to teach defensive networking, SOC operations, SIEM analysis, threat intelligence, and digital forensics. Because it handles synthetic threat telemetry and allows students to inspect simulated attacks, the system adheres strictly to the **Simulation Sandbox Invariant**:

```
+-------------------------------------------------------------------------+
|                  NEXORANET SECURITY SANDBOX BOUNDARY                    |
|                                                                         |
|  [Student Browser] ---> [FastAPI Backend] ---> [PostgreSQL / SQLite]     |
|                                |                                        |
|                                V                                        |
|                   Deterministic AST Parsers &                           |
|                   Synthetic Scenario Generators                         |
|                                |                                        |
|              X NO WAN Packet Transmissions                              |
|              X NO Arbitrary Code Execution (eval/exec)                  |
|              X NO Dynamic Shell Subprocesses                            |
|              X NO External SSRF / HTTP Outbound Fetching                |
|              X NO Real Operating System Modifications                   |
+-------------------------------------------------------------------------+
```

### Safety Principles Enforced:
1. **Zero Dynamic Code Execution**: The codebase contains zero calls to `eval()`, `exec()`, or `os.system()`. All query engines (PCAP filter, SIEM syntax, Threat Hunting QL) use safe, deterministic Abstract Syntax Tree (AST) tokenizers.
2. **Zero Outbound SSRF**: NexoraNet does not initiate outbound HTTP requests (`requests`, `httpx`, `urllib`) to user-supplied URLs. All threat intelligence feeds and PCAP samples are synthetically generated and deterministic.
3. **Strict Network Target Boundaries**: Synthetic ping and port scans are strictly validated via `is_authorized_lab_target()`. Only loopback addresses (`127.0.0.1`, `localhost`) and the designated virtual lab subnet (`10.99.0.0/16`) are accepted. Any attempt to target public IP addresses or unauthorized private infrastructure is blocked at the API boundary.

---

## 2. Authentication Hardening

NexoraNet uses a dual-layer authentication strategy that provides cryptographic security in production while preserving local development productivity.

### Cryptographic Password Hashing (PBKDF2-HMAC-SHA256)
- **Algorithm**: PBKDF2 with HMAC-SHA256.
- **Work Factor**: 100,000 iterations.
- **Salt**: 16 bytes of cryptographically secure random entropy (`secrets.token_hex(16)`).
- **Serialization Format**: `pbkdf2:sha256:100000$<salt_hex>$<hash_hex>`
- **Constant-Time Verification**: Password verification uses `secrets.compare_digest` to prevent side-channel timing attacks.

### Stateless JWT Bearer Authentication
- **Algorithm**: HMAC-SHA256 (`HS256`).
- **Signature Key**: `JWT_SECRET_KEY` (or fallback to `SECRET_KEY`).
- **Standard Claims**:
  - `sub`: User ID (primary key integer).
  - `role`: Role string (`STUDENT`, `INSTRUCTOR`, `ADMIN`).
  - `iat`: Timestamp of issuance.
  - `exp`: Timestamp of expiration (`ACCESS_TOKEN_EXPIRE_MINUTES`).
  - `jti`: Cryptographically random 12-byte token identifier to defend against replay attacks.
- **Generic Error Responses**: Both unknown usernames and incorrect passwords return an identical HTTP 401 error: `"Invalid username or password."`. This completely eliminates user enumeration vulnerabilities.

### Development Fallback Gating
In `development` and `testing` environments, API endpoints allow the existing dev header fallback (`X-User-Role: ADMIN`, `X-User-Id`) or default student fallback so automated test suites and local frontends operate seamlessly without manual auth token management.  
In `production` (`ENVIRONMENT=production`), **valid Bearer JWT tokens are strictly required**. Any unauthenticated or malformed request is rejected immediately with HTTP 401 Unauthorized.

---

## 3. Role-Based Access Control (RBAC) & IDOR Mitigation

### Server-Side Role Enforcement
Authorization is enforced on the server at every endpoint dependency:
- `CurrentUser`: Resolves the active user identity.
- `AdminUser`: Enforces `current_user.role == UserRole.ADMIN` (HTTP 403 Forbidden otherwise).
- `StaffUser`: Enforces `current_user.role in (UserRole.ADMIN, UserRole.INSTRUCTOR)`.

### Insecure Direct Object Reference (IDOR) Protection
Protected student assets (such as private portfolios, lab attempt histories, and challenge notes) utilize `verify_resource_ownership(resource_owner_id, current_user)`. Students can only view and mutate their own records; cross-tenant access is blocked with HTTP 403 Forbidden unless the caller holds Instructor or Administrator privileges.

---

## 4. Brute Force Mitigation & Rate Limiting

NexoraNet incorporates a thread-safe sliding-window rate limiter (`InMemoryRateLimiter`) applied to sensitive endpoints:
- **Authentication Routes** (`/api/v1/auth/login`, `/api/v1/auth/register`): Enforces `RATE_LIMIT_LOGIN_PER_MINUTE` (default: 10 requests per minute per IP).
- **CTF Flag Submissions** (`/api/v1/challenges/{id}/submit`): Enforces `RATE_LIMIT_FLAG_PER_MINUTE` (default: 30 attempts per minute per IP) to mitigate brute-forcing of flags.
- **HTTP 429 Response**: When the limit is exceeded, the API responds with HTTP 429 Too Many Requests and a `Retry-After: <seconds>` header.

---

## 5. Defense-in-Depth HTTP Security Headers

Every HTTP response produced by the application includes strict defense-in-depth security headers via `SecurityHeadersMiddleware`:

| Header | Production Value | Purpose |
| :--- | :--- | :--- |
| `X-Content-Type-Options` | `nosniff` | Prevents MIME-type sniffing |
| `X-Frame-Options` | `DENY` | Eliminates Clickjacking attacks |
| `Referrer-Policy` | `strict-origin-when-cross-origin` | Protects privacy on outbound navigation |
| `Permissions-Policy` | `geolocation=(), camera=(), microphone=(), payment=()` | Disables sensitive browser hardware APIs |
| `Content-Security-Policy` | `default-src 'self'; ...` | Restricts asset loading sources |
| `Strict-Transport-Security` | `max-age=31536000; includeSubDomains` | Enforces HTTPS connections (production only) |

---

## 6. Fail-Fast Production Startup Validation

To prevent accidental deployments with insecure development defaults, the application validates configuration parameters during startup (`validate_production_configuration`):

When `ENVIRONMENT=production`:
1. `SECRET_KEY` cannot be the development default, cannot contain `"dev"` or `"changeme"`, and must be at least 32 characters in length.
2. `DATABASE_URL` cannot use SQLite; a production RDBMS like PostgreSQL is required.
3. `DEBUG` must be set to `False`.
4. `CORS_ORIGINS` cannot contain wildcards (`*`) or `localhost` addresses.

If any invariant fails, the application aborts startup immediately with a descriptive error before serving any network traffic.
