# NexoraNet — Database Backup & Disaster Recovery Guide

## 1. Overview
This runbook details disaster recovery, data backup, and restoration procedures for the NexoraNet PostgreSQL production database and local development SQLite environments.

---

## 2. PostgreSQL Production Backup & Restore

### 2.1 Automated Nightly Dump (Logical Backup)
To capture a full logical backup of schema and data using `pg_dump`:
```bash
# Set database URI
export DATABASE_URL="postgresql://user:password@host:5432/nexoranet"

# Create timestamped compressed backup
pg_dump -Fc --no-acl --no-owner "$DATABASE_URL" > "backup_nexoranet_$(date +%Y%m%d_%H%M%S).dump"
```

### 2.2 Schema-Only Backup
To capture only DDL without student telemetry or challenge attempts:
```bash
pg_dump --schema-only "$DATABASE_URL" > nexoranet_schema.sql
```

### 2.3 Disaster Recovery Restoration
To restore a fresh database from a compressed custom-format dump:
```bash
# 1. Terminate active sessions and recreate target database
psql "$ADMIN_DB_URL" -c "DROP DATABASE IF EXISTS nexoranet_prod;"
psql "$ADMIN_DB_URL" -c "CREATE DATABASE nexoranet_prod;"

# 2. Restore using pg_restore
pg_restore --clean --if-exists --no-acl --no-owner -d "$RESTORE_TARGET_URL" backup_nexoranet_YYYYMMDD_HHMMSS.dump

# 3. Verify Alembic migration version
python -m alembic current
```

---

## 3. SQLite Development / Staging Backup

For lightweight local instances:
```bash
# Vacuum into backup file while engine is active
sqlite3 nexoranet.db "VACUUM INTO 'nexoranet_backup_$(date +%Y%m%d).db';"
```

---

## 4. Verification & Integrity Checks

Following any restore event, perform these validation steps:
1. Run database readiness probe:
   ```bash
   curl -i http://localhost:8000/health/ready
   ```
2. Check total row counts across key seeded tables:
   ```sql
   SELECT count(*) FROM courses;
   SELECT count(*) FROM detection_rules;
   SELECT count(*) FROM challenges;
   ```
3. Run the automated integration test suite against the target DB:
   ```bash
   pytest backend/tests/test_step22_security_audit.py
   ```
