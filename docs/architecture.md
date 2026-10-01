# NexoraNet System Architecture

> Tagline: **"Learn. Simulate. Analyze. Defend."**

---

## 1. Overview & Architectural Principles

NexoraNet is engineered as a modular, decoupled learning platform designed for computer networking and defensive cybersecurity education. It is architected to balance high accessibility for BCA and introductory cybersecurity students with rigorous technical authenticity for advanced security practitioners.

The system is structured into five distinct operational domains:
1. **Frontend Presentation & State Layer**: Single Page Application built on React 19, TypeScript, and Vite.
2. **Backend API Gateway & Orchestration**: High-performance asynchronous REST microservice implemented with FastAPI and Pydantic v2.
3. **Data Persistence & Migration Tier**: Relational data modeling using SQLAlchemy 2.0 ORM with Alembic schema versioning.
4. **Interactive Sandbox & Engine Tier (Phased)**: Future containerized Linux network namespaces, topology simulators, and packet parsing engines.
5. **Security Perimeter & Lab Boundaries**: Rigid execution containment ensuring all platform commands remain restricted to localhost and authorized virtual subnets.

---

## 2. Frontend Architecture

### Technology Stack
* **UI Engine**: React 19 (Functional Components with Hooks)
* **Language**: TypeScript 5.8+ (Strict mode, `verbatimModuleSyntax`)
* **Build System**: Vite 6+
* **Routing**: React Router 7 (`BrowserRouter`)
* **Styling**: Modern CSS Custom Properties architecture (`index.css`), optimized for high-contrast dark cybersecurity palettes, accessibility, and zero-runtime overhead.
* **Icons**: `lucide-react`
* **Testing**: Vitest with `@testing-library/react` and `jsdom`.

### Component Hierarchy
```
App
 └── MainLayout
      ├── Sidebar (Route-aware categorized navigation)
      ├── Navbar (Page breadcrumb, live backend connection health monitor)
      └── Main View (via <Outlet />)
           ├── DashboardPage
           │    ├── MetricCard (Learning Progress, Labs, Mock Tests, Skills, Level)
           │    ├── LearningPathFlow (Beginner → Intermediate → Advanced → Cyber Defense → Mini SOC)
           │    └── Feature Exploration Grid
           └── PlaceholderModule (Standardized template for un-implemented future phases)
                ├── Module Header & Status Badges
                ├── "Coming in a later development phase" Notice
                ├── Practice Opportunities Grid
                ├── Curriculum Objectives List
                └── Live API Readiness Introspection
```

### State & API Integration
* **Health Polling Hook (`useHealthCheck`)**: Monitors `GET /api/health` continuously with exponential backoff and error recovery. Provides visual real-time status (`● Connected` vs `○ Disconnected`).
* **Service Abstraction (`apiService`)**: Centralizes fetch requests, timeout abort controllers, and error unwrapping.
* **Component-Based State Feedback (`StateFeedback`)**: Unified UI component rendering loading spinners, error alerts with retry handlers, and empty states.

---

## 3. Backend Architecture

### Technology Stack
* **Framework**: FastAPI (ASGI compliant via Uvicorn)
* **Language**: Python 3.12 - 3.14 compatible
* **Data Validation**: Pydantic v2 & Pydantic Settings
* **ORM**: SQLAlchemy 2.0 (Declarative Base, async-ready)
* **Migrations**: Alembic
* **Code Quality**: Ruff (Linting & Formatting)
* **Testing**: Pytest with HTTPX TestClient

### Layered Structure
```
backend/
├── app/
│   ├── api/
│   │   ├── health.py                 # GET /api/health endpoint
│   │   └── v1/
│   │       ├── router.py             # Aggregated API v1 route aggregator
│   │       └── endpoints/            # Domain sub-routers
│   │           ├── learning.py       # GET /api/v1/learning
│   │           ├── labs.py           # GET /api/v1/labs
│   │           ├── mock_tests.py     # GET /api/v1/mock-tests
│   │           ├── questions.py      # GET /api/v1/questions
│   │           ├── packet_analysis.py# GET /api/v1/packet-analysis
│   │           ├── simulator.py      # GET /api/v1/simulator
│   │           ├── detection.py      # GET /api/v1/detection
│   │           ├── soc.py            # GET /api/v1/soc
│   │           └── progress.py       # GET /api/v1/progress
│   ├── core/
│   │   ├── config.py                 # Pydantic Settings & environment variables
│   │   ├── errors.py                 # Centralized exception handlers & responses
│   │   └── security.py               # Lab safety boundaries & target validation
│   ├── db/
│   │   ├── base.py                   # SQLAlchemy Base and TimeStampedModel
│   │   └── session.py                # SessionLocal engine and get_db dependency
│   ├── models/                       # Database ORM entity definitions
│   ├── schemas/                      # Pydantic request/response validation schemas
│   ├── services/                     # Business logic and domain calculations
│   └── main.py                       # FastAPI application factory & middleware
```

---

## 4. Database Architecture

* **Development Engine**: SQLite (`sqlite:///./nexoranet.db`) with `check_same_thread=False`.
* **Production Engine**: Ready for PostgreSQL (`postgresql+psycopg2://...`) by modifying `DATABASE_URL` in `.env` without altering application ORM models.
* **Base Model Pattern**:
  * `Base`: SQLAlchemy Declarative Base.
  * `TimeStampedModel`: Provides autoincrement primary keys (`id: int`), timezone-aware `created_at` timestamp, and automatically updated `updated_at` timestamp.
* **Migration Strategy**:
  * Alembic configured with `alembic.ini` and `alembic/env.py`.
  * Dynamic target metadata hooked directly into `Base.metadata`.
  * Auto-generation supported for new models via `alembic revision --autogenerate`.

---

## 5. API Architecture

### Endpoint Blueprint
| Method | Path | Purpose | Step 1 Status |
|---|---|---|---|
| `GET` | `/` | Root service metadata & quick links | Operational |
| `GET` | `/docs` | OpenAPI Swagger interactive UI | Operational |
| `GET` | `/api/health` | Service health & availability status | Operational |
| `GET` | `/api/v1/learning` | Structured curriculum metadata | Stub / Info |
| `GET` | `/api/v1/labs` | Lab environment status & limits | Stub / Info |
| `GET` | `/api/v1/mock-tests` | Practice exams status | Stub / Info |
| `GET` | `/api/v1/questions` | Question bank capabilities | Stub / Info |
| `GET` | `/api/v1/packet-analysis`| PCAP engine status | Stub / Info |
| `GET` | `/api/v1/simulator` | Topology simulator status | Stub / Info |
| `GET` | `/api/v1/detection` | Detection rule workshop status | Stub / Info |
| `GET` | `/api/v1/soc` | Mini SOC environment status | Stub / Info |
| `GET` | `/api/v1/progress` | Student progress engine status | Stub / Info |

---

## 6. Security Boundaries & Guard Rails

Because NexoraNet is a cybersecurity education platform, security guard rails are enforced by architectural design:

1. **Target Authorization Boundary**:
   * All lab tooling, ping simulators, and network drills are strictly bounded by `is_authorized_lab_target(target)`.
   * Permitted targets: `localhost`, `127.0.0.1`, `::1`, and the designated virtual lab subnet (`10.99.0.0/16`).
   * Explicitly forbidden targets: Arbitrary internet hosts, public IP addresses (e.g., `8.8.8.8`), and unauthorized local subnets.
2. **Execution Safety**:
   * No dynamic string evaluation (`eval()`, `exec()`).
   * No un-sanitized shell invocations (`shell=True`).
   * All user-supplied parameters are validated through Pydantic type schemas before reaching business logic.
3. **Exception Sanitization**:
   * Production mode suppresses stack traces and internal file paths.
   * Centralized JSON error format: `{"error": {"code": str, "message": str, "details": any}}`.
4. **Network & Origin Isolation**:
   * CORS headers strictly whitelisted via `CORS_ORIGINS` environment setting.
