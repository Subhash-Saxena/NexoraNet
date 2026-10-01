# NexoraNet — Post-Deployment Verification & Smoke Test Guide

## 1. Overview
This runbook defines the live operational verification procedure following deployment of the **NexoraNet** application to public cloud infrastructure.

---

## 2. Phase-by-Phase Smoke Test Checklist

### 2.1 Health & Readiness Probes
Run these requests against your live backend domain:
```bash
# 1. Operational Liveness Probe (Expect HTTP 200 and {"status": "ok"})
curl -i https://<BACKEND-URL>/health
curl -i https://<BACKEND-URL>/api/health

# 2. Database Connectivity Readiness Probe (Expect HTTP 200 and {"status": "ready", "database": "connected"})
curl -i https://<BACKEND-URL>/ready
curl -i https://<BACKEND-URL>/api/ready
```

### 2.2 Security Headers Audit
Verify that the response headers contain all defense-in-depth security policies:
```bash
curl -I https://<BACKEND-URL>/api/health
```
Verify the output contains:
- `Strict-Transport-Security: max-age=31536000; includeSubDomains`
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Permissions-Policy: geolocation=(), camera=(), microphone=(), payment=()`
- Absence of `Server` banner disclosing framework internals.

### 2.3 Live Authentication & Token Revocation
```bash
# 1. Register a student user
curl -X POST https://<BACKEND-URL>/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "smoke_cadet", "email": "smoke_cadet@nexora.test", "password": "SecurePassword2026!"}'

# 2. Login and extract JWT
# Response returns {"access_token": "ey...", "token_type": "bearer"}

# 3. Access /auth/me with Bearer token
curl -H "Authorization: Bearer <TOKEN>" https://<BACKEND-URL>/api/v1/auth/me

# 4. Logout and revoke token
curl -X POST -H "Authorization: Bearer <TOKEN>" https://<BACKEND-URL>/api/v1/auth/logout

# 5. Confirm revoked token yields HTTP 401 Unauthorized
curl -i -H "Authorization: Bearer <TOKEN>" https://<BACKEND-URL>/api/v1/auth/me
# Expected: HTTP 401 Unauthorized
```

### 2.4 Multi-Tenant IDOR Guardrail
- Register user A and user B.
- Create a project under User A: `POST /api/v1/portfolio/projects`.
- Attempt to mutate User A's project using User B's token: `PUT /api/v1/portfolio/projects/{UserA_Project_ID}`.
- Expected response: `HTTP 404 Not Found` or `HTTP 403 Forbidden`.

### 2.5 Single-Page Application (SPA) Direct Route Navigation
In the browser, load and refresh the following deep URLs on the frontend domain:
- `https://<FRONTEND-URL>/`
- `https://<FRONTEND-URL>/dashboard`
- `https://<FRONTEND-URL>/learning`
- `https://<FRONTEND-URL>/labs`
- `https://<FRONTEND-URL>/soc`
- `https://<FRONTEND-URL>/challenges`
- `https://<FRONTEND-URL>/portfolio`

Verify that refreshing nested routes renders the client application correctly without displaying a 404 page.
