# NexoraNet Environment Configuration Guide

This guide details all environment configuration variables used across local development, testing, staging, and production environments.

---

## Configuration Variables Reference

| Variable | Type | Default (Dev) | Description |
| :--- | :--- | :--- | :--- |
| `ENVIRONMENT` | string | `development` | Target lifecycle mode (`development`, `testing`, `staging`, `production`). Enforces strict security invariants in production. |
| `DEBUG` | boolean | `True` | Enables FastAPI auto-reload and SQLAlchemy query echoing. Must be `False` in production. |
| `BACKEND_HOST` | string | `0.0.0.0` | IP interface to which the backend server binds. |
| `BACKEND_PORT` | integer | `8000` | Port on which FastAPI listens for incoming HTTP requests. |
| `DATABASE_URL` | string | `sqlite:///./nexoranet.db` | SQLAlchemy connection string. SQLite for development; PostgreSQL for production. Legacy `postgres://` URLs are automatically normalized to `postgresql://`. |
| `DB_POOL_SIZE` | integer | `5` | Maximum number of persistent connections held open in the PostgreSQL pool. |
| `DB_MAX_OVERFLOW` | integer | `10` | Maximum number of transient connections that can be opened beyond `DB_POOL_SIZE`. |
| `DB_POOL_TIMEOUT` | integer | `30` | Seconds to wait before timing out on connection pool exhaustion. |
| `DB_POOL_RECYCLE` | integer | `300` | Seconds after which idle database connections are refreshed. |
| `CORS_ORIGINS` | string / list | `http://localhost:5173,...` | Comma-delimited list of permitted CORS frontend domains. Wildcards (`*`) and localhost are prohibited in production. |
| `SECRET_KEY` | string | *dev placeholder* | Master cryptographic secret. In production, must be at least 32 characters and cryptographically random. |
| `JWT_SECRET_KEY` | string | *None* | Optional dedicated signing key for JWT tokens. Falls back to `SECRET_KEY` if omitted. |
| `JWT_ALGORITHM` | string | `HS256` | Cryptographic algorithm for JWT signatures. |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | integer | `60` | Lifespan of issued JWT access tokens before expiration. |
| `RATE_LIMIT_LOGIN_PER_MINUTE` | integer | `10` | Maximum login/registration attempts per client IP in a 60-second sliding window. |
| `RATE_LIMIT_FLAG_PER_MINUTE` | integer | `30` | Maximum flag submissions per client IP in a 60-second sliding window. |
| `STRICT_SECURITY_HEADERS` | boolean | `True` | Attaches CSP, HSTS, X-Frame-Options, and X-Content-Type-Options headers. |
| `LAB_ALLOWED_SUBNET` | string (CIDR) | `10.99.0.0/16` | Permitted virtual lab subnet for safe synthetic network simulations. |

---

## Development vs Production Comparison

| Parameter | Development | Production |
| :--- | :--- | :--- |
| `ENVIRONMENT` | `development` | `production` |
| `DEBUG` | `True` | `False` |
| `DATABASE_URL` | `sqlite:///./nexoranet.db` | `postgresql://user:pass@host:5432/dbname` |
| `SECRET_KEY` | Dev default permitted | Random 32+ character string required |
| `CORS_ORIGINS` | `localhost:5173`, `localhost:3000` | Fully qualified production HTTPS domains |
| `Dev Header Auth` | Supported (`X-User-Role`) | Strictly disabled (Bearer JWT only) |
| `HSTS Header` | Not attached | `max-age=31536000; includeSubDomains` |
