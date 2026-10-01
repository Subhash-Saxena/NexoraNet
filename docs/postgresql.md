# NexoraNet PostgreSQL Production Configuration & Migration Guide

This guide details configuring, optimizing, and operating PostgreSQL 16+ as the production database engine for NexoraNet.

---

## 1. Engine Configuration & Connection Pooling

NexoraNet uses SQLAlchemy 2.0 with connection pooling optimized for multi-worker container deployments:

```python
# Production Connection Pool Parameters
engine = create_engine(
    DATABASE_URL,
    pool_size=10,         # Persistent connections maintained in pool
    max_overflow=20,      # Additional temporary connections during high demand
    pool_timeout=30,      # Maximum wait time (seconds) before pool exhaustion error
    pool_recycle=300,     # Proactively renew connections every 5 minutes to avoid stale sockets
    pool_pre_ping=True,   # Execute test SELECT 1 to verify socket health before checkout
)
```

### URL Normalization for Cloud Hosts
Many managed cloud database providers (e.g., Render, Railway, Neon, Supabase) emit database connection strings starting with the legacy `postgres://` schema. NexoraNet automatically normalizes `postgres://` to `postgresql://` upon initialization, guaranteeing out-of-the-box compatibility with standard SQLAlchemy drivers.

---

## 2. Applying Database Migrations (Alembic)

To apply all database schema revisions against a target PostgreSQL instance:

```bash
# Ensure target DATABASE_URL is exported in your environment
export DATABASE_URL="postgresql://nexora:securepass@localhost:5432/nexoranet"

# Run Alembic migrations
cd backend
alembic upgrade head
```

---

## 3. Database Seeding in Production

After migrations are applied, populate standard curriculum modules, taxonomy, beginner/intermediate/advanced labs, and 28 cybersecurity skills:

```bash
python app/seed/seed_db.py
python app/services/challenges/seed_challenges.py
python app/services/soar/seed_soar_playbooks.py
python app/services/soc_scenarios/seed_soc_scenarios.py
python app/services/analytics/seed_step20_data.py
```

---

## 4. Backup & Disaster Recovery

### Creating a Snapshot Backup
```bash
pg_dump -U nexora -h localhost -d nexoranet -F c -b -v -f nexoranet_backup_$(date +%Y%m%d).dump
```

### Restoring from Backup
```bash
pg_restore -U nexora -h localhost -d nexoranet -v nexoranet_backup_20261001.dump
```
