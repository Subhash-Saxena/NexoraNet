# NexoraNet — Administrative Operations & Governance

**“Learn. Simulate. Analyze. Defend.”**

## 1. Role-Based Access Control (RBAC)
NexoraNet implements strict server-side authorization:
- `UserRole.STUDENT` — Default learner role. Access to administrative endpoints returns `HTTP 403 Forbidden`.
- `UserRole.INSTRUCTOR` — Authorized to view content, manage curriculum, and inspect cohort progress.
- `UserRole.ADMIN` — Full governance, content state machine transitions, and audit inspection.

## 2. Server-Side Enforcement
The dependency `require_admin_user` in `backend/app/api/deps.py` resolves roles via authenticated tokens and request headers (`X-User-Role`, `X-User-Id`). If the calling context does not evaluate to `ADMIN`, an immediate `HTTP 403 Forbidden` response is returned.

## 3. Administrative Audit Ledger
All administrative actions produce immutable audit entries stored in the `admin_audit_logs` table:
- Actor ID & Actor Role
- Action Name (e.g. `PUBLISH_CONTENT`, `UNPUBLISH_CONTENT`, `ARCHIVE_CONTENT`)
- Target Entity Type & Target ID
- Detailed Rationale & Context
- UTC Creation Timestamp
