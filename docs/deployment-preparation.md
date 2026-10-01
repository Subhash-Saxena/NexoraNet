# NexoraNet Deployment Preparation Guide (Step 21 Readiness)

> **Important Boundary Notice**:  
> Step 21 prepares the application for production deployment. Actual live deployment, DNS configuration, and live cloud hosting provisioning belong to Step 22.

---

## 1. Free Web Hosting Architecture Options

NexoraNet is designed to deploy entirely on zero-cost, free-tier cloud infrastructure:

### Target Architecture A: Render Free Tier
- **Frontend**: Render Static Site (connected to frontend repo or subfolder `frontend`, build command `npm run build`, publish directory `dist`).
- **Backend**: Render Web Service (Python 3.12 or Docker, command `uvicorn app.main:app --host 0.0.0.0 --port 10000 --workers 2`).
- **Database**: Render Managed PostgreSQL or external Neon Serverless Postgres.

### Target Architecture B: Cloudflare Pages + Railway / Fly.io
- **Frontend**: Cloudflare Pages (Free global CDN, unlimited bandwidth, instant SPA deploys).
- **Backend**: Fly.io / Railway container running `docker/backend.prod.Dockerfile`.
- **Database**: Supabase / Neon free-tier PostgreSQL instance.

---

## 2. Pre-Deployment Configuration Checklist

Before initiating Step 22 deployment, confirm the following parameters:

- [ ] **Cryptographic Secret**: Generated 64-char key (`openssl rand -hex 32`) set to `SECRET_KEY`.
- [ ] **Environment Flag**: `ENVIRONMENT=production` exported in cloud dashboard.
- [ ] **Debug Disabled**: `DEBUG=False` strictly confirmed.
- [ ] **Database Connection**: PostgreSQL connection string configured in `DATABASE_URL`.
- [ ] **CORS Domains**: Production frontend HTTPS URL listed in `CORS_ORIGINS`.
- [ ] **Liveness Probe**: Configured cloud orchestrator healthcheck to hit `/health` or `/api/health`.
- [ ] **Readiness Probe**: Configured cloud orchestrator readiness check to hit `/ready` or `/api/ready`.
- [ ] **Database Migration Command**: `alembic upgrade head` specified in pre-deploy script.

---

## 3. Local Production Verification Commands

Test production readiness locally before executing live deployment:

```bash
# 1. Run full backend test suite
pytest backend/tests -v

# 2. Run frontend test suite
npm run test:run

# 3. Verify production frontend build
npm run build

# 4. Check backend linting
ruff check backend

# 5. Check frontend linting
npm run lint
```
