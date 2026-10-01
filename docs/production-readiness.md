# NexoraNet — Production Readiness & Architecture Specification

## 1. Overview
This document specifies the operational architecture, containerization configuration, health/readiness probes, and PostgreSQL support ensuring that **NexoraNet** is ready for zero-cost deployment (e.g. Render, Railway, Supabase, Cloudflare Pages).

---

## 2. Infrastructure & Hosting Topology

```
[Student Browser]
       │
       ▼ HTTPS
[Cloudflare / Edge CDN]
       │
  ┌────┴─────────────────────────────┐
  │                                  │
  ▼ (Static Assets / SPA)            ▼ (Reverse Proxy / API)
[Frontend Cloudflare Pages / Vercel] [Backend Free Tier Web Service]
                                     (FastAPI on Python 3.12/3.14)
                                             │
                                             ▼
                                     [PostgreSQL Database]
                                     (Supabase / Neon / Render)
```

---

## 3. Database Engine & Migration Linearity

### 3.1 Dual-Database Support (PostgreSQL & SQLite)
- **Production Mode**: Driven by PostgreSQL (`postgresql+psycopg2://...`). Automatic URI scheme normalization converts legacy `postgres://` URLs (standard on Render/Heroku/Supabase) to `postgresql://` in `backend/alembic/env.py` and `backend/app/db/session.py`.
- **Development/Testing Mode**: Driven by SQLite with foreign key enforcement (`PRAGMA foreign_keys=ON;`).

### 3.2 Alembic Head Linearity
- The database schema is controlled by Alembic migrations with a single linear head (`a1b2c3d4e5f6 (head)`).
- All models from Steps 1 through 21 (Curriculum, Labs, Questions, Simulator, PCAP, Detection, SOC, Threat Intel, Hunting, SIEM, Endpoint, Incidents, SOAR, Challenges, Analytics, Portfolio) are mapped and tracked without migration forks.

---

## 4. Containerization & Docker Configurations

### 4.1 Production Multi-Stage Backend Dockerfile (`backend/Dockerfile`)
- **Base**: `python:3.12-slim`
- **Security**: Runs under a dedicated, unprivileged non-root user (`appuser`, UID 10001).
- **Optimization**: Multi-stage build strips build compilers (`gcc`, `g++`) from the final runtime image, leaving only runtime shared libraries (`libpcap-dev`, `libpq-dev`).
- **Startup Script**:
  ```bash
  alembic upgrade head && python app/db/init_db.py && uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 2
  ```

### 4.2 Production Frontend Dockerfile / Build Output (`frontend/Dockerfile`)
- Multi-stage build: `node:20-alpine` builds static bundle via Vite; `nginx:alpine` serves static files with gzip compression, security headers, and single-page-app fallback routing.

---

## 5. Health, Liveness & Readiness Probes

The backend exposes dedicated probe endpoints under `/health`:
- `GET /health`: Basic ping probe verifying process responsiveness.
- `GET /health/ready`: Deep readiness probe checking database connectivity and connection pool health.
- `GET /health/live`: Liveness probe for container orchestrators (K8s / Render / Docker Compose).
