# NexoraNet — Project Status & Roadmap

Platform Tagline: **"Learn. Simulate. Analyze. Defend."**

---

## Current Status: STEP 23 COMPLETED (PRODUCTION DEPLOYMENT READY)

### Completed in Step 23: Deployment Execution Preparation & Zero-Cost Cloud Orchestration

* **Centralized Frontend API Configuration**:
  * Created `frontend/src/services/apiConfig.ts` with `getApiBaseUrl()` dynamically resolving `VITE_API_URL` or `VITE_API_BASE_URL` with clean local proxy fallback.
  * Updated all 14 frontend service clients to consume the centralized configuration, enabling decoupling between frontend static host and backend API host.
* **SPA Routing Fallbacks & Production Static Assets**:
  * Configured `frontend/public/_redirects` (for Cloudflare Pages / Netlify) and `frontend/vercel.json` (for Vercel) guaranteeing clean SPA client-side routing on hard refreshes.
  * Production frontend build verified with `tsc -b && vite build` (zero errors, sub-second execution, assets in `frontend/dist`).
* **Zero-Cost Cloud Architecture & Deployment Runbooks**:
  * Authored `docs/deployment-runbook.md` detailing step-by-step provisioning on Neon / Supabase (PostgreSQL), Render / Railway (FastAPI Backend), and Cloudflare Pages (React Frontend).
  * Authored `docs/production-environment.md` with explicit variable reference, sensitive classification, and cryptographic secret generation commands.
  * Authored `docs/post-deployment-verification.md` with smoke test cURLs across all platform subsystems.
  * Authored `docs/rollback.md` outlining zero-downtime rollback and Alembic migration downgrade protocols.
* **Testing & Security Verification**:
  * Backend: 279/279 tests passing.
  * Frontend: 139/139 tests passing across 18 test suites.
  * Linters: Ruff (backend) clean, Oxlint (frontend) clean.
  * Alembic: Single linear migration head verified.
  * Git security: Verified `.env` and sensitive configurations are strictly excluded from git tracking.
* **Deployment Execution State**:
  * Declared **DEPLOYMENT BLOCKED** strictly per security rules requiring user authorization for external cloud provider access, repository push, and live database credentials. Ready for zero-friction user execution.

---

### Completed in Step 22: Final Integration + Security Audit + E2E QA + Regression Testing + Production Readiness

* **Server-Side Token Revocation & JTI Blocklist**:
  * Implemented stateful `TokenRevocationRegistry` in `backend/app/core/security.py` tracking invalidated JWT IDs (`jti`) with automated expired token pruning.
  * Created `POST /api/v1/auth/logout` endpoint in `backend/app/api/v1/endpoints/auth.py` that immediately revokes the active user's access token.
  * Hardened `decode_access_token` to verify JTI status against the blocklist, rejecting revoked sessions with `HTTP 401 Unauthorized`.
* **Alembic Database Head Verification & Postgres URL Normalization**:
  * Audited migration history confirming a single linear migration head (`a1b2c3d4e5f6 (head)`) with zero divergent heads.
  * Hardened `backend/alembic/env.py` to automatically normalize legacy `postgres://` URLs to `postgresql://`.
* **Core API Endpoint Hardening**:
  * Removed legacy `get_current_dev_user(db)` fallbacks across curriculum (`/topics`, `/lessons`, `/learning/progress`) and lab attempt routes.
  * All endpoints now strictly resolve identity via `current_user: CurrentUser` (`app.api.deps`). In `ENVIRONMENT=production`, missing authentication headers strictly yield `HTTP 401 Unauthorized`.
* **SOAR Condition Evaluator Hardening**:
  * Fixed AST clause handling in `backend/app/services/soar/condition_evaluator.py`: malformed clauses without valid operator fields evaluate safely to `False`.
* **Pydantic V2 Modernization**:
  * Modernized legacy inner `class Config:` declarations to `model_config = ConfigDict(from_attributes=True)` in `backend/app/schemas/soar.py` and `backend/app/schemas/soc_scenario.py`, eliminating Pydantic deprecation warnings.
* **Comprehensive Step 22 Security Audit Suite**:
  * Authored `backend/tests/test_step22_security_audit.py` covering: token revocation on logout, multi-user IDOR defense in portfolios, production rejection of dev passwords, XSS sanitization, dangerous URL scheme rejection (`javascript:`, `data:`), SSRF/cloud metadata blocking (`169.254.169.254`), SOAR AST evaluation, CTF flag secrecy, and simulation invariants.
* **Full End-to-End Student Journey Suite**:
  * Authored `backend/tests/test_e2e_student_journey.py` testing the complete realistic lifecycle across all platform domains:
    Register -> Login -> Me -> Curriculum -> Lessons -> Labs -> Simulator -> PCAP Analysis -> Detection Rules -> SOC Alerts -> Threat Intel -> Threat Hunting -> SIEM -> Endpoint Security -> Incidents -> MITRE ATT&CK -> SOAR Playbooks -> SOC Scenarios -> CTF Challenges -> Skill Matrix -> Recommendations -> Portfolio -> Logout -> Revocation check.
* **Verification & Testing Results**:
  * **Backend**: **279 passing Pytest tests (100%)** across 30 test modules.
  * **Backend Linter**: Ruff check clean (**0 errors**).
  * **Frontend**: **139 passing Vitest tests (100%)** across 18 test files.
  * **Frontend Linter**: Oxlint clean (**0 errors**).
  * **Frontend Production Build**: `tsc -b && vite build` succeeds cleanly in ~660ms.
* **Production Documentation Deliverables**:
  * Created `docs/final-security-audit.md`
  * Created `docs/end-to-end-testing.md`
  * Created `docs/production-readiness.md`
  * Created `docs/backup-restore.md`
  * Created `docs/deployment-runbook.md`

---

### Completed in Step 21: Production Security + Hardening + PostgreSQL Support + Deployment Preparation

* **Production Security & Secret Management**:
  * Implemented fail-fast production startup validation (`validate_production_configuration` in `backend/app/core/config.py`).
  * Enforces that in `ENVIRONMENT=production`, default development secrets, SQLite databases, `DEBUG=True`, and wildcard/localhost CORS are strictly prohibited at boot time.
  * Added dedicated `JWT_SECRET_KEY`, `ACCESS_TOKEN_EXPIRE_MINUTES`, and cryptographically secure entropy validation (minimum 32 characters).
* **Authentication & Authorization Hardening**:
  * Built PBKDF2-HMAC-SHA256 password hashing engine (`backend/app/core/security.py`) with 100,000 iterations, 16-byte random salts, and constant-time verification (`secrets.compare_digest`).
  * Implemented stateless JWT bearer token authentication (`HS256`, subject, role, expiration, and random `jti` claims).
  * Created public authentication endpoints (`POST /api/v1/auth/login`, `POST /api/v1/auth/register`, `GET /api/v1/auth/me`).
  * Enforces generic authentication failure responses (`"Invalid username or password."`) to eliminate username enumeration.
  * Hardened request dependencies (`backend/app/api/deps.py`): Bearer tokens strictly required in production; development header fallback (`X-User-Role`) strictly restricted to `ENVIRONMENT=development` and `testing`.
  * Enforced server-side IDOR protection (`verify_resource_ownership`) preventing students from viewing or mutating cross-tenant assets.
* **PostgreSQL Production Support & Connection Pooling**:
  * Added `psycopg2-binary>=2.9.9` and `pyjwt>=2.8.0` to `backend/requirements.txt`.
  * Configured robust SQLAlchemy 2.0 connection pooling in `backend/app/db/session.py` (`pool_size=10`, `max_overflow=20`, `pool_timeout=30`, `pool_recycle=300`, `pool_pre_ping=True`).
  * Added automated cloud URL normalization converting legacy `postgres://` URLs (Render, Railway, Neon) to `postgresql://`.
* **Brute Force Mitigation & Sliding-Window Rate Limiting**:
  * Implemented thread-safe in-memory sliding-window rate limiter (`InMemoryRateLimiter`).
  * Enforced rate limits on `/api/v1/auth/login`, `/api/v1/auth/register` (`RATE_LIMIT_LOGIN_PER_MINUTE`), and `/api/v1/challenges/{challenge_id}/submit` (`RATE_LIMIT_FLAG_PER_MINUTE`).
  * Standardized HTTP 429 Too Many Requests responses with compliant `Retry-After` header.
* **Defense-in-Depth HTTP Security Headers**:
  * Implemented `SecurityHeadersMiddleware` in `backend/app/main.py`.
  * Injects `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy: strict-origin-when-cross-origin`, `Permissions-Policy: geolocation=(), camera=(), microphone=(), payment=()`, and `Content-Security-Policy`.
  * Automatically injects `Strict-Transport-Security: max-age=31536000; includeSubDomains` in production environments.
* **Health & Readiness Observability Probes**:
  * Root and API liveness probes (`/health`, `/api/health`) returning operational status and service identity.
  * Root and API readiness probes (`/ready`, `/api/ready`) executing `SELECT 1` database checks with HTTP 503 error handling that sanitizes database connection strings and internal credentials.
* **Multi-Stage Production Docker Configuration**:
  * `docker/backend.prod.Dockerfile`: Multi-stage build with non-root user `appuser` (UID 10001), healthcheck probe, and multi-worker Uvicorn configuration without `--reload`.
  * `docker/frontend.prod.Dockerfile`: Multi-stage build compiling static assets with Node 22 Alpine and serving via minimal Nginx Alpine.
  * `docker/nginx.conf`: Custom Nginx configuration with gzip compression, security headers, SPA client routing, and immutable asset caching.
  * `docker-compose.prod.yml`: Production topology with PostgreSQL 16 container, persistent storage volumes, health checks, and service dependencies.
* **Comprehensive Documentation & Checklist**:
  * Created `docs/production-security.md` (threat model and hardening architecture).
  * Created `docs/environment.md` (configuration variable reference).
  * Created `docs/postgresql.md` (database setup, migrations, pooling, and backup).
  * Created `docs/docker-production.md` (container architecture and non-root execution).
  * Created `docs/deployment-preparation.md` (Step 21 deployment readiness and hosting options).
  * Created `docs/security-checklist.md` (50+ point verification checklist).
  * Updated `.env.example` with complete production guidance.
* **Verification & Testing**:
  * **Backend**: **267 passing Pytest tests (100%)** (`tests/test_security_hardening.py` + full regression suite).
  * **Backend Linter**: Ruff check passes with **0 errors**.
  * **Frontend**: **139 passing Vitest tests (100%)** (all 18 test files).
  * **Frontend Linter**: Oxlint passes with **0 errors**.
  * **Frontend Production Build**: `tsc -b && vite build` succeeds cleanly.

---

### Completed in Step 20: Analytics + Skill Assessment + Reports + Portfolio + Admin

* **Student Analytics & Learning Intelligence Engine**:
  * Built authoritative progress telemetry service (`backend/app/services/analytics/student_analytics_service.py`).
  * Aggregates multi-source evidence across all 19 prior modules: Lessons, Labs, Mock Tests, PCAPs, Detection Engine, Mini-SOC, Threat Intelligence, Threat Hunting, SIEM, Endpoint Security, Incident Response, SOAR playbooks, SOC scenarios, and CTF challenges.
  * Calculates learning time, completion counts, current streak, recent activity timeline feed, and 14-day rolling performance trends.
  * Strictly adheres to non-judgmental educational phrasing: *"Recent results suggest additional practice with subnetting may be useful."*
* **Continuous Skill Assessment Matrix (28 Core Proficiencies)**:
  * Implemented `SkillAssessmentService` evaluating 28 granular cybersecurity proficiencies across 8 domains: Networking, Packet Analysis, Detection Engineering, SOC Analysis, Threat Intelligence & Hunting, SIEM & Logs, Endpoint Security, and Incident Response.
  * **Recency Weighting Formula**: Evaluates evidence using 50% recent performance + 30% historical performance + 20% practical simulation performance.
  * **Explainable Confidence Framework**: Decouples confidence (`HIGH`, `MEDIUM`, `LOW`) from accuracy percentage, reflecting evidence volume and recency rather than permanent abilities.
* **Pedagogical Recommendation & Achievement System**:
  * `RecommendationEngineService`: Identifies confidence gaps and generates actionable study recommendations with neutral pedagogical rationales and direct workbench action links.
  * `AchievementService`: Evaluates and awards 10 documented educational achievements (`FIRST_LESSON`, `LAB_PIONEER`, `EXAM_READY`, `PACKET_DISSECTOR`, `TRIAGE_SPECIALIST`, `THREAT_HUNTER`, `SIEM_OPERATOR`, `ENDPOINT_DEFENDER`, `INCIDENT_RESPONDER`, `AUTOMATION_ENGINEER`).
* **Educational Assessment Reports & Completion Certificates**:
  * `ReportService`: Generates archival assessment reports with report codes (`REP-`), executive summary, knowledge evidence, practical evidence, demonstrated strengths, growth areas, and printable layout.
  * Read-only educational certificate verification endpoint (`NX-` codes) with tamper-evident disclaimer confirming internal simulation milestones.
* **Student Portfolio & Educational Showcase**:
  * `PortfolioService`: Full portfolio management with 3-tier visibility controls (`PRIVATE` by default, `UNLISTED`, `PUBLIC`).
  * Strict URL sanitization blocking dangerous schemes (`javascript:`, `data:`, `vbscript:`) with `HTTP 400 Bad Request`.
  * Public portfolio view strictly prevents leakage of student emails, password hashes, internal notes, or question/challenge answers.
  * Full JSON export functionality (`/api/v1/portfolio/export/json`).
* **Administration & Content Lifecycle Governance**:
  * Server-side authorization in `deps.py` enforcing `UserRole.ADMIN` (`require_admin_user`) and returning `HTTP 403 Forbidden` for unauthorized student requests.
  * `AdminContentService`: Content catalog management with state machine (`DRAFT` ↔ `REVIEW` → `PUBLISHED` → `ARCHIVED`).
  * Validation guards preventing publication of incomplete courses, modules without topics, topics without lessons, or labs without steps.
  * Immutable `AdminAuditLog` recording actor, role, action, target type, target id, details, and UTC timestamp.
* **Database & Migration (`a1b2c3d4e5f6`)**:
  * Alembic migration `2026_10_01_1030-a1b2c3d4e5f6_step_20_analytics_skills_reports_.py` applied cleanly.
  * 12 models in `backend/app/models/analytics.py`: `Skill`, `SkillAssessment`, `LearningActivity`, `StudentRecommendation`, `Achievement`, `UserAchievement`, `Portfolio`, `PortfolioProject`, `PortfolioItem`, `AssessmentReport`, `EducationalCertificate`, `AdminAuditLog`, `ContentVersion`.
  * Seeded 28 skills, 10 achievements, and admin/instructor dev users in `backend/nexoranet.db`.
* **Frontend UI & Workbenches (`frontend/src/`)**:
  * `SkillCatalogPage.tsx` (`/progress/skills`): 28-skill matrix with confidence indicators, domain filter tabs, search, and detail modal.
  * `AssessmentReportPage.tsx` (`/progress/assessment`): Printable comprehensive educational progress report with disclaimers and multi-source evidence breakdown.
  * `PortfolioPage.tsx` (`/portfolio`): Student profile, visibility toggle (`PRIVATE`/`UNLISTED`/`PUBLIC`), project manager, URL validation, and JSON export.
  * `PublicPortfolioPage.tsx` (`/portfolio/public/:publicSlug`): Public view honoring visibility, verified certificates, and zero private data leakage.
  * `AdminDashboardPage.tsx` (`/admin`): Metrics, catalog counts, and development role switcher.
  * `AdminContentPage.tsx` (`/admin/content`): Content table, filters, publish/unpublish/archive actions with validation error alerts.
  * `AdminAuditPage.tsx` (`/admin/audit`): Filterable immutable audit ledger.
  * Navigation: Added `Skill Assessment`, `Assessment Report`, `Showcase Portfolio`, and `Admin Operations` in `Sidebar.tsx`.
  * Updated `ProgressPage.tsx` with quick links to skills, report, and portfolio.
  * Stylesheet: `frontend/src/components/analytics/analytics.css`.
* **Verification & Testing**:
  * **Backend**: **254 passing Pytest tests (100%)** (`tests/test_analytics_and_admin.py` + full suite).
  * **Backend Linter**: Ruff check passes with **0 errors**.
  * **Frontend**: **139 passing Vitest tests (100%)** (`src/test/AnalyticsAndAdmin.test.tsx` + full suite across 18 test files).
  * **Frontend Linter & Build**: `tsc -b && vite build` clean with **0 errors**, Oxlint passes with **0 errors**.
  * **Documentation**: `docs/analytics.md`, `docs/skill-assessment.md`, `docs/recommendations.md`, `docs/portfolio.md`, `docs/admin.md`, `docs/content-management.md`, `docs/privacy-analytics.md`.

---

* **Safe Offline SOAR Simulation Engine**:
  * Built an authoritative offline educational SOAR simulation engine (`backend/app/services/soar/`).
  * Full educational workflow:
    `ALERT → DETECTION → AUTOMATION RULE → PLAYBOOK → DECISION → SIMULATED ACTION → VERIFICATION → INCIDENT/CASE → EVIDENCE → MITRE → LESSONS LEARNED`.
  * **Strict Offline Boundaries**: Non-destructive simulation invariant strictly enforced: `simulation_only = True` on 100% of actions and entities. Zero live host alteration, zero shell/PowerShell/Bash execution, zero dynamic code execution (`eval`/`exec`), zero external network queries.
  * **Whitelist Condition Engine**: Declarative condition evaluator supporting 13 operators (`eq`, `ne`, `gt`, `gte`, `lt`, `lte`, `contains`, `not_contains`, `in`, `not_in`, `regex_match`, `is_empty`, `is_not_empty`) with dot-notation field resolution and compound `and`/`or` Boolean logic.
  * **Human-in-the-Loop Analyst Approval Gates**: High-risk containment and eradication steps automatically pause in `WAITING_APPROVAL` status until an analyst reviews telemetry and authorizes or rejects the action, logged immutably to `AutomationAuditLog`.
  * **Idempotency & Failure Handling**: Idempotency key deduplication per entity/playbook, maximum 2 retries on transient errors, and declarative failure strategies (`STOP` vs `CONTINUE`).
  * **8 Seeded Official Educational Playbooks**:
    * `SOAR-PB-001`: Phishing Email Triage & Safe Quarantine
    * `SOAR-PB-002`: Malware Endpoint Host Containment
    * `SOAR-PB-003`: Ransomware Rapid Containment & Snapshot
    * `SOAR-PB-004`: Credential Access & User Account Revocation
    * `SOAR-PB-005`: Data Exfiltration Perimeter IP Block
    * `SOAR-PB-006`: Suspicious Geo-Login Investigation & MFA Reset
    * `SOAR-PB-007`: Lateral Movement Isolation & Evidence Capture
    * `SOAR-PB-008`: Automated Threat Intelligence IOC Enrichment
  * **Curriculum & Question Bank Expansion**: 15 new learning lessons in `soar-automation` topic and 10 new Step 18 Question Bank items (`SOAR` & `SOC_SCENARIO`).

* **Advanced SOC Scenario Engine**:
  * 9-stage guided investigation room player:
    `INITIAL SIGNAL → EVIDENCE SELECTION → CORRELATION → HYPOTHESIS → VALIDATION → MITRE MAPPING → RESPONSE DECISION → OUTCOME → LESSONS LEARNED`.
  * **28 Seeded Synthetic Scenarios**:
    * Beginner (5): `SCEN-001` through `SCEN-005`
    * Intermediate (8): `SCEN-006` through `SCEN-013`
    * Advanced (10): `SCEN-014` through `SCEN-023`
    * Expert (5): `SCEN-024` through `SCEN-028`
  * **Transparent 7-Factor Rubric Scoring**:
    Signal analysis (15%), Evidence selection (20%), Correlation (15%), Hypothesis (20%), MITRE mapping (15%), Response actions (15%), and Progressive hint penalties.
  * **Progressive Hint System**: Contextual hints with transparent score deduction warnings (-5.0 pts per hint).

* **Relational Schema & Alembic Migration (`ca2d83e1cdbb`)**:
  * Models added in `backend/app/models/soar.py` and `soc_scenario.py`:
    * `AutomationPlaybook`, `AutomationStep`, `PlaybookExecution`, `ExecutionStepLog`, `AutomationAuditLog`.
    * `SocScenario`, `ScenarioAttempt`.
  * Enums added in `backend/app/models/enums.py`:
    * `PlaybookStatus`, `PlaybookRiskLevel`, `PlaybookTriggerType`, `PlaybookExecutionStatus`, `StepExecutionStatus`, `ApprovalStatus`, `AutomationActionType`, `ScenarioDifficulty`, `ScenarioCategory`, `ScenarioStage`, `ScenarioAttemptStatus`, `QuestionType.SOAR`, `QuestionType.SOC_SCENARIO`.

* **Frontend UI & Workbenches (`frontend/src/`)**:
  * `SoarDashboardPage.tsx` (`/soc/automation`): KPI metrics (playbooks, hours saved, success rate, waiting approval alert banner), recent executions, quick trigger modal.
  * `SoarPlaybooksPage.tsx` (`/soc/automation/playbooks`): Filterable playbook catalog with risk badges and status toggles.
  * `SoarPlaybookDetailPage.tsx` (`/soc/automation/playbooks/:playbookId`): Step flowchart, parameters, condition inspector, dry-run simulator tab.
  * `SoarExecutionsPage.tsx` (`/soc/automation/executions`): Execution history and filtering.
  * `SoarExecutionDetailPage.tsx` (`/soc/automation/executions/:executionId`): Step timeline, input/output inspection, analyst approval action buttons.
  * `SocScenariosPage.tsx` (`/soc/scenarios`): 28-scenario catalog with difficulty and category filters.
  * `SocScenarioWorkspacePage.tsx` (`/soc/scenarios/workspace/:attemptId`): 9-stage guided investigation workspace with hint unlock modal.
  * `SocScenarioResultPage.tsx` (`/soc/scenarios/results/:attemptId`): Final score breakdown, feedback list, and root-cause explanation.
  * Navigation: Added `SOAR Automation` and `SOC Scenarios` in `Sidebar.tsx`.
  * Stylesheets: `frontend/src/components/soar/soar.css` and `frontend/src/components/soc_scenarios/socScenarios.css`.

* **Verification & Testing**:
  * **Backend**: **235 passing Pytest tests (100%)** (`tests/test_soar_engine.py` + full suite).
  * **Backend Linter**: Ruff check passes with **0 errors**.
  * **Frontend**: **127 passing Vitest tests (100%)** (`src/test/SoarAndScenarios.test.tsx` + full suite across 16 test files).
  * **Frontend Linter & Build**: `tsc -b && vite build` clean with **0 errors**, Oxlint passes with **0 errors**.
  * **Documentation**: `docs/soar-engine.md`, `docs/soc-scenarios.md`, `docs/automation-safety.md`.

---

### Completed in Step 17: Incident Response, Case Management & MITRE ATT&CK Investigation Framework

* **Safe Offline Incident Response & Case Management System**:
  * Built an authoritative offline educational incident handling and case coordination workbench (`backend/app/services/incident_response/`).
  * End-to-end incident lifecycle aligned with NIST SP 800-61 Rev 2:
    `ALERT → TRIAGE → INCIDENT → CASE → EVIDENCE → TIMELINE → HYPOTHESIS → FINDINGS → MITRE ATT&CK → RESPONSE PLAN → CONTAINMENT SIMULATION → ERADICATION SIMULATION → RECOVERY SIMULATION → LESSONS LEARNED → REPORT`.
  * **Strict Offline Educational Boundary**: Zero live execution, zero network reconfiguration, zero process kill, zero active credential modification. Every defensive action enforces `simulation_only = True` with prominent safety warning banners across the UI.

* **Relational Schema & Alembic Migration (`71031b25909d`)**:
  * Added 8 core database models in `backend/app/models/incident.py`, `playbook.py`, `mitre.py`:
    * `Incident`: Core ticket entity tracking priority, status, NIST phase, classification, SLA timestamps, and root cause notes.
    * `IncidentAlert`: Cross-linking junction connecting detection alerts, SOC alerts, and SIEM correlation alerts to the incident.
    * `IncidentEvidence`: Cross-engine evidence repository calculating and storing SHA-256 cryptographic hashes.
    * `EvidenceAuditLog`: Immutable chain of custody ledger recording actions (`ATTACHED`, `VIEWED`, `ANNOTATED`, `LINKED`, `HASH_VERIFIED`).
    * `IncidentTimelineEvent`: Multi-source unified timeline with category tags and milestone markers.
    * `IncidentHypothesis`: Structured scientific working theories with testing states (`PROPOSED`, `SUPPORTED`, `NOT_SUPPORTED`, `INCONCLUSIVE`).
    * `IncidentFinding`: Validated discoveries linked to affected assets and MITRE techniques.
    * `ResponseAction`: Non-destructive containment, eradication, and recovery simulations with educational outcomes.
    * `AttackTactic` & `AttackTechnique`: 14 Enterprise tactics and comprehensive techniques catalog.
    * `IncidentTechniqueMapping`: Association of techniques to active incidents with confidence ratings (`OBSERVED_EVIDENCE`, `HYPOTHESIS_SUGGESTED`, `ANALYST_INFERRED`).
    * `IncidentPlaybook`: 10 standardized Incident Response operating procedures.

* **MITRE ATT&CK Enterprise Matrix Engine**:
  * Seeded 14 Enterprise Tactics and 35+ core techniques (`backend/scripts/seed_incident_response.py`).
  * Interactive 14-column heat map visualizer with dynamic coverage calculations (`MatrixCoverageResponse`).
  * Technical guidance drawer detailing detection rules, mitigation strategies, and official references.

* **Response Action Simulation Sandbox**:
  * Simulation-only containment, eradication, and recovery engine.
  * Allows students to propose, execute, and revert simulated defensive actions (`SIMULATE_HOST_ISOLATION`, `SIMULATE_ACCOUNT_RESTRICTION`, `SIMULATE_NETWORK_BLOCK`, `SIMULATE_IOC_BLOCK`, `SIMULATE_SESSION_REVOCATION`, `SIMULATE_REMOVE_PERSISTENCE`, `SIMULATE_RESET_CREDENTIAL`, `SIMULATE_RESTORE_HOST`).
  * Deterministic educational feedback explaining operational rationale, side effects, and trade-offs.

* **Cross-Engine Evidence Vault & Chain of Custody**:
  * Aggregates observables from Step 10 (PCAP), Step 11 (Detection), Step 12 (SOC), Step 13 (Threat Intel), Step 14 (Threat Hunting), Step 15 (SIEM), and Step 16 (Endpoint).
  * Cryptographic integrity verification comparing live SHA-256 payload digests against stored values.

* **Standardized Playbooks & Post-Incident Executive Reporting**:
  * 10 pre-configured incident playbooks covering Ransomware, Phishing, Pass-the-Hash, DNS C2, Web Exploitation, and DDoS.
  * Automated NIST SP 800-61 Post-Incident Executive Report generation (Markdown + JSON) with one-click `.md` download.

* **Frontend UI & Workbenches (`frontend/src/`)**:
  * `IncidentsPage.tsx` (`/soc/incidents`): Incident queue, KPI metrics, filter bar, safety banner, and creation modal.
  * `IncidentDetailPage.tsx` (`/soc/incidents/:incidentId`): 8-tab comprehensive IR workbench (`Overview`, `Evidence & Custody`, `Timeline`, `Hypotheses & Findings`, `MITRE ATT&CK`, `Response Simulation`, `Playbook Guide`, `Executive Report`).
  * `MitreMatrix.tsx`: 14-column interactive ATT&CK matrix with heat map indicators and technique detail inspection.
  * `EvidenceDrawer.tsx`: Evidence vault with SHA-256 verification and collapsible chain of custody logs.
  * `IncidentTimeline.tsx`: Multi-source chronological timeline with milestone filters and auto-sync trigger.
  * `ResponseSimulator.tsx`: Containment/eradication sandbox with propose modal, execute/revert buttons, and simulation safety banners.
  * `ReportView.tsx`: NIST SP 800-61 executive report viewer with download and copy utilities.
  * `MitreCoveragePage.tsx` (`/soc/mitre`): Standalone ATT&CK matrix explorer.
  * `PlaybooksPage.tsx` (`/soc/playbooks`): 10 IR standard operating procedure guides with phase checklists.
  * Navigation: Added `Incident Response`, `MITRE ATT&CK`, and `IR Playbooks` in `Sidebar.tsx`.
  * Styling: Cyber dark SOC styling in `incidentResponse.css`.

* **Verification & Testing**:
  * **Backend**: **219 passing Pytest tests (100%)** (`tests/test_incident_response.py` + all prior suites).
  * **Backend Linter**: Ruff check passes with **0 errors**.
  * **Frontend**: **120 passing Vitest tests (100%)** (`src/test/IncidentResponse.test.tsx` + all 14 prior suites).
  * **Frontend Linter & Build**: `tsc -b && vite build` clean with **0 errors**.
  * **Documentation**: `docs/incident-response.md`, `docs/mitre-framework.md`, `docs/response-simulation.md`.

---

### Completed in Step 16: Endpoint Security & Host Investigation Engine

* **Safe Offline Educational Endpoint Simulator**:
  * Built an authoritative offline educational endpoint security and host investigation engine (`backend/app/services/endpoint_security/`).
  * End-to-end host investigation lifecycle: `HOST → TELEMETRY → EVENT → OBSERVATION → CORRELATION → DETECTION → IOC → INVESTIGATION → HYPOTHESIS → EVIDENCE → CONCLUSION`.
  * **Strict Offline Boundaries**: Strictly defensive offline analysis of synthetic endpoint telemetry. Zero endpoint agents, zero command execution (PowerShell/Bash/CMD/`eval`/`exec`), zero process termination, zero registry editing, zero live packet capture, zero real malware. All addresses in RFC 5737 (`192.0.2.0/24`, `198.51.100.0/24`, `203.0.113.0/24`) and RFC 2606 (`.test`).

* **Relational Schema & Alembic Migration (`i01e2f345683`)**:
  * Added 8 core database models in `backend/app/models/endpoint_security.py`:
    * `EndpointHost`: Synthetic host fleet inventory, platform, architecture, OS build, risk level, status.
    * `EndpointEvent`: 10-category multi-telemetry schema (processes, auth, network, DNS, files, registry, services, persistence, privileges).
    * `EndpointInvestigation`: Scoped student investigation cases with priority, status, and IDOR protection.
    * `EndpointHypothesis`: Analyst working hypotheses with confidence tiers (`LOW`, `MEDIUM`, `HIGH`) and testing states.
    * `EndpointEvidence`: Corroborating host observables with analytical relevance tags (`SUPPORTING`, `REFUTING`, `INCONCLUSIVE`).
    * `EndpointFinding`: Key adversary discoveries with MITRE ATT&CK techniques and severity ratings.
    * `EndpointConclusion`: Executive analytical conclusion, final verdict, lessons learned, and automated rubric scoring (0–100).
    * `EndpointScenario`: Guided hands-on host investigation challenges with objectives and solution rubrics.

* **Multi-Category Telemetry & Process Tree Engine**:
  * `HostService`: Fleet-wide aggregations, platform distributions, and individual host overview metrics.
  * `TelemetryService`: Category-filtered queries, unified chronological timeline, and authentication pattern detection (*"Pattern requiring investigation"* / *"Normal logon activity"*).
  * `ProcessTreeService`: Recursive parent-child process hierarchy construction (`explorer.exe` → `powershell.exe` → `update.exe`) with execution arguments, integrity levels, spawned/terminated timestamps, and socket/DNS/file correlations.

* **Cross-Platform Escalation & 1-Click Pivots**:
  * Integrated with Step 13: 1-click pivot from endpoint observables (file hashes, destination IPs, domains) into Threat Intelligence.
  * Integrated with Step 14: 1-click launch of Threat Hunting campaigns pre-seeded with endpoint event context.
  * Integrated with Step 12: Direct escalation from suspicious endpoint alerts into SOC Investigation Cases.
  * Integrated with Step 15: Temporal window correlation with SIEM security event logs.
  * Integrated with Step 10: Port and IP correlation with offline PCAP captures.

* **Guided Hands-On Training Scenarios (`ESCEN-01` to `ESCEN-06`)**:
  * 6 pre-seeded educational investigation scenarios:
    * `ESCEN-01`: Suspicious PowerShell Process Spawning (Process Anomaly & Ingress Tool Transfer)
    * `ESCEN-02`: Persistence via Scheduled Task & Registry Run Key (Persistence Mechanism)
    * `ESCEN-03`: Unauthorized Privilege Escalation via Sudo on Linux (Privilege Escalation)
    * `ESCEN-04`: Host-Based Credential Access & Brute-Force Logons (Credential Access)
    * `ESCEN-05`: Suspicious Service Installation & Lateral Movement (Defense Evasion)
    * `ESCEN-06`: Obfuscated Binary Execution & C2 Beaconing (C2 Communication)
  * Automated solution validator evaluating student-identified processes, parents, C2 destinations, persistence mechanisms, and verdicts.

* **Frontend UI & Workbenches (`frontend/src/`)**:
  * `EndpointDashboardPage.tsx` (`/endpoint-security`): Fleet overview, KPI cards, synthetic training warning banner, host preview grid, SOC methodology guidance.
  * `EndpointHostsPage.tsx` (`/endpoint-security/hosts`): Filterable host inventory (by platform, risk level, search) with host cards and workbench links.
  * `EndpointHostDetailPage.tsx` (`/endpoint-security/hosts/:hostId`): Tabbed workbench (`Overview`, `Processes`, `Timeline`, `Authentication`, `Network`, `DNS`, `Files`, `Persistence`, `Privileges`) and case creation modal.
  * `ProcessTree.tsx`: Interactive collapsible process tree with PID badges, integrity levels, and process details drawer.
  * `EndpointTimeline.tsx`: Unified chronological host timeline with category chips and pivot action modals.
  * `EndpointEventsPage.tsx` (`/endpoint-security/events`): Multi-host searchable telemetry explorer with 1-click pivot actions.
  * `EndpointInvestigationsPage.tsx` (`/endpoint-security/investigations` & `/:investigationId`): Case listing and 3-panel workspace for hypotheses, evidence, findings, and conclusion scoring.
  * `EndpointScenariosPage.tsx` (`/endpoint-security/scenarios` & `/:slug`): Scenario catalog, background narrative, objectives checklist, hints reveal, and analytical findings validator.
  * Navigation: Added `Monitor` icon in `Sidebar.tsx` and sub-navigation bar in `EndpointNav.tsx`.
  * Styling: Cyber dark theme in `endpointSecurity.css`.

* **Verification & Testing**:
  * **Backend**: **206 passing Pytest tests (100%)** (`tests/test_endpoint_security.py` + full suite).
  * **Backend Linter**: Ruff check passes with **0 errors**.
  * **Frontend**: **113 passing Vitest tests (100%)** (`src/test/EndpointSecurity.test.tsx` + full suite).
  * **Frontend Linter & Build**: `tsc -b && vite build` clean with **0 errors**.
  * **Documentation**: `docs/endpoint-security.md`, `docs/process-investigation.md`, `docs/endpoint-security-safety.md`.

---

### Completed in Step 15: SIEM & Security Log Analysis Engine

* **Safe Offline Educational SIEM Architecture**:
  * Built an authoritative offline educational SIEM workbench (`backend/app/services/siem/`).
  * End-to-end telemetry lifecycle: `COLLECT → NORMALIZE → SEARCH → FILTER → VISUALIZE → CORRELATE → DETECT → INVESTIGATE → HUNT → DOCUMENT`.
  * **Strict Offline Boundaries**: Strictly defensive offline analysis of synthetic security logs. Zero endpoint agents, zero raw socket listeners, zero outbound network scanning, zero SSRF, and zero dynamic code execution (`eval`/`exec`). All synthetic addresses adhere strictly to RFC 5737 and RFC 2606.

* **Multi-Format Log Normalization Engine**:
  * Implemented `LogNormalizationService` parsing heterogeneous formats into a unified taxonomy:
    * Windows Event Log XML (Events 4624, 4625, 4688, 4740, 7045)
    * Linux / Unix Syslog (RFC 3164/5424) for `sshd`, `sudo`, and `iptables`
    * ArcSight Common Event Format (CEF) for network security appliances (e.g. Cisco ASA)
    * Structured JSON & Comma-Separated Values (CSV)
  * Harmonizes vendor action codes into standard states: `LOGIN`, `LOGIN_FAILURE`, `CONNECTION`, `CONNECTION_BLOCKED`, `DNS_QUERY`, `PROCESS_START`, `ACCOUNT_DISABLED`, `PRIVILEGE_CHANGE`.

* **Governed Visual Query Builder & Search Engine**:
  * Implemented `SiemSearchService` executing queries over whitelisted indexed schema attributes: `action`, `event_category`, `source_type`, `host`, `username`, `source_ip`, `destination_ip`, `destination_port`, `protocol`, `severity`, `status`, `message`, `domain`, `process_name`.
  * Boolean logic combinations (`AND`, `OR`), 8 relational operators (`=`, `!=`, `CONTAINS`, `STARTSWITH`, `>`, `<`, `>=`, `<=`), free-text search, time window presets (`ALL`, `LAST_15M`, `LAST_1H`, `LAST_24H`, `LAST_7D`), and saved search CRUD.

* **Real-Time Aggregations & Dashboard Telemetry**:
  * Implemented `SiemAggregationService` computing KPI metrics, severity distributions, category breakdowns, top suspicious entities (source IPs, target hosts, usernames, destination ports), and time-series histogram buckets.

* **Multi-Event Behavioral Correlation Engine**:
  * Implemented `SiemCorrelationEngine` tracking sliding time windows, threshold aggregations, and multi-stage attack patterns.
  * 9 default educational correlation rules: `AUTH-001`, `AUTH-002`, `NET-001`, `NET-002`, `DNS-001`, `PRIV-001`, `WIN-001`, `WEB-001`, `CORR-001`.
  * Dry-Run Rule Tester enabling students to evaluate rule logic against historical datasets without polluting alert queues.
  * Correlation alert lifecycle management (`NEW`, `ACKNOWLEDGED`, `ESCALATED`, `RESOLVED`, `FALSE_POSITIVE`).

* **Hands-on Practice Labs & Automated Scoring**:
  * 8 guided educational lab scenarios across Beginner, Intermediate, and Advanced difficulties.
  * Automated validation engine assessing queries, identified malicious entities, and analyst findings notes.

* **Cross-Platform Escalation Pipeline**:
  * One-click escalation from SIEM events or correlation alerts to Step 12 SOC Investigations (`INV-YYYY-XXXX`).
  * Seamless threat hunting initialization in Step 14 (`HUNT-YYYY-XXXX`) with pivot entity binding.
  * Automated candidate IOC extraction directly into Step 13 Threat Intelligence feeds.

* **Database Schema & Migrations (`h01e2f345682`)**:
  * Added 9 models: `log_sources`, `security_log_datasets`, `raw_log_events`, `security_events`, `log_correlation_rules`, `correlation_alerts`, `saved_searches`, `search_history`, `siem_lab_scenarios`.
  * Initialized and seeded 7 log sources, 3 datasets, 685 events, 9 correlation rules, 6 alerts, and 8 labs via `backend/scripts/seed_siem.py`.

* **Frontend UI & Workbenches (`frontend/src/`)**:
  * `SiemDashboardPage.tsx` (`/siem`): KPI cards, histogram, top entities, category breakdown, recent alerts.
  * `SiemSearchPage.tsx` (`/siem/search`): Query builder, quick filter chips, table with Event ID column, detail drawer, saved searches.
  * `SiemDatasetsPage.tsx` (`/siem/datasets`): Pre-loaded datasets, collector sources, safe ingestion modal with template presets.
  * `SiemRulesPage.tsx` (`/siem/rules`): Rule catalog, sliding window inspector, dry-run tester modal, alert triage table.
  * `SiemLabsPage.tsx` (`/siem/labs` & `/siem/labs/:slug`): Interactive lab scenarios, search pre-fill, validation form, scoring report.
  * Navigation: `Database` icon in `Sidebar.tsx` and sub-navigation bar in `SiemNav.tsx`.
  * Styling: `frontend/src/components/siem/siem.css` with dark SOC theme.

* **Verification & Testing**:
  * **Backend**: **190 passing Pytest tests (100%)** (`tests/test_siem_engine.py` + full suite).
  * **Backend Linter**: Ruff check passes with **0 errors**.
  * **Frontend**: **107 passing Vitest tests (100%)** (`src/test/Siem.test.tsx` + full suite).
  * **Frontend Linter & Build**: `tsc -b && vite build` clean with **0 errors**.
  * **Documentation**: `docs/siem.md`, `docs/log-normalization.md`, `docs/siem-query-language.md`, `docs/log-correlation.md`, `docs/siem-security.md`.

---

### Completed in Step 14: Threat Hunting & Investigation Workspace

* **Offline Threat Hunting & Investigation Architecture**:
  * Built an authoritative offline educational threat hunting workbench (`backend/app/services/threat_hunting/`).
  * Investigative flow: `LEARN → OBSERVE → ALERT → IOC → HUNT → CORRELATE → FORM HYPOTHESIS → COLLECT EVIDENCE → VALIDATE → CONCLUDE → DOCUMENT`.
  * Unified data pipeline connecting: `PCAP (Step 10) → Packet Metadata → Detection Alerts (Step 11) → SOC Alerts (Step 12) → IOCs (Step 13) → Threat Hunting Workspace (Step 14)`.
  * **Strict Offline Boundaries**: Strictly defensive offline analysis. Zero raw socket creation, zero network interface packet transmission, zero active port/host scanning, zero SSRF/outbound HTTP fetches, and zero dynamic code execution (`eval`/`exec`).

* **Governed Hunt Query Engine (HQL)**:
  * Implemented `query_engine.py` evaluating multi-condition AST query expressions with whitelist-governed fields (`event_type`, `protocol`, `src_ip`, `dst_ip`, `src_port`, `dst_port`, `domain`, `summary`, etc.).
  * 11 supported operators: `=`, `!=`, `CONTAINS`, `STARTS_WITH`, `ENDS_WITH`, `IN`, `NOT_IN`, `>`, `<`, `>=`, `<=`.
  * Execution performance tracking (`query_time_ms`) and human-readable natural language query explanations.
  * Robust SQL injection protection via SQLAlchemy ORM parameterization and sanitized wildcard escaping.

* **Multi-Source Dataset Management & Normalization**:
  * Implemented `dataset_service.py` synthesizing unified telemetry events from:
    * Step 10 PCAP parsed packets (IP, TCP, UDP, DNS, HTTP, TLS)
    * Step 11 Network Detection alerts
    * Step 12 SOC triage alerts
    * Step 13 Indicators of Compromise (IOCs)
  * Pre-populated with 9 training datasets and 1,000+ normalized events using reserved documentation networks (RFC 5737 and RFC 2606).

* **Threat Hunt Lifecycle & Investigation Room**:
  * Implemented `hunt_service.py` with sequential human-readable IDs (`HUNT-YYYY-XXXX`).
  * 7-Tab Interactive Investigation Room:
    1. **Telemetry & Query Engine**: Visual query builder, raw event inspector, payload viewer, and one-click evidence pinning.
    2. **Timeline View**: Chronological progression of adversary activity, alert triggers, and hypothesis events.
    3. **Entity Correlation Graph**: Bounded topological graph (depth $\le 2$, nodes $\le 50$) visualizing IP, Domain, Port, and Alert links.
    4. **Pivot Correlator**: Rapid exploration tool across `IP`, `DOMAIN`, `PORT`, and `ALERT` pivots with co-occurring telemetry.
    5. **Hypotheses Workbench**: Formulate, test, validate, and refute attack assumptions with confidence ratings (`LOW`, `MEDIUM`, `HIGH`).
    6. **Evidence & Findings Binding**: Categorize raw events as `SUPPORTING`, `CONTRADICTING`, or `CONTEXTUAL`, attaching analyst rationale notes and promoting to formal findings mapped to MITRE ATT&CK.
    7. **Analyst Journal & Conclusion Scoring**: Free-form timestamped field notes, final disposition (`MALICIOUS_CONFIRMED`, `SUSPICIOUS_UNRESOLVED`, `BENIGN_FALSE_POSITIVE`, `INCONCLUSIVE`), executive summaries, and remediation guidance.

* **Curated MITRE ATT&CK Scenarios**:
  * Implemented `scenario_service.py` providing 8 realistic educational threat hunting exercises:
    * `lateral-movement-smb` (Beginner - T1021.002)
    * `dns-tunneling-exfil` (Intermediate - T1071.004)
    * `powershell-beaconing` (Intermediate - T1071.001)
    * `kerberoasting-ad` (Advanced - T1558.003)
    * `internal-recon-scan` (Beginner - T1046)
    * `tls-encrypted-c2` (Intermediate - T1573.002)
    * `phishing-malware-stage` (Advanced - T1204.002)
    * `scheduled-task-persist` (Beginner - T1053.005)

* **Educational Rubric & 100-Point Scoring Engine**:
  * Implemented `scoring_service.py` grading completed hunts across 5 core competency dimensions:
    1. Hypothesis Formulation & Rigor (20 pts)
    2. Evidence Collection & Relevance (25 pts)
    3. Pivot & Correlation Depth (20 pts)
    4. Finding Identification & ATT&CK Mapping (20 pts)
    5. Conclusion, Rationale & Remediation (15 pts)
  * Detailed pedagogical feedback with letter grades (A–F) and recommendations for improvement.

* **Database Schema & Migrations (`g01e2f345681`)**:
  * Applied Alembic migration `2026_09_30_1900-g01e2f345681_add_step14_threat_hunting_tables.py`.
  * Added 7 models: `hunt_datasets`, `hunt_events`, `threat_hunts`, `threat_hunt_hypotheses`, `threat_hunt_evidence`, `threat_hunt_findings`, `threat_hunt_notes`.
  * Populated initial seed datasets and exemplar hunt campaign via `backend/scripts/seed_threat_hunting.py`.

* **Frontend UI & Workbenches (`frontend/src/`)**:
  * `ThreatHuntingDashboardPage.tsx` (`/threat-hunting`): Overview metrics, active hunts, dataset explorer, scenario launch carousel, and custom hunt creation modal.
  * `HuntScenariosPage.tsx` (`/threat-hunting/scenarios`): 8 scenario cards with MITRE ATT&CK tags, difficulty badges, and guided investigation questions.
  * `HuntWorkspacePage.tsx` (`/threat-hunting/hunts/:huntId`): Comprehensive 7-tab workbench with query builder, timeline, entity graph, pivot table, hypotheses, evidence/findings, journal, and conclusion modal.
  * Cross-linking: Direct "Launch Threat Hunt" action buttons embedded in `AlertDetailsPage.tsx` and `IndicatorDetailPage.tsx`.
  * Dedicated styling: `frontend/src/components/threat_hunting/threat_hunting.css`.
  * Navigation: `Crosshair` icon in `Sidebar.tsx` and sub-navigation in `ThreatHuntingNav.tsx`.

* **Verification & Testing**:
  * **Backend**: **174 passing Pytest tests (100%)** (`tests/test_threat_hunting_engine.py` + full suite).
  * **Backend Linter**: Ruff check passes with **0 errors**.
  * **Frontend**: **101 passing Vitest tests (100%)** (`src/test/ThreatHunting.test.tsx` + full suite).
  * **Frontend Linter & Build**: `tsc -b && vite build` clean with **0 errors**.
  * **Documentation**: `docs/threat-hunting.md`, `docs/hunt-query-language.md`, `docs/hunt-investigation-workflow.md`, `docs/threat-hunting-security.md`.

---

### Completed in Step 13: Threat Intelligence & IOC Investigation

* **Offline Defensive Threat Intelligence Architecture**:
  * Built an authoritative offline educational threat intelligence and IOC investigation system (`backend/app/services/threat_intel/`).
  * End-to-end investigation lifecycle: `ALERT → OBSERVED ARTIFACT → EXTRACT IOC → NORMALIZE → CLASSIFY → ENRICH → VALIDATE → CORRELATE → INVESTIGATE → DOCUMENT → DETECTION / CASE`.
  * **Strict Offline Boundaries**: Strictly operates against offline PCAP captures, detection alerts, and local synthetic threat feeds. Zero live network sniffing, zero raw socket emissions, zero active scanning, zero arbitrary URL requests / SSRF prevention, and treatment of all IOCs as passive data.
  * Core educational tenets embedded throughout: *"IOC ≠ Incident"*, *"Unknown ≠ Benign"*, and *"Source Reliability ≠ Indicator Confidence"*.

* **IOC Normalization, Canonicalization & Defanging**:
  * Implemented `NormalizationService` canonicalizing 5 indicator types:
    * `IP_ADDRESS`: Canonical IPv4 and compressed IPv6 formats.
    * `DOMAIN`: Lowercase ASCII/IDNA with trailing root dots stripped.
    * `URL`: Lowercase host, default port handling, and automatic redaction of embedded credentials (`user:pass@`).
    * `FILE_HASH`: Hexadecimal validation and algorithm mapping by digest length (MD5=32, SHA1=40, SHA256=64, SHA512=128).
    * `EMAIL_ADDRESS`: Lowercase `user@domain` format with canonicalized domain component.
  * Defanging neutralization supporting common researcher formats: `hxxp://`, `hxxps://`, `[.]`, `(dot)`, `[:]`, and `[at]`.
  * Preserves raw ingested value, canonical normalized value, and clean display value separately.

* **IOC Extraction & Automated Intelligence Enrichment**:
  * Implemented `IOCExtractionService` passively parsing indicators from packet headers/payloads (L3/L4/DNS/HTTP/TLS SNI), detection alerts, investigations, cases, and free-form analyst notes.
  * Implemented `SyntheticThreatIntelProvider` supplying safe RFC 5737 (`198.51.100.0/24`, `203.0.113.0/24`, `192.0.2.0/24`) and RFC 2606 (`.test`) intelligence data.
  * Implemented `IndicatorService` managing sequential IDs (`IOC-YYYY-XXXX`), auto-enrichment, classification updates, observation recording, and cross-entity correlation across captures and alerts.

* **Structural Relationships & Interactive Correlation Graph**:
  * Implemented directional indicator relationships (`RESOLVES_TO`, `CONTACTS`, `HOSTS`, `REDIRECTS_TO`, `RELATED_TO`, `ASSOCIATED_WITH`).
  * Built correlation graph generator compiling multi-entity nodes (`INDICATOR`, `ALERT`, `INVESTIGATION`, `CASE`) and links, rendered through an interactive SVG visualizer on the frontend.

* **Analyst Watchlists**:
  * Implemented `WatchlistService` allowing students to place high-priority indicators on active monitoring watchlists with custom reasons and expiration dates.
  * Full authorization and IDOR protections ensuring students only manage their own watchlist items.

* **Safe Import & Sanitized Export**:
  * Implemented `ImportExportService` supporting JSON, JSONL, and CSV formats.
  * Enforces safety guardrails: 5MB maximum file size limit, 1,000 indicator batch row cap.
  * Robust CSV formula injection mitigation: prefixing sensitive characters (`=`, `+`, `-`, `@`, `\t`, `\r`) with single quotes on export and safely sanitizing on import.

* **Hands-On Educational Challenges & 5-Dimension Rubric**:
  * Implemented `ChallengeService` providing 5 hands-on investigation scenarios:
    * `c2-ip-attribution`: Command & Control IP beaconing and domain correlation.
    * `typosquatting-phishing-domain`: Typosquatting credential harvesting portal triage.
    * `malicious-file-hash-triage`: Trojan dropper hash triage and MITRE ATT&CK mapping.
    * `benign-cdn-false-positive`: High-volume CDN false positive investigation and rule tuning.
    * `dns-tunneling-exfiltration-domain`: Covert DNS tunneling exfiltration analysis.
  * Automated 100-point rubric evaluation across 5 dimensions (20% each: IOC Identification, Evidence Review, Intel Interpretation, Entity Correlation, SOC Conclusion) with qualitative feedback and pedagogical insights.

* **Database Schema & Migrations (`f01e2f345680`)**:
  * Applied Alembic migration `2026_09_30_1700-f01e2f345680_add_step13_threat_intel_tables.py`.
  * Added 10 models and relations: `threat_intel_sources`, `indicators`, `indicator_relationships`, `indicator_observations`, `indicator_timelines`, `indicator_notes`, `indicator_watchlists`, `threat_intel_challenges`, `threat_intel_challenge_attempts`, `threat_intel_enrichment_cache`.
  * Seeded initial sources, baseline indicators, and challenges via `backend/scripts/seed_threat_intel.py`.

* **Frontend UI & Complete Workbenches (`frontend/src/`)**:
  * `ThreatIntelDashboardPage.tsx` (`/threat-intelligence`): High-level overview metrics, type/classification breakdowns, source origins, and recent indicators.
  * `IndicatorListPage.tsx` (`/threat-intelligence/indicators`): Searchable, filterable repository of cataloged IOCs with manual ingestion modal.
  * `IndicatorDetailPage.tsx` (`/threat-intelligence/indicators/:indicatorId`): Deep investigation view with MITRE ATT&CK, correlated alerts/cases, observed telemetry, timeline, analyst notes, classification updates, and watchlist toggle.
  * `IndicatorGraphPage.tsx` (`/threat-intelligence/graph`): SVG correlation graph visualizer rendering central root IOC and connected satellite entities.
  * `ThreatIntelSearchPage.tsx` (`/threat-intelligence/search`): Dedicated OSINT search engine querying local indicators by value, type, or keyword.
  * `WatchlistPage.tsx` (`/threat-intelligence/watchlist`): Table of monitored indicators under elevated analyst watch.
  * `ThreatIntelChallengesPage.tsx` (`/threat-intelligence/challenges`): Scenario catalog with difficulty ratings and rubric guide.
  * `ThreatIntelChallengeDetailPage.tsx` (`/threat-intelligence/challenges/:slug`): Interactive challenge workspace with submission form and rubric scorecard.
  * Dedicated styling: `frontend/src/components/threat_intel/threat_intel.css` with dark cyber SOC theme.
  * Cross-link integrations: Added Threat Intel investigation actions in `AlertDetailPage.tsx`, `InvestigationWorkspacePage.tsx`, and `CaptureInspectionPage.tsx`.

* **Verification & Testing**:
  * **Backend**: **160 passing Pytest tests (100%)** (`tests/test_threat_intel_engine.py` + full suite).
  * **Backend Linter**: Ruff check passes with **0 errors**.
  * **Frontend**: **96 passing Vitest tests (100%)** (`src/test/ThreatIntel.test.tsx` + full suite).
  * **Frontend Linter & Build**: `tsc -b && vite build` clean with **0 errors**.
  * **Documentation**: `docs/threat-intelligence.md`, `docs/ioc-analysis.md`, `docs/threat-intelligence-sources.md`, `docs/ioc-normalization.md`, `docs/ioc-security.md`, `docs/threat-intelligence-investigation.md`.

---

### Completed in Step 12: SOC Dashboard & Alert Triage

* **Educational Defensive SOC Architecture**:
  * Built an authoritative offline educational SOC analyst simulation environment (`backend/app/services/soc/`).
  * Full analyst lifecycle workflow: `DATA → PACKET ANALYSIS → DETECTION → ALERT → TRIAGE → INVESTIGATION → EVIDENCE → HYPOTHESIS → VALIDATION → CONCLUSION → CLOSE / FALSE POSITIVE`.
  * **Strict Offline Boundaries**: Strictly operates on offline PCAP captures and synthetic network events. Zero live network sniffing, zero active packet injection/replay, zero active firewall modifications/endpoint isolation, and zero automated external probing.
  * Always prominently displays: *"Offline Training Environment"* banner and enforces the core educational tenets *"ALERT ≠ INCIDENT"* and *"OBSERVATION ≠ PROOF"*.

* **Explainable Priority Calculation Service (`P1`–`P4`)**:
  * Implemented `prioritization_service.py` computing deterministic priority based on rule severity (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`, `INFO`), confidence (`HIGH`, `MEDIUM`, `LOW`), evidence count, and packet volume with transparent human-readable explanations.

* **Alert Correlation & Network Context Telemetry**:
  * Implemented `correlation_service.py` discovering related alerts across shared source/destination IP, capture context, and category.
  * Implemented `network_context_service.py` calculating source and destination endpoint context (packet volumes, byte totals, protocol distributions, active ports) from parsed database telemetry.
  * Implemented `timeline_service.py` reconstructing chronological timelines combining initial packet activity, detection triggers, status transitions, and analyst notes.

* **Full Investigation & Hypothesis Lifecycle**:
  * Implemented `investigation_service.py` supporting sequential IDs (`INV-YYYY-XXXX`), bound alerts, evidence items, interactive hypotheses (`UNTESTED`, `SUPPORTED`, `NOT_SUPPORTED`, `INCONCLUSIVE`), verified findings with confidence levels (`LOW`, `MEDIUM`, `HIGH`), and analyst notes.
  * One-click compile & export of complete forensic JSON incident reports (`GET /api/v1/soc/investigations/{id}/report`).

* **Case Management & Incident Containerization**:
  * Implemented `case_service.py` supporting sequential case IDs (`CASE-YYYY-XXXX`), grouping multiple related investigations and alerts into cohesive security incidents.

* **Educational Rubric Evaluation & Challenges**:
  * Implemented `challenge_service.py` evaluating student investigation submissions across 5 weighted criteria (20% each: Alert Triaged, Classification Accuracy, Hypothesis Validity, Evidence Linking, Conclusion Depth) with qualitative guidance tips.
  * Seeded 5 standard educational scenarios (`investigate-tcp-activity`, `investigate-dns-activity`, `investigate-arp-conflict`, `investigate-http-error-pattern`, `investigate-multi-destination-traffic`).

* **Pre-built Datasets & Safe Reset**:
  * Implemented `training_dataset_service.py` providing 5 synthetic datasets (`tcp_investigation`, `dns_investigation`, `arp_investigation`, `mixed_investigation`, `benign_activity`) with safe reset routines.

* **Audit Trails & Security Safeguards**:
  * Implemented `audit_service.py` providing append-only audit trail logging (`SocAuditLog`) and user notifications (`SocNotification`).
  * Enforced authorization and IDOR guards across all endpoints.

* **Database Schema & Migrations (`e01e2f345679`)**:
  * Applied migration `2026_09_30_1600-e01e2f345679_add_step12_soc_tables.py`.
  * Added 14 models and relations: `investigations`, `investigation_alerts`, `investigation_evidence`, `investigation_hypotheses`, `investigation_findings`, `investigation_notes`, `cases`, `case_alerts`, `case_investigations`, `case_notes`, `soc_audit_logs`, `soc_notifications`, `soc_challenges`, `soc_challenge_attempts`.

* **Frontend UI & Complete Workbenches (`frontend/src/`)**:
  * `SocDashboardPage.tsx` (`/soc`): SOC Overview with metrics cards, priority queue, activity stream, network summary, learning recommendations, and dataset loader/reset.
  * `AlertQueuePage.tsx` (`/soc/alerts`): Analyst alert queue with multi-filter search, pagination, and bulk triage actions.
  * `AlertDetailPage.tsx` (`/soc/alerts/:alertId`): Comprehensive alert inspection with timeline, packet evidence links, network context, related alerts, analyst notes, and triage launcher.
  * `AlertTriagePage.tsx` (`/soc/alerts/:alertId/triage`): 12-step guided triage checklist, classification form, and justification notes.
  * `AnalystQueuePage.tsx` (`/soc/queue`): Quick triage workbench for new, high-priority, and assigned alerts.
  * `InvestigationListPage.tsx` (`/soc/investigations`): List of investigations with status filters and "New Investigation" modal.
  * `InvestigationWorkspacePage.tsx` (`/soc/investigations/:investigationId`): Interactive workspace with hypothesis builder, evidence binding, findings recorder, and JSON report export.
  * `CaseListPage.tsx` (`/soc/cases`) & `CaseDetailPage.tsx` (`/soc/cases/:caseId`): Incident case management grouping investigations and alerts.
  * `DetectionCoveragePage.tsx` (`/soc/detection-coverage`): Matrix of protocol categories, active rules, and MITRE techniques.
  * `SocChallengesPage.tsx` (`/soc/challenges`) & `SocChallengeDetailPage.tsx` (`/soc/challenges/:challengeSlug`): Educational scenario launcher, submission form, and qualitative grading feedback scorecard.
  * Dedicated styling: `frontend/src/components/soc/soc.css` with dark SOC theme.

* **Verification & Testing**:
  * **Backend**: **141 passing Pytest tests (100%)** (`tests/test_soc_engine.py` + full suite).
  * **Backend Linter**: Ruff check passes with **0 errors**.
  * **Frontend**: **88 passing Vitest tests (100%)** (`src/test/SocDashboard.test.tsx` + full suite).
  * **Frontend Linter & Build**: `tsc -b && vite build` clean with **0 errors**.
  * **Documentation**: `docs/soc-dashboard.md`, `docs/soc-alert-triage.md`, `docs/soc-investigations.md`, `docs/soc-case-management.md`, `docs/soc-training-scenarios.md`, `docs/soc-security.md`.

---

### Completed in Step 11: Network Detection Engine


* **Deterministic & Explainable Detection Engine**:
  * Built an authoritative offline detection engine (`backend/app/services/detection/detection_engine.py`, `feature_service.py`, `rule_registry.py`, `alert_service.py`, `detection_run_service.py`).
  * Normalizes heterogeneous packet streams and simulator traces into `NormalizedEvent`, `FlowAggregation`, and `HostProfile` objects.
  * Calculates statistical metrics: inter-arrival interval mean and standard deviation, Shannon entropy of subdomains, incomplete handshake ratios, and flow byte asymmetries.
  * **Strict Offline Boundaries**: Operates strictly against parsed capture telemetry in SQLite. Zero live packet sniffing, zero raw socket emissions, zero network packet transmission, and zero payload binary execution.

* **Complete Catalog of 15 Deterministic Detection Rules**:
  * `NET-TCP-001`: Repeated TCP SYN Connection Attempts Without Completion (T1046)
  * `NET-TCP-002`: TCP RST Spike Following SYN Requests (T1046)
  * `NET-TCP-003`: Incomplete TCP Handshake Ratio Above Threshold (T1498)
  * `NET-CONN-001`: Beaconing Pattern with Regular Intervals (T1071)
  * `NET-CONN-002`: Horizontal Host Sweep Across Subnet (T1018)
  * `NET-DNS-001`: DNS NXDOMAIN Response Burst (T1568.002)
  * `NET-DNS-002`: High-Entropy DNS Subdomain Query Pattern (T1071.004)
  * `NET-DNS-003`: Excessive DNS Request Rate to External Resolver (T1071.004)
  * `NET-ARP-001`: Conflicting MAC Address Mapping for Single IPv4 (T1557.002)
  * `NET-ICMP-001`: High-Rate ICMP Echo Request Sequence (T1018)
  * `NET-PORT-001`: Traffic Involving Suspicious High-Risk Port (T1071)
  * `NET-TRAFFIC-001`: Flow Byte Ratio Asymmetry Above Threshold (T1048)
  * `NET-TRAFFIC-002`: High-Frequency Packet Burst Over Short Window (T1498)
  * `NET-HTTP-001`: HTTP Cleartext Authentication in Packet Payload (T1552)
  * `NET-RECON-001`: Multi-Port Vertical Scan Against Target Host (T1046)
  * Seeded into database via `scripts/seed_detection_rules.py`.

* **Deduplication, Dynamic Confidence & Concrete Evidence**:
  * Windowed deduplication key: `dedup_key = f"{rule.rule_id}:{src}:{dst}:{port}:{window_bucket}"` collapsing repetitive events and tracking packet counts.
  * Dynamic confidence scoring (`LOW`, `MEDIUM`, `HIGH`) derived from sample size, ratio thresholds, and variance.
  * Every alert links concrete `AlertEvidence` records (`PACKET`, `FLOW`, `STATISTIC`, `DNS_QUERY`, `TCP_FLAG`, `ARP_ENTRY`) with expandable JSON payloads.

* **Interactive SOC Analyst Triage Lifecycle**:
  * State transitions: `NEW` → `ACKNOWLEDGED` → `INVESTIGATING` → `CLOSED` / `FALSE_POSITIVE`.
  * `AlertStatusHistory` audit log capturing user ID, old/new status, timestamp, and justification reason.
  * `AlertNote` thread for student observations, Wireshark filters, and IOC documentation.
  * Interactive SOC Investigation Checklist allowing students to check off ordered steps.

* **Rule Testing & Sandbox API**:
  * Dry-run simulation endpoint `POST /api/v1/detection/rules/test` evaluating rules against offline captures without persisting database changes.

* **Database Schema & Migrations (`d01e2f345678`)**:
  * Applied migration `2026_09_30_1530-d01e2f345678_add_step11_detection_tables.py`.
  * Added `detection_rules`, `detection_runs`, `detection_alerts`, `alert_evidence`, `alert_notes`, `alert_status_history` tables.

* **Frontend UI & Interactive Workbench (`frontend/src/`)**:
  * `DetectionDashboardPage.tsx` (`/detection`): Real-time metrics cards, severity breakdown, active triage queue with live filters, and recent runs history.
  * `DetectionRunPage.tsx` (`/detection/run`): Run configuration wizard with capture selector, rule scope picker, synchronous execution, and summary metrics.
  * `AlertDetailsPage.tsx` (`/detection/alerts/:alertId`): SOC triage workspace with flow box, MITRE mapping, neutral educational explanation, interactive checklist, evidence table with payload viewer, status controller, and analyst notes.
  * `DetectionRulesPage.tsx` (`/detection/rules`): Rule catalog with filter by category/severity, rule inspection modal, and interactive dry-run Sandbox.
  * Navigation integration: Sidebar link with `ShieldAlert` icon, direct "Run Detection" button on `CaptureInspectionPage.tsx`.
  * Dedicated styling: `frontend/src/components/detection/detection.css`.

* **Verification & Testing**:
  * **Backend**: **129 passing Pytest tests (100%)** (`tests/test_detection_engine.py` + full suite).
  * **Backend Linter**: Ruff check passes with **0 errors**.
  * **Frontend**: **82 passing Vitest tests (100%)** (`src/test/DetectionEngine.test.tsx` + full suite).
  * **Frontend Linter & Build**: Oxlint 0 errors, `tsc -b && vite build` clean with 0 errors.
  * **Documentation**: `docs/detection-engine.md`, `docs/detection-rules.md`, `docs/detection-rule-authoring.md`, `docs/detection-alerts.md`, `docs/detection-security.md`, `docs/detection-investigation.md`.

---

* **Defensive Offline Packet Forensics Engine**:
  * Built an authoritative offline packet dissection and analysis workbench (`backend/app/services/pcap_parser_service.py`, `packet_filter_service.py`, `conversation_service.py`, `pcap_statistics_service.py`, `packet_observation_service.py`, `packet_analysis_service.py`).
  * **Strict Safety Boundaries**: Zero packet transmission, zero raw socket emission, zero packet replaying, zero network sniffing, zero remote target probing, and zero payload execution. HTTP previews are rendered as sanitized ASCII text without running scripts.
  * **Hardened Ingestion**: File size ceiling (50 MB), strict whitelist (`.pcap`, `.pcapng`, `.cap`), blacklist protection (`.exe`, `.dll`, etc.), UUID4 internal storage isolating files against path traversal, and a 5,000 packet cap per capture.

* **Layer-by-Layer OSI Protocol Decapsulation**:
  * **Layer 2 (Data Link)**: Ethernet II (MAC source/destination, EtherType) and ARP (hardware/protocol types, opcode, IP/MAC mappings).
  * **Layer 3 (Network)**: IPv4 & IPv6 (addresses, TTL, hop limits, protocol numbers, header checksums, identification, fragmentation flags) and ICMP (type, code, echo ID/sequence, checksum).
  * **Layer 4 (Transport)**: TCP (ports, sequence & acknowledgement numbers, window size, flags: SYN, ACK, FIN, RST, PSH, URG) and UDP (ports, length, checksum).
  * **Layer 7 (Application)**: DNS (transaction ID, QR, opcode, rcode, query name/type, answers), HTTP (request/response line, method, URI, status code, sanitized header preview), DHCP (op, xid, client/your IP, message type), and TLS (handshake metadata, version, SNI server name indication).

* **Safe AST Display Filter Grammar**:
  * Lexer and recursive-descent parser compiles filter expressions into parameterized SQLAlchemy binary expressions.
  * **Zero `eval()` or `exec()` execution** eliminates code injection vulnerabilities.
  * Supports protocol keywords (`tcp`, `http`, `dns`, `icmp`, `arp`, `udp`), field comparisons (`ip.addr == 10.0.0.5`, `tcp.port == 80`), TCP flag existence (`tcp.flags.syn`, `tcp.flags.rst`), boolean operators (`&&`, `and`, `||`, `or`, `!`, `not`), and parenthesized grouping.

* **5-Tuple Conversations & Flow Sequence Ladders**:
  * Canonical bidirectional conversation grouping (`{proto}_{endpoint1}_{endpoint2}`).
  * Heuristic TCP 3-way handshake lifecycle classifier (`COMPLETE`, `INCOMPLETE`, `RESET`, `UNKNOWN`).
  * Sequence ladder diagram showing chronological packet exchanges between client and server lifelines.

* **Rule-Based Pedagogical SOC Observation Engine**:
  * Heuristic detector identifying noteworthy traffic behaviors: `HIGH_SYN_RATE`, `MANY_TCP_RESETS`, `DNS_NXDOMAIN_SPIKE`, `ARP_MAPPING_CHANGE`, `UNUSUAL_PORT_USAGE`.
  * Neutral educational explanations distinguishing noteworthy traffic behaviors from definitive proof of malice.
  * Clickable evidence packet tags linking observations directly to table rows.

* **Investigation Workspace & Forensic Reporting**:
  * Packet bookmarking with custom analyst tags and notes.
  * Free-form analyst notes journal.
  * Structured finding logger (Title, Severity, Evidence Packets, Hypothesis, Conclusion).
  * Printable and downloadable JSON SOC Forensic Report.

* **Prebuilt Synthetic PCAP Library (`scripts/seed_pcap_library.py`)**:
  * Programmatically generated and seeded 9 reference captures:
    * `basic_ping.pcap` (ICMP Echo Request/Reply)
    * `tcp_handshake.pcap` (Clean TCP 3-Way Handshake)
    * `dns_lookup.pcap` (DNS Query & Answer)
    * `http_request.pcap` (HTTP GET & Response)
    * `dhcp_exchange.pcap` (Full DHCP DORA Cycle)
    * `arp_resolution.pcap` (ARP Request/Reply Mapping)
    * `tcp_reset.pcap` (Abrupt TCP RST Teardown)
    * `multi_host_traffic.pcap` (Multi-Host Mixed LAN Traffic)
    * `noteworthy_syn_pattern.pcap` (Rapid TCP SYN Sequence)

* **Database Schema & Migrations (`c90d1e2f3456`)**:
  * Applied migration `2026_09_30_1400-c90d1e2f3456_add_step10_pcap_tables.py`.
  * Added `captures` table (upload/sample metadata, format, packet counts, duration, summary telemetry).
  * Added `parsed_packets` table (normalized relational OSI headers, layers, layer details).
  * Added `capture_bookmarks`, `capture_notes`, `capture_findings` tables.

* **Frontend UI & Interactive Workbench (`frontend/src/`)**:
  * `PacketAnalysisPage.tsx`: Capture catalog dashboard featuring sample library, user uploads, and upload modal.
  * `CaptureInspectionPage.tsx`: Multi-panel inspection workbench with tabs for Packet Dissector, Conversations & Flow Ladder, Observations, Statistics, and Investigation Workspace.
  * `InvestigationReportPage.tsx`: Formal SOC Forensic Investigation Report with executive telemetry, findings, and JSON export.
  * Components: `CaptureUploader.tsx`, `PacketTable.tsx`, `PacketFilterBar.tsx`, `PacketDetailsPanel.tsx`, `ConversationPanel.tsx`, `StatisticsPanel.tsx`, `ObservationPanel.tsx`, `InvestigationWorkspace.tsx`.
  * Dark Wireshark-inspired styling: `frontend/src/components/pcap/pcap.css`.

* **Verification & Test Coverage**:
  * **Backend**: **18 passing Pytest tests** (`backend/tests/test_pcap_engine.py` + `test_api_v1.py` covering parser, filters, AST validation, conversations, statistics, observations, workspace, and upload API).
  * **Backend Linter**: Ruff check passes with **0 errors, 0 warnings** across `app`.
  * **Frontend**: **78 passing Vitest tests across 8 test files** in 5.09s (`frontend/src/test/PacketAnalysis.test.tsx` testing filter bar, table, layer tree, conversation ladder, statistics, observations, workspace, and catalog).
  * **Frontend Build**: `tsc -b && vite build` compiles cleanly in 1.54s with **0 errors**.

* **Documentation Authored**:
  * `docs/pcap-analysis.md`: Master architecture, pedagogical purpose, and system components.
  * `docs/packet-parser.md`: Reference guide for layer decapsulation (L2 to L7).
  * `docs/packet-filter-language.md`: Filter grammar (EBNF), AST engine, and operator reference.
  * `docs/pcap-security.md`: Strict offline boundaries, upload sanitization, and defensive design.
  * `docs/packet-investigation.md`: 5-step SOC investigation methodology and reporting.

---

### Completed in Step 9: Interactive Network Simulator

* **Authoritative Virtual Educational Simulation Engine**:
  * Built an authoritative, purely virtual network simulation engine (`backend/app/services/simulation_engine.py`) designed for educational transparency, zero-risk experimentation, and deterministic verification.
  * **Strict Safety & Sandbox Guarantee**: Zero raw sockets, zero Scapy packet generation, zero actual socket pings, zero shell subprocesses, and zero `eval()`. Running a simulation transmits frames strictly in memory within the server runtime.
  * **Educational Explanations & Telemetry**: Every hop and frame transmission produces structured `HopRecord` and `SimulationEvent` streams containing clear "Why Did This Happen?" educational explanations and cybersecurity relevance callouts (e.g. ARP cache poisoning, MAC flooding, VLAN hopping, TTL expiration loop mitigation).

* **Simulated Devices & Protocols**:
  * **Devices**: Workstation PCs, Laptops, Servers, 4-Port Layer 2 Switches, Multi-interface Layer 3 Routers, State-aware ACL Firewalls, Internet Cloud WAN, Local DNS Resolvers, and Dynamic DHCP Servers.
  * **Layer 2 Ethernet Switching**: Dynamic source MAC learning tables (`MAC_Table[src_mac] = (port, vlan)`), unknown unicast flooding, broadcast flooding (`FF:FF:FF:FF:FF:FF`), and 802.1Q port VLAN segmentation isolation.
  * **Layer 3 Routing**: Longest Prefix Match (LPM) routing table lookup, IPv4 Time-To-Live (TTL) decrement with loop prevention (`ICMP Time Exceeded (Type 11, Code 0)`), and next-hop gateway resolution.
  * **Perimeter Firewall Filtering**: Sequential ACL rule matching (`ALLOW` / `DENY`) filtering on protocol (`ANY`, `ICMP`, `TCP`, `UDP`), source CIDR, destination CIDR, and port.
  * **End-to-End Protocols**:
    * **ARP**: Address resolution request/reply cycles and local ARP cache updates.
    * **ICMP**: Ping Echo Request (`Type 8`) and Echo Reply (`Type 0`) with simulated latency calculation.
    * **TCP**: 3-Way Handshake (`SYN` → `SYN-ACK` → `ACK`) and closed port reset (`RST`).
    * **DNS**: UDP port 53 query/response against internal record maps (`A` records) and `NXDOMAIN` handling.
    * **DHCP**: Full DORA cycle (`Discover` → `Offer` → `Request` → `Acknowledge`) dynamically binding leases to clients.

* **Database Schema & Migrations (`b89c0d1e2f34`)**:
  * Created and applied migration `2026_09_30_1030-b89c0d1e2f34_add_step9_network_simulator_tables.py`.
  * Added `simulator_topologies` table: user-authored and template library network topologies (JSON geometry, devices, links).
  * Added `simulator_scenarios` table: guided missions, learning objectives, initial topologies, validation rules, progressive hints, and max scores.
  * Added `simulator_scenario_attempts` table: student challenge history, scores, hints used, and pass/fail audit results.
  * Extended `app/models/enums.py` with `SimDeviceType`, `SimProtocol`, `SimEventType`, `SimulatorValidationType`.
  * Created `backend/app/models/simulator.py` declarative models.

* **Prebuilt Topologies & Guided Scenarios (`scripts/seed_simulator_catalog.py`)**:
  * Seeded 6 ready-to-use reference topologies: *Direct Two PC Link*, *Simple Switched LAN*, *Dual Subnet Router*, *Segmented VLAN Network*, *DMZ Firewall Perimeter*, and *Enterprise DNS & DHCP Services*.
  * Seeded 10 progressive guided scenarios:
    * *Beginner*: First Ping (P2P), Build Switched LAN, Subnet Configuration Mastery, Default Gateway Setup.
    * *Intermediate*: Route Between Two Subnets, VLAN Segmentation Challenge, Configure Automated DHCP Service, Local DNS Resolution.
    * *Advanced*: Secure Web Server with Firewall, Troubleshoot Broken Enterprise Network.
  * **Deterministic Validation Service (`SimulatorValidationService`)**: Evaluates student topologies against formal rules (`DEVICE_EXISTS`, `DEVICE_CONNECTED`, `IP_MATCH`, `SUBNET_MATCH`, `GATEWAY_MATCH`, `ROUTE_EXISTS`, `PING_SUCCESS`, `VLAN_MATCH`, `FIREWALL_RULE`) with progressive hint scoring.

* **Backend REST API Endpoints (`backend/app/api/v1/endpoints/simulator.py`)**:
  * `GET /api/v1/simulator/topologies`: List library and user topologies.
  * `GET /api/v1/simulator/topologies/{id_or_slug}`: Retrieve specific topology.
  * `POST /api/v1/simulator/topologies`: Create and persist custom topology.
  * `PUT /api/v1/simulator/topologies/{id}`: Update user topology.
  * `DELETE /api/v1/simulator/topologies/{id}`: Delete user topology.
  * `POST /api/v1/simulator/topologies/validate`: Audit topology for IP conflicts, invalid subnet masks, or missing default gateways.
  * `POST /api/v1/simulator/simulate/packet`: Authoritative virtual packet simulation across topology graph.
  * `GET /api/v1/simulator/scenarios`: List guided scenario missions.
  * `GET /api/v1/simulator/scenarios/{slug}`: Retrieve scenario specification, initial topology, and progressive hints.
  * `POST /api/v1/simulator/scenarios/{slug}/validate`: Validate student topology against scenario rules.

* **Frontend UI & Interactive Workspace (`frontend/src/`)**:
  * `NetworkSimulatorPage.tsx`: Full-screen responsive workspace at `/network-simulator` with prominent sandbox disclaimer banner.
  * `NetworkCanvas.tsx`: Interactive SVG canvas featuring zoom/pan controls, drag-and-drop node movement, interactive port wiring mode, glowing packet pulse animations, and midpoint link deletion buttons.
  * `DevicePalette.tsx`: Draggable device dock categorized into End Devices, Network Devices, and Infrastructure Services.
  * `DevicePropertiesPanel.tsx`: Tabbed inspector (General, Interfaces, Routing Table, Firewall Rules, Services) and canvas-wide Network Overview summary.
  * `SimulationControls.tsx`: Source/Destination selection, protocol toggles, Send Packet action, sample topology selector, Export/Import JSON, and Scenarios launcher.
  * `PacketInspector.tsx`: 5-layer OSI visualizer illuminating active layers and decapsulating Layer 2, Layer 3, Layer 4, and Layer 7 protocol headers.
  * `EventTimeline.tsx`: Chronological event log with severity badges and interactive "Why Did This Happen?" educational popovers.
  * `ScenarioDrawer.tsx`: Slide-over mission drawer featuring objective checklists, progressive 3-step hint system, and automated solution scoring.

* **Verification & Test Coverage**:
  * **Backend**: **109 passing Pytest tests** in 2.48s (`backend/tests/test_network_simulator.py` covering virtual ARP, Layer 2 switching, VLAN isolation, routing, TTL expiration, firewall ACLs, ICMP ping, TCP handshake, DNS, DHCP, topology validation, and scenario evaluation).
  * **Backend Linter**: Ruff check passes with **0 errors, 0 warnings** across `app` and `tests`.
  * **Frontend**: **68 passing Vitest tests across 7 test files** in 2.68s (`frontend/src/test/NetworkSimulator.test.tsx` testing device palette, properties panel, simulation controls, packet inspector, event timeline, scenario drawer, and full page).
  * **Frontend Build**: `tsc -b && vite build` compiles cleanly in 419ms with **0 errors**.

* **Documentation Authored**:
  * `docs/network-simulator.md`: Architecture, canvas design, data models, and usage guide.
  * `docs/simulation-engine.md`: Algorithmic specifications for Layer 2 switching, Layer 3 routing, ARP, TCP handshake, DNS, DHCP, and firewall ACLs.
  * `docs/simulator-scenarios.md`: Catalog of reference topologies and 10 guided scenarios with learning objectives and validation criteria.
  * `docs/simulator-security.md`: Virtual sandbox boundaries, JSON import sanitization, and security design.

---
  * **Strict Pedagogical Principles**: No competitive ranking, public leaderboards, or permanent ability classifications. Student mastery is tracked using neutral, constructive performance states: `NEEDS_PRACTICE` (<60%), `DEVELOPING` (60–79%), `SOLID` (80–89%), `STRONG` (≥90%), and `INSUFFICIENT_DATA` (<5 questions).
  * **Zero-Knowledge Examination Security**: Active adaptive test attempts completely shield question answer keys, `is_correct`, and pedagogical explanations until formal submission.

* **Database Schema & Migrations (`a78b9c1d2e3f`)**:
  * Created and applied migration `2026_09_30_0945-a78b9c1d2e3f_add_step8_adaptive_engine_tables.py`.
  * Added `performance_snapshots` table for historical accuracy, question counts, and diagnostic telemetry tracking across topics and difficulty tiers.
  * Added `recommendation_events` table for transparent student interaction tracking (`VIEWED`, `CLICKED`, `DISMISSED`, `COMPLETED`).
  * Extended `enums.py` with `MockTestType.ADAPTIVE`, `TopicPerformanceStatus`, `RecommendationType`, `RecommendationPriority`, and `ConfidenceLevel`.
  * Created `backend/app/models/adaptive.py` declarative models.

* **Core Configuration & Hyperparameters (`backend/app/core/adaptive_config.py`)**:
  * Centralized hyperparameter configuration preventing scattered magic numbers:
    * `ADAPTIVE_MIN_QUESTIONS = 5`: Confidence threshold before assigning non-neutral performance states.
    * `ADAPTIVE_RECENT_ATTEMPTS = 5`: Recency window for student test history analysis.
    * Recency decay weights: `[1.0, 0.85, 0.70, 0.55, 0.40]`.
    * Session question balance: 50% Focus / Needs Practice, 30% Developing, 15% Solid / Review, 5% Strong / Retention.
    * Performance decay window: 14 days of topic inactivity flags knowledge decay for periodic refresher drills.

* **Backend Services & Engine (`backend/app/services/`)**:
  * `adaptive_performance_service.py` (`AdaptivePerformanceService`):
    * Evaluates recency-weighted accuracy per curriculum topic and Bloom cognitive difficulty level.
    * Sample confidence classification (`LOW` < 5 questions, `MEDIUM` 5–14, `HIGH` ≥ 15).
    * Difficulty progression evaluator (`ADVANCE`, `CONSOLIDATE`, `REINFORCE_BASICS`).
    * Performance decay tracking and empty attempt filtering (`MockTestAttempt.student_answers.any()`).
  * `recommendation_service.py` (`RecommendationService`):
    * Curriculum prerequisite-aware recommendation ranking.
    * Categorized action cards: `LESSON`, `LAB`, `MOCK_TEST`, `TOPIC_PRACTICE`, `REVIEW`, `DIFFICULTY_REINFORCEMENT`.
    * Onboarding track for beginners with insufficient diagnostic data.
    * Highest-priority action selector powering the "What Should I Do Next?" card.
  * `adaptive_test_service.py` (`AdaptiveTestService`):
    * Deterministic multi-factor candidate scoring (`DifficultyWeight` + `NoveltyWeight` + `TypeVariety`).
    * Repetition suppression engine preventing repeat questions seen in the student's last 2 attempts.
    * Session generator with unique slug creation avoiding collision during rapid sitting initialization.

* **REST API Endpoints (`backend/app/api/v1/endpoints/`)**:
  * `GET /api/v1/adaptive/overview`: Overall accuracy, question volume, difficulty distribution, top focus areas, and high-priority action.
  * `GET /api/v1/adaptive/topic-performance`: Topic-level accuracy, status badges, confidence, and recommended difficulty.
  * `GET /api/v1/adaptive/recommendations`: Prioritized, explainable recommendation feed with rationale callouts.
  * `GET /api/v1/adaptive/recommendations/next`: Single top-priority next action.
  * `POST /api/v1/adaptive/events`: Telemetry tracking for recommendations.
  * `POST /api/v1/adaptive-tests/start`: Launch adaptive practice session with custom question count, duration, and focus topic.
  * `GET /api/v1/adaptive-tests/{attempt_id}`: Active sitting question payload with zero-knowledge shielding.
  * `GET /api/v1/adaptive-tests/{attempt_id}/status`: Authoritative server timer synchronization.

* **Frontend UI & Interactive Workspace (`frontend/src/`)**:
  * `WhatShouldIDoNextCard.tsx`: Hero diagnostic card answering the fundamental student question with an explicit "Why" explanation and direct action button.
  * `PerformanceOverviewCard.tsx`: Macro telemetry card with total questions answered, overall accuracy %, and beginner/intermediate/advanced accuracy distribution bars.
  * `TopicPerformanceCard.tsx` & `TopicPerformanceGrid.tsx`: Status-badged topic cards with category filtering ("All", "Attempted", "Needs Practice") and keyword search.
  * `RecommendationCard.tsx` & `RecommendationList.tsx`: Categorized recommendation cards with reason callouts and dismiss/action buttons.
  * `BeginnerPathBanner.tsx`: Guided 5-step foundational track for students with insufficient performance data.
  * `AdaptiveLaunchModal.tsx`: Session customizer modal (question count, duration, focus topic selector).
  * `AdaptivePage.tsx`: Full `/adaptive-test` dashboard.
  * Navigation integration: `Sidebar.tsx` (Adaptive Practice link with Compass icon), `ProgressPage.tsx` (Adaptive Hub entry card), `MockTestWorkspacePage.tsx` (Adaptive Practice badge), and `MockTestResultPage.tsx` (Updated Adaptive Practice link).

* **Command-Line & Demo Tooling (`scripts/`)**:
  * `scripts/seed_demo_adaptive_performance.py`: Seeds realistic student attempt history (strong, weak, developing, decayed) for local evaluation.

* **Verification & Test Coverage**:
  * **Backend**: 93 passing Pytest tests in 2.50s (`backend/tests/test_adaptive_engine.py` covering performance calculation, recommendations, prerequisites, question selection, repetition suppression, and API endpoints).
  * **Backend Linter**: Ruff check passes with 0 warnings/errors.
  * **Frontend**: 60 passing Vitest tests in 2.65s (`frontend/src/test/AdaptiveEngine.test.tsx` testing all cards, launch modal, empty states, and recommendations).
  * **Frontend Build**: `tsc -b && vite build` passes in 457ms with 0 errors.

* **Documentation**:
  * `docs/adaptive-testing.md`: Architecture, algorithms, formulas, and data models.
  * `docs/personalization.md`: Rules, sample sizes, decay logic, and explainability guarantees.
  * `docs/recommendation-engine.md`: Priority formulas, prerequisite checking, and candidate ranking.

---

### Completed in Step 7: Mock Test Catalog & Test Library System

* **Structured Mock Test Catalog (46 Examinations Defined)**:
  * Authored 46 structured networking and cybersecurity assessments across 4 dedicated JSON catalogs in `backend/data/mock_tests/`:
    * `beginner.json` (14 examinations)
    * `intermediate.json` (16 examinations)
    * `advanced.json` (13 examinations)
    * `full_mocks.json` (3 full-length certification simulations: CCNA, Security+, Comprehensive)
  * **Pool Availability & Readiness Diagnostics**:
    * **40 examinations are READY & PUBLISHED**: Fully satisfied by the 531-question bank pool with 826 questions allocated deterministically via `MockTestQuestion`.
    * **6 examinations are in DRAFT / SHORTFALL status**: Single-domain quizzes where question pool is currently deficient (e.g. single-topic DNS, DHCP, advanced subnetting). Attempts are blocked with an HTTP 400 Bad Request error while allowing syllabus inspection.

* **Database Schema & Migrations (`f19a8b2c4e33`)**:
  * Created and applied migration `2026_09_30_0905-f19a8b2c4e33_add_step7_mock_test_catalog_columns.py`.
  * Extended `MockTest` model with:
    * `code: Mapped[str | None]` (indexed, unique, 64-char max; e.g. `BEGINNER-NETWORKING-001`, `FULL-MOCK-001`)
    * `blueprint_id: Mapped[int | None]` (`ForeignKey("test_blueprints.id", ondelete="SET NULL")`, indexed)
    * `prerequisites: Mapped[str | None]` (textual guidance for students prior to sitting)
    * `tags: Mapped[str | None]` (categorical keywords for taxonomy filtering)
    * `blueprint = relationship("TestBlueprint", backref="mock_tests")`

* **Core Services & Catalog Engine (`backend/app/services/`)**:
  * `mock_test_catalog_service.py` (`MockTestCatalogService`):
    * `sync_catalog_from_files`: Idempotent synchronization from JSON catalog definitions into database blueprints and mock test models.
    * Question pool availability auditor and deterministic allocation engine.
    * `list_catalog_tests`: Multi-dimensional filtering by category, difficulty, test_type, topic, duration range, status, and search query. Attaches `is_ready`, `shortfall`, `active_attempt_id`, and student score indicators.
    * `get_catalog_statistics`, `list_catalog_categories`, `list_catalog_topics`, `list_catalog_difficulties`, `list_catalog_types`, and `get_filter_options`.
    * `get_test_preview`: Safe syllabus preview without leaking question text or answer options.
    * `get_attempt_history`: Chronological sitting records for a specific examination.
  * Enhanced `test_attempt_service.py`:
    * Distinguishes 404 from 400 when attempting to start draft/unready tests.
    * Continue active sitting support without reshuffling questions.
    * Fresh retake sitting generation with separate history records.

* **Command-Line Tooling (`scripts/`)**:
  * `scripts/seed_mock_test_catalog.py`: Database synchronization CLI.
  * `scripts/validate_mock_test_catalog.py`: Quality assurance auditor verifying schema, code/slug uniqueness, blueprint rules, and question availability.

* **REST API Endpoints (`backend/app/api/v1/endpoints/mock_tests.py`)**:
  * `GET /api/v1/mock-tests`: Filtered catalog with readiness indicators and active sitting tracking.
  * `GET /api/v1/mock-tests/categories`: Catalog domain categories with live test counts.
  * `GET /api/v1/mock-tests/topics`: Topics represented across catalog tests with counts.
  * `GET /api/v1/mock-tests/difficulties`: Difficulty levels with counts.
  * `GET /api/v1/mock-tests/types`: Test types with counts.
  * `GET /api/v1/mock-tests/filter-options`: Combined options for UI hydration.
  * `GET /api/v1/mock-tests/statistics`: Aggregate catalog metrics.
  * `GET /api/v1/mock-tests/{id}/preview`: Safe syllabus preview.
  * `GET /api/v1/mock-tests/{id}/blueprint`: Associated blueprint and rules.
  * `GET /api/v1/mock-tests/{id}/attempt-history`: Student sitting history for this specific test.
  * `GET /api/v1/mock-tests/{id}`: Detailed test metadata with practice competencies.
  * `POST /api/v1/mock-tests/{id}/start`: Launch or continue exam sitting.

* **Frontend UI Upgrades (`frontend/src/`)**:
  * `MockTestCategoryTabs.tsx`: Domain navigation tabs (All Tests, Recommended Practice, Beginner, Intermediate, Advanced, Comprehensive, Full Mocks).
  * Enhanced `MockTestCard.tsx`: Displays formatted industrial codes, readiness badges, active sitting badges, and state-aware action buttons (Start, Continue, Retake, View Details).
  * Enhanced `MockTestFilters.tsx`: Topic, duration, readiness status, difficulty, test type, and keyword search controls.
  * `MockTestsPage.tsx`: Catalog statistics cards, category switching, recommended starting track, and responsive library grid.
  * `MockTestDetailPage.tsx`: Code badge, readiness alert banner, what you will practice competencies, rules, and sitting history table.

* **Verification & Test Coverage**:
  * Backend: 83 passing pytest tests in 2.12s (`backend/tests/test_mock_test_catalog.py`).
  * Backend linter: Ruff check passes with 0 warnings/errors.
  * Frontend: 53 passing vitest tests in 2.43s (`frontend/src/test/MockTestCatalog.test.tsx`).
  * Frontend build: `tsc -b && vite build` passes in 815ms with 0 errors.

---

### Completed in Step 6: Comprehensive Networking & Cybersecurity Question Bank

* **Repository Scale & Question Inventory**:
  * Built and audited a comprehensive repository of **531 total questions** (486 newly authored across 15 JSON catalogs in `backend/data/question_bank/` + 45 legacy seed questions).
  * Covers **102 distinct curriculum topics** spanning networking fundamentals, protocols, switching, routing, transport mechanics, firewalls, network defense, packet analysis, reconnaissance detection, and SOC investigation.
  * **Zero Duplicate Collisions**: 100% audited for duplicate codes and normalized question texts with 0 duplicate collisions.
  * **Difficulty Distribution**:
    * `BEGINNER`: 176 questions (33.1%)
    * `INTERMEDIATE`: 182 questions (34.3%)
    * `ADVANCED`: 173 questions (32.6%)
  * **Cognitive Level Distribution (Bloom's Taxonomy)**:
    * `REMEMBER`: 132 questions (24.9%)
    * `UNDERSTAND`: 255 questions (48.0%)
    * `APPLY`: 78 questions (14.7%)
    * `ANALYZE`: 66 questions (12.4%)

* **Database Schema & Migrations (`e48d3c51b921`)**:
  * Created and applied migration `2026_09_29_2320-e48d3c51b921_add_step6_question_bank_code_column.py`.
  * Added globally unique, human-readable stable `code: Mapped[str | None]` column (indexed, 64-char max) to `questions` table.

* **Core Services & Quality Engine (`backend/app/services/`)**:
  * `question_validator.py` (`QuestionValidator`):
    * Strict schema validation, topic slug mapping against curriculum tables, points/time constraints, and XSS sanitization.
    * Choice rules: exactly 1 correct for `SINGLE_CHOICE` and `TRUE_FALSE`; at least 1 correct for `MULTIPLE_CHOICE`.
    * Programmatic IPv4 subnetting validation (`verify_subnet_calculation`) powered by Python standard library `ipaddress.IPv4Network`.
    * Duplicate detection engine auditing codes and normalized text bodies.
  * `question_importer.py` (`QuestionImporter`):
    * Directory recursive loader supporting JSON and JSONL catalogs.
    * Tag resolution and in-place idempotent updates.
    * Safe upsert behavior: re-running import creates 0 duplicates and preserves all foreign keys.
  * `question_bank_service.py` (`QuestionBankService`):
    * Fast aggregated metrics query (`get_statistics`).
    * Full-text search and filtering by topic, difficulty, cognitive level, and tag.
    * Admin authoring and question lifecycle management (creation, updates, publishing, archiving).

* **Command-Line Tooling (`scripts/`)**:
  * `scripts/import_questions.py`: CLI importer with `--dry-run`, `--dir`, `--verbose`, UTF-8 console compatibility, and ASCII summaries.
  * `scripts/validate_question_bank.py`: Quality assurance auditor verifying schema, topic links, choice correctness, duplicate absence, and subnet math across all 15 catalog files.

* **REST API Endpoints (`backend/app/api/v1/endpoints/questions.py`)**:
  * `GET /api/v1/questions/statistics`: Aggregated question bank statistics.
  * `GET /api/v1/questions/code/{code}`: Direct lookup by stable human-readable code.
  * `GET /api/v1/questions`: Search and filtered listing with student answer shielding.
  * `GET /api/v1/questions/admin/list`: Instructor listing across all statuses.
  * `GET /api/v1/questions/admin/{id}`: Full question details including authoring explanations and answer keys.
  * `POST /api/v1/questions/admin/create`: Author new validated questions.
  * `PUT /api/v1/questions/admin/{id}`: Update stem, options, points, or tags.
  * `PUT/POST /api/v1/questions/admin/{id}/publish`: Publish question for student exams.
  * `PUT/POST /api/v1/questions/admin/{id}/archive`: Retire question from student visibility.

* **Integration & Exam Blueprint Compatibility**:
  * Verified 100% sufficiency for Step 5's `TestGenerationService` blueprints:
    * `CCNA Network Fundamentals Blueprint`: `is_sufficient: True` (0 shortfall across all 7 topic rules).
    * `Cyber Defense & Packet Forensics Blueprint`: `is_sufficient: True` (0 shortfall across all 5 topic rules).

* **Verification & Testing**:
  * **Backend**: 77/77 Pytest tests passing in 1.48s (`tests/test_question_bank_system.py` covering validation, subnet math, duplicate detection, student shielding, statistics, search filters, admin lifecycle, and blueprints).
  * **Backend Linting**: Ruff check passing with 0 errors, 0 warnings.
  * **Frontend**: 48/48 Vitest tests passing in 2.75s.
  * **Documentation**: `docs/question-bank.md` updated and comprehensive `docs/question-authoring-guide.md` created.

---

### Completed in Step 5: Core Mock Test Engine

* **Examination Architecture & Philosophy**:
  * Production-grade, timed exam engine for individual networking & cybersecurity certification preparation.
  * **Strict Server-Authoritative Timer**: Timers are enforced exclusively by the backend (`expires_at = started_at + duration_minutes`). Client-side countdown is purely visual; late submissions beyond grace periods are auto-expired and rejected.
  * **Zero-Knowledge Student Answer Shielding**: Active attempts completely shield `is_correct`, `explanation`, and answer keys from student payloads (`StudentQuestionPayload`). Attempt review endpoints strictly return HTTP 403 Forbidden while an exam is in progress.
  * **Pedagogical Assessment Feedback**: Objective evaluation with exact-set matching for multi-choice, topic domain performance radar/breakdowns, difficulty accuracy analysis, and comprehensive post-submission answer review.
  * **Resilient Attempt Lifecycle**: Auto-resumption of in-flight sessions, question review marking, answer clearing, retake sessions without history overwrite, and targeted practice generation for incorrect/unanswered questions.

* **Database Schema & Migrations (`c39f182da410`)**:
  * Added `MockTestType` enum (`TOPIC`, `DIFFICULTY`, `MIXED`, `COMPREHENSIVE`, `PRACTICE`, `FULL_MOCK`).
  * Extended `MockTest` with `test_type` and markdown `instructions`.
  * Extended `StudentAnswer` with `is_marked_for_review: Mapped[bool]`.
  * Extended `TestResult` with `passed: Mapped[bool]`, `total_points: Mapped[int]`, `earned_points: Mapped[int]`, and `passing_percentage: Mapped[float]`.

* **Scoring & Test Services (`backend/app/services/`)**:
  * `scoring_service.py`: Exact set matching for multi-choice questions, partial credit prevention, authoritative pass/fail thresholds, topic breakdown calculations, and difficulty breakdown calculations.
  * `test_attempt_service.py`: Attempt initiation, session resumption, zero-knowledge question serialization, answer auto-saving, review marking, timer status synchronization, authoritative submission, post-exam review verification, and targeted practice generation.
  * `test_generation_service.py`: Algorithmic exam generation from `TestBlueprint`, validation of question pool availability per topic/difficulty rule, and shortfall reporting.
  * `mock_test_service.py`: Catalog listing with search/difficulty/type filters and topic count distributions.

* **Curated Seed Data (`backend/app/seed/`)**:
  * 45 total questions with verified RFC citations, clear distractors, and pedagogical explanations.
  * 4 published, ready-to-sit mock tests:
    1. `beginner-networking-fundamentals-test` (30 questions, 30 min, 70% passing)
    2. `beginner-networking-basics` (10 questions, 30 min, 70% passing)
    3. `beginner-osi-and-tcpip-test` (10 questions, 15 min, 70% passing)
    4. `intermediate-networking-subnetting` (12 questions, 25 min, 75% passing)
  * 2 test generation blueprints for automated test authoring.

* **REST API Endpoints (`app/api/v1/endpoints/mock_tests.py`, `mock_test_attempts.py`)**:
  * `GET /api/v1/mock-tests`: Filterable catalog with search, difficulty, and test type filters.
  * `GET /api/v1/mock-tests/{id_or_slug}`: Detailed pre-test page with rules and instructions.
  * `POST /api/v1/mock-tests/{id}/start`: Attempt initialization or resumption.
  * `GET /api/v1/mock-tests/blueprints/list`: Test generation blueprints catalog.
  * `POST /api/v1/mock-tests/blueprints/{id}/validate`: Blueprint question pool audit.
  * `POST /api/v1/mock-tests/blueprints/{id}/generate`: Dynamic mock test synthesis.
  * `GET /api/v1/mock-test-attempts/history`: Student test attempt history.
  * `GET /api/v1/mock-test-attempts/{id}/status`: Live authoritative timer status check.
  * `POST /api/v1/mock-test-attempts/{id}/save-answer`: Real-time answer persistence.
  * `DELETE /api/v1/mock-test-attempts/{id}/clear-answer/{q_id}`: Answer removal.
  * `POST /api/v1/mock-test-attempts/{id}/mark-question/{q_id}`: Review flag toggle.
  * `POST /api/v1/mock-test-attempts/{id}/submit`: Authoritative submission and auto-grading.
  * `GET /api/v1/mock-test-attempts/{id}/result`: Performance scorecard and breakdowns.
  * `GET /api/v1/mock-test-attempts/{id}/review`: Complete post-submission answer key and explanations.
  * `POST /api/v1/mock-test-attempts/{id}/practice`: Targeted practice session synthesis.

* **Frontend UI & Interactive Workspace (`frontend/src/components/mock_tests/`, `pages/MockTests/`)**:
  * **Test Catalog (`/mock-tests`)**: Filterable test cards with search, difficulty pills, test type filters, questions count, duration, and passing threshold badges.
  * **Pre-Test Details (`/mock-tests/:slug`)**: Exam syllabus, rules, time limits, instructions, and Start/Resume action.
  * **Timed Workspace (`/mock-tests/attempt/:id`)**:
    * Responsive two-column exam interface with dark cybersecurity aesthetic.
    * Sticky top navigation bar with live countdown timer (MM:SS), warning alerts at < 5 minutes, answered count, and Exit/Submit buttons.
    * Interactive question palette with color-coded status badges (Current, Answered, Marked for Review, Unanswered).
    * Radio button (Single Choice / True-False) and Checkbox (Multiple Choice) answer inputs.
    * Clear Choice button and Mark for Review toggle.
    * Previous/Next question navigation and keyboard shortcut support.
    * Submission confirmation modal summarizing answered, unanswered, and marked questions.
  * **Results Scorecard (`/mock-tests/attempt/:id/result`)**:
    * Large score display with Pass/Fail status banner.
    * Summary metrics: Total questions, Correct, Incorrect, Unanswered, Time spent.
    * Performance breakdown by topic domain and difficulty level.
    * Direct actions: Review Answers, Retake Test, Practice Missed Questions, Back to Catalog.
  * **Answer Review (`/mock-tests/attempt/:id/review`)**:
    * Full post-exam answer audit with correctness indicators.
    * Status filters: All, Incorrect, Unanswered, Correct, Marked for Review.
    * Pedagogical explanations and highlighted correct options.
  * **Attempt History (`/mock-tests/history`)**: Historical exam attempts with scores, timestamps, and review links.

* **Verification & Testing**:
  * **Backend**: 68/68 Pytest tests passing in 1.36s (`tests/test_mock_test_engine.py` covering catalog filtering, authoritative timer, answer shielding, auto-grading, review guards, retakes, and blueprints).
  * **Backend Linting**: Ruff check passing with 0 errors, 0 warnings.
  * **Frontend**: 48/48 Vitest tests passing in 2.75s (`src/test/MockTestEngine.test.tsx` verifying cards, timers, navigators, question inputs, submission modals, scorecards, and full page flows).
  * **Frontend Type Checking & Build**: `tsc -b && vite build` passing cleanly.
  * **Documentation**: Comprehensive architecture guide in `docs/mock-test-engine.md`.

---

### Completed in Step 4: Hands-on Networking Lab Engine

* **Pedagogical Lab Framework**:
  * Implemented the **LEARN → DO → OBSERVE → EXPLAIN → VALIDATE → CHALLENGE** interactive laboratory cycle.
  * Strict security posture: **Zero arbitrary server-side command execution**. Local system drills provide structured CLI instructions for host terminals, with observations safely verified against server schemas.
  * Prepared extensible architecture supporting 6 environment types (`LOCAL_SYSTEM`, `CONCEPTUAL`, `CONTAINER`, `PCAP`, `SIMULATOR`, `LOG_ANALYSIS`).

* **Database Schema & Migrations (`b28c4e61f092`)**:
  * Added `LabEnvironmentType` and `LabValidationType` core enums.
  * Extended `Lab` with `instructions` markdown overview.
  * Extended `LabStep` with `description`, `points`, `is_required`, and step-question associations.
  * Extended `LabQuestion` with `step_id` foreign key.
  * Extended `LabAttempt` with `total_points`, `percentage`, `attempt_number`, `time_taken_seconds`.
  * Created `LabStepSubmission` model tracking step answers, correctness, earned points, hints used, feedback, and timestamps.

* **Validation Engine & Security (`backend/app/services/lab_validator.py`)**:
  * Multi-type verification engine supporting:
    * `SINGLE_CHOICE` (options mapping, index resolution, synonym matching)
    * `MULTIPLE_CHOICE` (multi-select set comparison, subset matching)
    * `TEXT` & `SHORT_ANSWER` (case-insensitive string normalization, regex patterns, synonym sets)
    * `NUMERICAL` (exact integers, float tolerances)
    * `IP_ADDRESS` (IPv4 / IPv6 syntax, RFC 1918 private address verification)
    * `CIDR` (prefix length validation, subnet matching)
    * `SUBNET` (subnet masks, structured multi-field calculations)
    * `PORT` (TCP/UDP port number bounds 1-65535, well-known port verification)
  * **Zero-Knowledge Student Answer Shielding**: Strips correct answers, regex patterns, and pedagogical explanations before submission. Answers and explanations are unlocked exclusively after server evaluation.

* **Lab Service & API Endpoints (`app/api/v1/endpoints/labs.py`, `lab_attempts.py`)**:
  * `GET /api/v1/labs`: Filterable catalog with search, difficulty, environment, and user status filters.
  * `GET /api/v1/labs/{id_or_slug}`: Detailed lab blueprint with sanitized safe input configs.
  * `GET /api/v1/labs/slug/{slug}`: Slug-based lab resolution.
  * `GET /api/v1/labs/{id_or_slug}/steps`: Step list with verification configurations.
  * `POST /api/v1/labs/{id_or_slug}/start`: Attempt initialization or resumption.
  * `POST /api/v1/lab-attempts/{attempt_id}/steps/{step_id}/submit`: Idempotent step submission with score recalculation.
  * `POST /api/v1/lab-attempts/{attempt_id}/retry`: Attempt reset and fresh attempt counter.
  * `GET /api/v1/lab-attempts`: Student historical attempts list.
  * `GET /api/v1/lab-attempts/{attempt_id}`: Deep attempt review with submitted answers, points, and explanations.
  * `GET /api/v1/labs/telemetry`: Global lab telemetry (total, completed, in progress, average score, tier ratios).

* **Curriculum Seed Data (22 Labs, 43 Steps)**:
  * **10 Beginner Labs (LOCAL_SYSTEM)**:
    1. `find-your-local-ipv4-address`
    2. `identify-network-interfaces`
    3. `find-mac-address`
    4. `inspect-default-gateway`
    5. `inspect-host-routing-table`
    6. `perform-dns-lookup`
    7. `verify-localhost-connectivity`
    8. `inspect-listening-ports`
    9. `compare-ipv4-and-ipv6-addresses`
    10. `map-host-network-profile`
  * **8 Intermediate Labs (LOCAL_SYSTEM & CONCEPTUAL)**:
    11. `calculate-subnet-boundaries`
    12. `find-network-and-broadcast-range`
    13. `tcp-vs-udp-service-mapping`
    14. `trace-tcp-3-way-handshake`
    15. `recursive-dns-resolution-walkthrough`
    16. `http-request-response-headers`
    17. `longest-prefix-match-routing`
    18. `defensive-firewall-rules-acl`
  * **4 Advanced Planned Blueprints (DRAFT)**:
    19. `analyze-suspicious-pcap-beaconing` (PCAP)
    20. `linux-network-namespace-bridge` (Container)
    21. `soc-alert-triage-brute-force` (Log Analysis)
    22. `configure-ospf-routed-topology` (Simulator)

* **Frontend UI & Interactive Workspace (`frontend/src/components/labs/`)**:
  * **Input Components**: `SingleChoiceInput`, `MultipleChoiceInput`, `TextInput`, `NumericInput`, `IPAddressInput`, `CIDRInput`, `PortInput`, `SubnetInput`, `LabAnswerInput`.
  * **Presentation Components**:
    * `LabCard`: Status badges, environment tags, points, minutes, and responsive action links.
    * `LabFilters`: Search, difficulty pills, environment select, status select, and reset button.
    * `LabStepList`: Interactive stepper sidebar with progress bar and earned points.
    * `LabInstructions`: Platform command switcher tabs (Windows / Linux / macOS) with copy-to-clipboard and safe execution guidance.
    * `LabObservation`: Output inspection guidance.
    * `LabHint`: Collapsible guided hints with usage tracking.
    * `LabFeedback`: Real-time success/error alerts and unlocked pedagogical takeaways.
    * `LabCompletion`: Final celebration card with score, accuracy %, time elapsed, step breakdown, and retry action.
  * **Pages & Routing (`frontend/src/pages/Labs/`)**:
    * `/labs`: Full Lab Catalog with live telemetry bar, filters, and cards grid.
    * `/labs/:labSlug`: Interactive two-column workspace.
    * `/labs/history`: Comprehensive attempt history with modal breakdown of past answers and explanations.
  * **Dashboard Integration**: `DashboardPage` updated to fetch live `LabTelemetry` for real completed lab counts.

* **Verification & Testing**:
  * **Backend**: 57/57 Pytest tests passing in 0.97s (`tests/test_lab_engine.py` covering all validation types, answer shielding, idempotency, retries, and security).
  * **Backend Linting**: Ruff check passing with 0 errors, 0 warnings.
  * **Frontend**: 36/36 Vitest tests passing in 2.04s (`src/test/LabEngine.test.tsx` testing all inputs, presentation components, catalog, workspace, and history review).
  * **Frontend Linting & Typing**: Oxlint passing with 0 errors. `tsc -b && vite build` clean.
  * **Documentation**: `docs/lab-engine.md` and `docs/lab-authoring.md`.

---

### Completed in Step 3: Learning System & Curriculum

* Comprehensive Networking & Cybersecurity Curriculum with 38 Production-Quality Lessons.
* Relational dependencies (`topic_prerequisites`, `lesson_progress`, `lesson_bookmarks`).
* 5 Interactive Protocol Visualizers (OSI Stack, TCP Handshake with SYN Flood, DNS Resolution with Cache Poisoning, DHCP DORA with Rogue Server, Packet Encapsulation).
* Full Learning Dashboard (`/learning`), Topic pages, Lesson reader with Markdown, and Bookmarks page.

---

### Completed in Step 2: Database & Content Architecture

* Normalized relational schema designed with SQLAlchemy 2.0 and declarative mapping (`backend/app/models/`).
* Universal Topic pivot anchoring Lessons, Labs, Question Bank items, Blueprint distributions, and Student telemetry.
* Question validation engine with zero-knowledge student answer shielding (`StudentQuestionResponse`).
* Complete database seeding: 1 Course, 19 Modules, 126 Topics, 14 Question Tags, 10 Questions, 2 Mock Tests, and 2 Test Blueprints.

---

### Completed in Step 1: Project Foundation & Shell

* Clean monorepo structure (`frontend/`, `backend/`, `docs/`, `scripts/`, `docker/`).
* React 19 + TypeScript + Vite architecture with dark-mode cybersecurity visual design.
* Full client-side routing covering all required paths.
* FastAPI backend with operational health and API router scaffolding.
* Strict lab security boundary (`is_authorized_lab_target`) preventing unauthorized network execution.

---

## Upcoming Phases

* **Step 20: Advanced Progress Analytics, Career Pathways & Platform Administration**:
  * Multi-dimensional competency radar, career readiness forecasting, student mastery telemetry, and administrator controls.
