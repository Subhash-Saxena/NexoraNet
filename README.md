# NexoraNet

> **Learn. Simulate. Analyze. Defend.**

NexoraNet is an interactive computer networking and cybersecurity learning platform designed for students, educators, and aspiring cybersecurity engineers. It bridges the gap between theoretical textbook diagrams and real-world defensive operations through visual packet simulation, hands-on containerized labs, and an authentic Mini SOC environment.

---

## 🎯 Target Users

* **BCA / Computer Science Students**: Building intuitive mental models of the OSI and TCP/IP stack, IP subnetting, and network protocols.
* **Aspiring Cybersecurity & SOC Analysts**: Learning packet forensics, traffic dissection, intrusion detection rules, and incident investigation.
* **Certification Candidates**: Practicing targeted mock exams and scenario drills for Cisco CCNA, CompTIA Network+, and CompTIA Security+.
* **Networking & Security Instructors**: Leveraging interactive visual demonstrations to explain abstract network flows.

---

## 🏆 Main Goals

1. **Intuitive Visual Learning**: Transform abstract networking concepts (ARP broadcasts, 3-way handshakes, routing tables) into visual, step-by-step animations.
2. **Safe Hands-on Practice**: Provide authentic networking drills inside isolated sandboxes with strict execution guard rails.
3. **Progressive Skill Graduation**: Guide learners from foundational networking fundamentals up through intermediate routing, advanced cyber defense, and Security Operations Center (SOC) triage.
4. **Actionable Mastery Telemetry**: Diagnose weak technical areas and recommend personalized revision paths.

---

## 🚀 Planned Features & Modules

1. **Structured Networking Curriculum**: Layer-by-layer progressive lessons from physical frames to application protocols.
2. **Beginner → Intermediate → Advanced Learning Paths**: Clear track-based progression.
3. **Interactive Networking Explanations**: Visualizers for subnetting, OSI encapsulation, routing algorithms, and protocol state machines.
4. **Hands-on Networking Labs**: Isolated container sandboxes with strictly bounded target permissions.
5. **Mock Tests & Practice Exams**: Authentic timed certification simulations with domain performance breakdowns.
6. **Networking Question Bank**: Categorized repository of vetted questions with RFC citations.
7. **Interactive Network Simulator**: Drag-and-drop topology builder with animated packet traversal.
8. **PCAP & Packet Analysis**: In-browser Wireshark-like stream reassembly and protocol dissection.
9. **Network Security Exercises**: Defense against ARP spoofing, DoS patterns, DNS exfiltration, and stealth scans.
10. **Detection Engineering**: Sigma and Snort/Suricata rule creation workshop with synthetic log verification.
11. **Mini SOC Environment**: Simulated enterprise alert queues, triage workflows, and incident containment.
12. **Incident Investigation Exercises**: Timeline reconstruction, artifact analysis, and threat hunting drills.
13. **Student Progress Tracking**: Multi-domain competency scoring and mastery telemetry.
14. **Personalized Weak-Topic Recommendations**: Algorithmic study guidance.
15. **Security Challenges**: Gamified protocol capture-the-flag drills.

---

## 🛠️ Technology Stack

| Tier | Technologies |
|---|---|
| **Frontend** | React 19, TypeScript, Vite, React Router 7, Modern CSS Architecture, Lucide Icons |
| **Backend** | Python 3.12+, FastAPI, Pydantic v2, Pydantic Settings, Uvicorn |
| **Database** | SQLite (development), SQLAlchemy 2.0 ORM, Alembic migrations |
| **Testing** | Pytest (backend), Vitest + React Testing Library + JSDOM (frontend) |
| **Code Quality** | Ruff (backend linting/formatting), Oxlint & TypeScript (frontend) |
| **Infrastructure** | Docker, Docker Compose, Multi-stage Dockerfiles |

---

## 📂 Project Structure

```text
nexoranet/
│
├── frontend/                     # React + TypeScript + Vite Single Page Application
│   ├── src/
│   │   ├── components/
│   │   │   ├── common/           # Reusable UI widgets (MetricCard, Badge, StatusDot, StateFeedback)
│   │   │   └── navigation/       # Sidebar, Top Navbar, Footer
│   │   ├── pages/                # Route pages (Dashboard, Learning, Labs, MockTests, Simulator, SOC, etc.)
│   │   ├── layouts/              # Main application shell layout
│   │   ├── hooks/                # Custom React hooks (useHealthCheck)
│   │   ├── services/             # API client abstraction layer
│   │   ├── types/                # Shared TypeScript interfaces
│   │   └── test/                 # Vitest component test suites
│   ├── package.json
│   ├── vite.config.ts            # Vite config with API proxy
│   └── vitest.config.ts          # Vitest testing configuration
│
├── backend/                      # FastAPI Python Application
│   ├── app/
│   │   ├── api/
│   │   │   ├── health.py         # GET /api/health endpoint
│   │   │   └── v1/               # Aggregated v1 endpoints (learning, labs, soc, etc.)
│   │   ├── core/                 # Config (Pydantic Settings), Error handling, Security guards
│   │   ├── db/                   # SQLAlchemy engine, session maker, get_db dependency
│   │   ├── models/               # SQLAlchemy Declarative ORM models
│   │   ├── schemas/              # Pydantic request/response schemas
│   │   └── main.py               # FastAPI application factory
│   ├── alembic/                  # Database migration scripts
│   ├── tests/                    # Pytest test cases
│   ├── alembic.ini               # Alembic configuration
│   └── requirements.txt          # Python dependencies
│
├── docs/                         # Technical documentation & system architecture
│   └── architecture.md
│
├── scripts/                      # Local development & testing runner scripts (.bat & .sh)
│
├── docker/                       # Container definitions
│   ├── frontend.Dockerfile
│   └── backend.Dockerfile
│
├── docker-compose.yml            # Multi-service development configuration
├── .env.example                  # Environment variable reference
├── .gitignore                    # Version control ignore rules
├── README.md                     # Project documentation
└── PROJECT_STATUS.md             # Implementation milestone tracker
```

---

## 💻 Local Development Setup (Without Docker)

### Prerequisites
* **Node.js**: v20 or later
* **Python**: v3.12 or later
* **npm**: v10 or later

### 1. Environment Configuration
Copy `.env.example` to `.env` in the root workspace:
```bash
cp .env.example .env
```

### 2. Backend Setup
```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment
python -m venv .venv

# On Windows:
.venv\Scripts\activate
# On Linux / macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start backend development server
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
The FastAPI backend will be live at `http://127.0.0.1:8000`.
Interactive Swagger API documentation is available at `http://127.0.0.1:8000/docs`.

### 3. Frontend Setup
In a new terminal window:
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start Vite development server
npm run dev
```
The frontend will be live at `http://localhost:5173`.
The top navigation bar will dynamically indicate:
`Backend: ● Connected`

---

## 🐳 Docker Development Setup

Run the full stack inside containers with Docker Compose:

```bash
# Build and launch all services in the background
docker compose up --build -d

# View live container logs
docker compose logs -f

# Stop container services
docker compose down
```

* **Frontend**: Accessible at `http://localhost:5173`
* **Backend API**: Accessible at `http://localhost:8000`
* **API Docs**: Accessible at `http://localhost:8000/docs`

---

## 🧪 Testing

### Running Full Test Suite
Windows:
```cmd
.\scripts\run_tests.bat
```

Linux / macOS:
```bash
./scripts/run_tests.sh
```

### Running Backend Tests Separately
```bash
cd backend
pytest tests -v
```

### Running Frontend Tests Separately
```bash
cd frontend
npm test
```

### Running Linters
```bash
# Backend lint check (Ruff)
cd backend && ruff check app tests

# Frontend lint check (Oxlint)
cd frontend && npm run lint
```

---

## 🔒 Security Philosophy & Guard Rails

Because NexoraNet is a cybersecurity education platform, security guard rails are enforced from Day 1:

1. **Strict Target Authorization Boundary**:
   * All lab tooling, network probes, and simulation commands are strictly restricted by code to:
     * `localhost` (`127.0.0.1`, `::1`)
     * Safe virtual lab subnet: `10.99.0.0/16`
   * Targeting public WAN hosts (e.g., `8.8.8.8`, external domains) or unauthorized private networks is blocked by the backend security layer (`is_authorized_lab_target`).
2. **No Arbitrary Command Execution**:
   * No `eval()`, `exec()`, or un-sanitized shell concatenation (`shell=True`).
   * Command arguments are validated and sanitized using Pydantic schemas.
3. **No Leaked Stack Traces**:
   * Centralized exception handlers catch all server faults and return structured JSON errors without revealing internal file paths or stack traces in production.
4. **Environment Isolation**:
   * Secrets and parameters are read strictly from environment variables. No secrets are committed to version control.

---

## 🗺️ Development Roadmap

* **Step 1 (Completed)**: Clean architectural foundation, React frontend dashboard & navigation, FastAPI backend gateway, SQLite/SQLAlchemy setup, Alembic migrations, Docker Compose configuration, dynamic health checking, and test suites.
* **Step 2 (Completed)**: Relational content architecture, 19 modules, 126 topics, Question Bank, Mock Tests & Blueprints, Question Validation Engine, and Zero-Knowledge student answer shielding.
* **Step 3 (Completed)**: Interactive Learning System & Structured Curriculum:
  * 38 comprehensive lessons following the 10-point pedagogical teaching structure.
  * Interactive Learning Dashboard with progress telemetry, Continue Learning card, and real-time search.
  * Interactive visual Learning Roadmap (Beginner ➔ Intermediate ➔ Advanced).
  * Dedicated Topic page (`/learning/topics/:topicSlug`) with prerequisites, objectives, and security relevance.
  * Dedicated Lesson page (`/learning/lessons/:lessonSlug`) with markdown reader, callout perspectives, and server-synced completion.
  * 5 self-contained interactive visual protocol diagrams: OSI 7-Layer Stack, TCP 3-Way Handshake with SYN Flood simulation, Recursive DNS Resolution with Kaminsky exploit, DHCP DORA with Rogue DHCP defense, and Packet Encapsulation deconstruction.
  * Lesson Bookmarking (`/learning/bookmarks`) and curriculum search endpoints.
* **Step 4 (Completed)**: Hands-on Networking Lab Engine:
  * Pedagogical **LEARN → DO → OBSERVE → EXPLAIN → VALIDATE → CHALLENGE** interactive laboratory cycle.
  * Zero-knowledge student answer shielding: backend strips sensitive keys before submission; answers and explanations are unlocked upon correct server validation.
  * Multi-type verification engine supporting Single Choice, Multiple Choice, Text, Numerical, IP Address, CIDR, Subnet Mask, and Port Number.
  * 22 curated networking labs (10 Beginner, 8 Intermediate, 4 Advanced draft blueprints) with 43 step blueprints.
  * Interactive two-column workspace (`/labs/:labSlug`) with platform command switchers (Windows / Linux / macOS) and copy-to-clipboard.
  * Dynamic Lab Catalog (`/labs`) with live telemetry statistics and multi-faceted filtering.
  * Attempt history & submission review drawer (`/labs/history`).
  * Strict security posture: zero arbitrary server-side command execution.
* **Step 5 (Completed)**: Core Mock Test Engine:
  * Server-authoritative timer enforcement (`expires_at = started_at + duration_minutes`) with automatic session expiration handling.
  * Zero-knowledge student answer shielding: student payloads never leak `is_correct`, `explanation`, or answer keys before submission; in-progress reviews return HTTP 403 Forbidden.
  * Responsive two-column exam workspace (`/mock-tests/attempt/:id`) with sticky timer header, question status palette (Current, Answered, Marked for Review, Unanswered), Clear Choice, and Prev/Next navigation.
  * Authoritative backend scoring engine with exact-set matching for multi-choice questions and partial credit prevention.
  * Comprehensive post-submission results scorecard (`/mock-tests/attempt/:id/result`) with pass/fail status, topic performance breakdown, and difficulty accuracy analysis.
  * Post-exam answer review (`/mock-tests/attempt/:id/review`) with question filter toggles and pedagogical explanations.
  * Retake support preserving historical attempts (`/mock-tests/history`) and targeted practice session generation for missed/unanswered questions.
  * Algorithmic test generation foundation via `TestBlueprint` definitions with question availability audits.
  * 4 published mock tests (45 vetted networking questions) and 2 test generation blueprints.
* **Step 6 (Completed)**: Comprehensive Question Bank System:
  * 531 total questions in database (486 newly authored across 15 JSON catalog files + 45 legacy seed questions) covering 102 distinct curriculum topics.
  * Rigorous distribution across Bloom's Taxonomy: Remember (132), Understand (255), Apply (78), Analyze (66).
  * Stable human-readable question code taxonomy (`NET-FUND-xxx`, `OSI-xxx`, `IPV4-xxx`, `PORT-xxx`, `DEV-SEC-xxx`, `SUBNET-xxx`, `TCP-xxx`, `APP-xxx`, `ROUT-xxx`, `FW-xxx`, `PCAP-xxx`, `SEC-DEF-xxx`, `RECON-xxx`, `DET-xxx`, `SOC-xxx`).
  * Programmatic IPv4 subnetting verification using Python's `ipaddress.IPv4Network`.
  * Safe idempotent importer CLI (`scripts/import_questions.py`) with in-place upserting and zero duplicate generation.
  * Quality auditor CLI (`scripts/validate_question_bank.py`) verifying schema, topic links, choice correctness, and duplicate absence.
  * Server-side zero-knowledge student answer shielding (`StudentQuestionResponse`).
  * Question bank statistics endpoint (`GET /api/v1/questions/statistics`) and search/filter API.
  * Admin question authoring and lifecycle management endpoints (`/admin/create`, `/admin/{id}`, publish, archive).
  * 100% blueprint sufficiency for Step 5's exam generation engine.
* **Step 7 (Completed)**: Mock Test Catalog & Exam Preparation
* **Step 8 (Completed)**: Adaptive Testing & Personalized Practice
* **Step 9 (Completed)**: Interactive Network Simulator
* **Step 10 (Completed)**: PCAP & Packet Analysis Engine
* **Step 11 (Completed)**: Network Detection Engine & IDS-Style Alerting
* **Step 12 (Completed)**: SOC Dashboard & Alert Triage
* **Step 13 (Completed)**: Threat Intelligence & IOC Investigation
* **Step 14 (Completed)**: Threat Hunting & Investigation Workspace
* **Step 15 (Completed)**: SIEM & Security Log Analysis Engine
* **Step 16 (Completed)**: Endpoint Security & Host Investigation Engine
* **Step 17 (Completed)**: Incident Response, Case Management & MITRE ATT&CK Framework
* **Step 18 (Completed)**: SOAR-Style Security Automation & Advanced SOC Scenario Engine:
  * Deterministic SOAR playbook execution engine with dry-run verification, approval checkpoints, and simulation rollback safety.
  * Multi-stage SOC training scenarios with progressive alert injection and student containment scoring.
* **Step 19 (Completed)**: CTF / Challenges + Advanced Cybersecurity Training Engine:
  * Safe offline educational CTF challenge engine (`LEARN → PRACTICE → INVESTIGATE → SOLVE → EXPLAIN → DEFEND`).
  * Salted SHA-256 flag verification service with constant-time comparison and zero-knowledge student payload protection.
  * 40 comprehensive seeded challenges across 4 difficulty tiers (Beginner to Expert) and 12 defensive categories.
  * 5 structured training tracks: Network Defender, SOC Analyst, Network Detection, Incident Investigator, and Endpoint Investigator.
  * Multi-source synthetic evidence attachments (PCAP frames, SIEM event logs, IDS alerts, IOC intelligence cards, endpoint artifacts).
  * 3-column interactive cybersecurity workspace (`/challenges/:challengeId/workspace`) with task steppers, evidence explorers, and autosaving student scratchpad.
  * Post-challenge pedagogical reviews (`/challenges/:challengeId/results`) with official solutions, common pitfalls, and next-step recommendations.
  * Adaptive recommendation engine and Module 19 interactive curriculum expansion.
* **Step 20 (Completed)**: Analytics + Skill Assessment + Reports + Portfolio + Admin:
  * Comprehensive Student Analytics Engine tracking learning time, streaks, activity feeds, and 14-day rolling performance trends with non-judgmental educational phrasing.
  * 28-Skill Continuous Assessment Matrix evaluated using recency-weighted scoring (50% recent / 30% historical / 20% practical) and explainable confidence levels (HIGH/MEDIUM/LOW).
  * Pedagogical Recommendation & 10-Achievement Engine providing targeted drills and educational milestones.
  * Formal Educational Assessment Reports (`REP-` codes) and read-only Certificate Verification (`NX-` codes) with simulation disclaimers.
  * Student Portfolio System with 3-tier privacy controls (`PRIVATE`/`UNLISTED`/`PUBLIC`), strict URL scheme validation, zero sensitive data leakage, and JSON export.
  * Administrative Governance & Content Management with server-side RBAC (`HTTP 403 Forbidden` for students), publication state machine validation guards, and immutable audit logging.
* **Step 21 (Completed)**: Production Security, Hardening & Deployment Preparation:
  * Fail-fast production configuration validator preventing deployment with insecure default secrets, SQLite, or wildcard CORS.
  * PBKDF2-HMAC-SHA256 password hashing (100,000 iterations, 16-byte random salt, constant-time verification) and stateless HS256 JWT bearer token authentication.
  * Production PostgreSQL support with SQLAlchemy 2.0 connection pooling (`pool_size=10`, `max_overflow=20`, `pool_recycle=300`, `pool_pre_ping=True`) and cloud URL normalization (`postgres://` → `postgresql://`).
  * Sliding-window rate limiter protecting `/api/v1/auth/login`, `/api/v1/auth/register`, and `/api/v1/challenges/{id}/submit` against brute-force attacks (HTTP 429 with `Retry-After`).
  * Defense-in-depth HTTP security headers middleware (CSP, HSTS, X-Content-Type-Options: nosniff, X-Frame-Options: DENY, Referrer-Policy, Permissions-Policy).
  * Cloud container liveness (`/health`, `/api/health`) and readiness (`/ready`, `/api/ready`) probes.
  * Multi-stage production container configurations (`docker/backend.prod.Dockerfile` with non-root `appuser`, `docker/frontend.prod.Dockerfile` with Nginx Alpine, and `docker-compose.prod.yml`).
  * 100% test pass rate: 267 backend pytest tests, 139 frontend vitest tests, clean linters, and clean production build.
* **Step 22 (Completed)**: Final Integration, Security Audit, E2E QA, Regression Testing & Production Readiness:
  * Server-side JWT token revocation registry (`TokenRevocationRegistry`) with JTI blocklist and `POST /api/v1/auth/logout` endpoint.
  * Linear Alembic migration head verification (`a1b2c3d4e5f6 (head)`) and automated PostgreSQL URL scheme normalization (`postgres://` → `postgresql://`).
  * Strict removal of developer prototype fallbacks across all curriculum and lab endpoints in production mode.
  * AST-based safe SOAR condition evaluation hardening preventing malformed clause runtime crashes.
  * Pydantic V2 modernization across SOAR and SOC scenario response schemas (`model_config = ConfigDict(from_attributes=True)`).
  * Comprehensive Step 22 Security Audit Suite (`test_step22_security_audit.py`) and Full End-to-End Student Journey Suite (`test_e2e_student_journey.py`).
  * 100% test pass rate across platform: **279 passing backend tests (100%)**, **139 passing frontend tests (100%)**, clean Ruff, clean Oxlint, and clean Vite production build.
  * Production documentation suite: `final-security-audit.md`, `end-to-end-testing.md`, `production-readiness.md`, `backup-restore.md`, `deployment-runbook.md`.

