# NexoraNet — Production Deployment Runbook

## 1. Overview
This runbook provides step-by-step instructions for deploying NexoraNet to free-tier cloud platforms (e.g. Render/Railway for backend, Cloudflare Pages/Vercel for frontend, Supabase/Neon for managed PostgreSQL).

---

## 2. Pre-Deployment Verification Checklist

Prior to launching production hosting:
- [x] Backend tests: 279/279 passed (`pytest backend/tests`).
- [x] Frontend tests: 139/139 passed across 18 suites (`npm test` in `frontend`).
- [x] Frontend build: `tsc -b && vite build` clean (0 errors, 631ms).
- [x] Backend linting: `ruff check backend` clean (0 errors).
- [x] Frontend linting: `oxlint` clean (0 errors).
- [x] Single linear Alembic migration head: `a1b2c3d4e5f6 (head)`.
- [x] Production environment flags set: `ENVIRONMENT=production`, `DEBUG=False`.
- [x] Cryptographic secrets: 64-character high-entropy `SECRET_KEY` generated.

---

## 3. Environment Variables Reference

### 3.1 Backend Service Environment Variables (Configure in Render / Railway)

| Variable | Recommended Production Value | Sensitive |
| :--- | :--- | :---: |
| `ENVIRONMENT` | `production` | No |
| `DEBUG` | `False` | No |
| `SECRET_KEY` | Strong 64-character token from `python -c "import secrets; print(secrets.token_urlsafe(48))"` | **Yes** |
| `JWT_SECRET_KEY` | Strong 64-character token from `python -c "import secrets; print(secrets.token_urlsafe(48))"` | **Yes** |
| `DATABASE_URL` | PostgreSQL connection URI from Neon / Supabase | **Yes** |
| `CORS_ORIGINS` | `https://<YOUR-FRONTEND-URL>` (e.g. `https://nexoranet.pages.dev`) | No |
| `RATE_LIMIT_LOGIN_PER_MINUTE` | `10` | No |
| `RATE_LIMIT_FLAG_PER_MINUTE` | `30` | No |
| `DB_POOL_SIZE` | `10` | No |
| `DB_MAX_OVERFLOW` | `20` | No |
| `DB_POOL_TIMEOUT` | `30` | No |
| `DB_POOL_RECYCLE` | `300` | No |

### 3.2 Frontend Service Environment Variables (Configure in Cloudflare Pages / Vercel)

| Variable | Recommended Value | Sensitive |
| :--- | :--- | :---: |
| `VITE_API_URL` | `https://<YOUR-BACKEND-URL>` (e.g. `https://nexoranet-api.onrender.com`) | No |

---

## 4. Step-by-Step Deployment Instructions

### Step 1: Provision Managed PostgreSQL (Neon / Supabase — Free Tier)
1. Navigate to **Neon** (https://console.neon.tech) or **Supabase** (https://supabase.com).
2. Create a new free project named `nexoranet-prod`.
3. In connection settings, select `Direct connection` or `Pooled connection (Session mode)`.
4. Copy the connection string. Example format:
   ```text
   postgresql://nexora_user:password@ep-sample-pooler.us-east-2.aws.neon.tech/nexoranet?sslmode=require
   ```
   *(Note: If the connection string begins with `postgres://`, NexoraNet automatically normalizes it to `postgresql://`.)*

### Step 2: Deploy Backend Web Service (Render — Free Tier)
1. Navigate to **Render Dashboard** (https://dashboard.render.com) -> **New +** -> **Web Service**.
2. Connect your GitHub repository containing NexoraNet.
3. Configure service settings:
   - **Name**: `nexoranet-api`
   - **Region**: Choose closest to database region (e.g. Ohio / Frankfurt).
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3` (or Docker pointing to `docker/backend.prod.Dockerfile`).
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**:
     ```bash
     alembic upgrade head && python -m app.db.init_db && uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 2
     ```
   - **Instance Type**: `Free`
4. In **Environment Variables**, add the keys from Section 3.1:
   - `ENVIRONMENT` = `production`
   - `DEBUG` = `False`
   - `DATABASE_URL` = `<YOUR-NEON-OR-SUPABASE-URL>`
   - `SECRET_KEY` = `<GENERATED-SECRET-KEY>`
   - `JWT_SECRET_KEY` = `<GENERATED-JWT-SECRET-KEY>`
   - `CORS_ORIGINS` = `https://localhost` *(temporarily, update with frontend URL once deployed)*
5. In **Health Check Path**, enter: `/ready` or `/api/ready`.
6. Click **Create Web Service**. Wait for build completion and copy your public backend URL (e.g. `https://nexoranet-api.onrender.com`).

### Step 3: Deploy Frontend (Cloudflare Pages — Free Tier)
1. Navigate to **Cloudflare Dashboard** -> **Workers & Pages** -> **Create application** -> **Pages** -> **Connect to Git**.
2. Select your NexoraNet repository.
3. Configure build settings:
   - **Project Name**: `nexoranet`
   - **Framework Preset**: `Vite`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Build Output Directory**: `dist`
4. In **Environment variables**, set:
   - `VITE_API_URL` = `https://<YOUR-RENDER-BACKEND-URL>`
5. Click **Save and Deploy**. Cloudflare automatically copies `frontend/public/_redirects` into `dist/_redirects`, providing instant SPA routing.
6. Once deployed, copy your public frontend URL (e.g. `https://nexoranet.pages.dev`).

### Step 4: Update Backend CORS Origins
1. Return to Render Dashboard -> `nexoranet-api` -> **Environment Variables**.
2. Update `CORS_ORIGINS` to your real frontend URL:
   ```text
   CORS_ORIGINS=https://nexoranet.pages.dev
   ```
3. Save changes. Render will automatically redeploy the backend with the new origin.

---

## 5. Post-Deployment Verification Smoke Tests

Run these checks against your live domains:

1. **Liveness Probe**:
   ```bash
   curl -i https://<BACKEND-URL>/health
   # Expected: HTTP 200 with {"status":"ok","service":"NexoraNet API","environment":"production"}
   ```
2. **Database Readiness Probe**:
   ```bash
   curl -i https://<BACKEND-URL>/ready
   # Expected: HTTP 200 with {"status":"ready","database":"connected"}
   ```
3. **Security Headers**:
   ```bash
   curl -I https://<BACKEND-URL>/ready
   # Verify presence of X-Content-Type-Options: nosniff, X-Frame-Options: DENY, Strict-Transport-Security
   ```
4. **Interactive Browser Verification**:
   - Open `https://<FRONTEND-URL>/register`.
   - Register a student account and verify login redirection.
   - Navigate to **Curriculum**, **Labs**, **Simulator**, and **Challenges**.
   - Navigate to **Portfolio**, add a project, refresh the page, and confirm persistence.
   - Click **Logout** and verify session termination.
