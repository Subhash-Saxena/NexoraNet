# NexoraNet — Production Rollback & Incident Response Runbook

## 1. Overview
This runbook details contingency actions, database downgrades, and deployment rollback procedures in the event of an outage, regression, or infrastructure failure during production operations.

---

## 2. Fast Rollback Procedures

### 2.1 Frontend Static Rollback
- **Cloudflare Pages**:
  1. Open Cloudflare Pages dashboard -> Select Project -> **Deployments**.
  2. Find the last known healthy deployment commit.
  3. Click the three dots (`...`) -> **Rollback to this deployment**.
  4. Changes take effect globally within 15 seconds.
- **Vercel**:
  1. Open Vercel dashboard -> Select Project -> **Deployments**.
  2. Locate the previous working production deployment.
  3. Click **Instant Rollback**.

### 2.2 Backend Web Service Rollback (Render / Railway)
- **Render**:
  1. Navigate to the Web Service -> **Events**.
  2. Select the previously passing build event.
  3. Click **Rollback**.
  4. Render stops active containers and reverts traffic to the previous Docker image.
- **Railway**:
  1. Navigate to Deployments list.
  2. Click **Rollback** on the preceding healthy revision.

---

## 3. Database Migration Downgrades

If an Alembic migration fails or introduces an invalid column or constraint:

### 3.1 Step-by-Step Migration Reversal
```bash
# 1. Identify previous migration revision ID
python -m alembic history

# 2. Downgrade to target revision
python -m alembic downgrade -1
# OR downgrade to a specific revision:
python -m alembic downgrade <revision_id>

# 3. Verify current revision
python -m alembic current
```

---

## 4. Emergency Database Point-In-Time Restoration

If data corruption occurs:
1. Re-provision an empty database or clean existing schemas using `docs/backup-restore.md`.
2. Restore latest logical dump:
   ```bash
   pg_restore --clean --if-exists -d "$DATABASE_URL" backup_nexoranet_latest.dump
   ```
3. Run Alembic upgrade:
   ```bash
   python -m alembic upgrade head
   ```
4. Trigger `/api/ready` to confirm health.
