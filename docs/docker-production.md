# NexoraNet Production Docker Architecture & Deployment Guide

This document describes the multi-stage containerization, non-root execution policies, and production Docker Compose configuration for NexoraNet.

---

## 1. Container Architecture Overview

NexoraNet uses a decoupled three-tier production architecture:

```
[ Internet / Reverse Proxy ]
             |
             +---> [ frontend: Nginx Alpine (Port 80) ]
             |          | Static Pre-built SPA Assets
             |          | Gzip compression + Cache-Control
             |
             +---> [ backend: Uvicorn / FastAPI (Port 8000) ]
                        | Python 3.12-slim, Non-Root (appuser: 10001)
                        | Multiprocess workers (2 workers)
                        |
                        +---> [ db: PostgreSQL 16 (Port 5432) ]
                                   Persistent pgdata volume
```

---

## 2. Security Hardening Measures in Docker

### Non-Root Application User
The backend Docker image creates a dedicated unprivileged user and group:
```dockerfile
RUN groupadd -r -g 10001 appgroup && \
    useradd -r -u 10001 -g appgroup -s /sbin/nologin -d /app appuser

USER appuser:appgroup
```
This ensures that any vulnerability inside the Python process cannot escalate to container root or access host resources.

### Multi-Stage Build Optimization
- **Backend**: Stage 1 builds C-extensions (`build-essential`, `libpq-dev`). Stage 2 copies only the compiled libraries into a minimal `python:3.12-slim` runner, eliminating build tools and reducing the image attack surface.
- **Frontend**: Stage 1 runs `npm run build` inside `node:22-alpine`. Stage 2 copies only the optimized HTML/JS/CSS assets into a lightweight `nginx:alpine` runner, completely discarding the Node.js runtime and dev dependencies.

### Container Health Probes
Both services include integrated healthcheck probes:
- **Backend Probe**: Checks `curl -f http://localhost:8000/api/health || exit 1` every 30 seconds.
- **Frontend Probe**: Checks `wget -qO- http://localhost:80/ || exit 1` every 30 seconds.
- **Database Probe**: Checks `pg_isready -U nexora -d nexoranet` every 10 seconds.

---

## 3. Running Production Docker Compose

To build and run the complete production topology:

```bash
# 1. Provide production environment variables in .env
cp .env.example .env
# Set ENVIRONMENT=production, strong SECRET_KEY, and PostgreSQL passwords

# 2. Build and launch all production containers
docker compose -f docker-compose.prod.yml up --build -d

# 3. Verify health status of all running containers
docker compose -f docker-compose.prod.yml ps
```
