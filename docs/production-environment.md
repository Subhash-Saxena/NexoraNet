# NexoraNet — Production Environment Configuration

## 1. Overview
This document defines the production environment specifications, variable definitions, and security policies for **NexoraNet** ("*Learn. Simulate. Analyze. Defend.*").

---

## 2. Environment Variables Specification

### 2.1 Backend Environment Variables

| Variable Name | Required | Default | Example Value | Description |
| :--- | :---: | :---: | :--- | :--- |
| `ENVIRONMENT` | **Yes** | `development` | `production` | Runtime mode. When set to `production`, fail-fast security validations are enforced at boot. |
| `DEBUG` | **Yes** | `True` | `False` | Disables debug mode, interactive stack traces, and verbose error reflections. Must be `False` in production. |
| `DATABASE_URL` | **Yes** | `sqlite:///...` | `postgresql://user:pass@host:5432/nexoranet` | PostgreSQL connection string. Legacy `postgres://` URLs are automatically normalized to `postgresql://`. SQLite is strictly prohibited in production. |
| `SECRET_KEY` | **Yes** | - | `<generated-64-character-secret>` | Cryptographic secret for signing sessions and fallback authentication. Minimum 32 characters required. |
| `JWT_SECRET_KEY` | Optional | `SECRET_KEY` | `<generated-64-character-secret>` | Dedicated secret key for signing HS256 JWT bearer access tokens. |
| `JWT_ALGORITHM` | No | `HS256` | `HS256` | JWT signing algorithm. |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | `60` | `60` | Lifespan of issued student and admin JWT bearer tokens. |
| `CORS_ORIGINS` | **Yes** | - | `https://nexoranet.pages.dev` | Comma-separated list or JSON array of allowed origins. Wildcards (`*`) and `localhost` entries are strictly forbidden in production. |
| `RATE_LIMIT_LOGIN_PER_MINUTE` | No | `10` | `10` | Maximum login/registration attempts per minute per IP address. |
| `RATE_LIMIT_FLAG_PER_MINUTE` | No | `30` | `30` | Maximum CTF challenge flag submissions per minute per student. |
| `DB_POOL_SIZE` | No | `5` | `10` | SQLAlchemy 2.0 connection pool base capacity. |
| `DB_MAX_OVERFLOW` | No | `10` | `20` | Maximum temporary connection pool overflow under high concurrent load. |
| `DB_POOL_TIMEOUT` | No | `30` | `30` | Maximum seconds to wait for a database connection before raising an exception. |
| `DB_POOL_RECYCLE` | No | `300` | `300` | Seconds after which idle database connections are refreshed. |
| `STRICT_SECURITY_HEADERS` | No | `True` | `True` | Injects CSP, HSTS, X-Content-Type-Options, X-Frame-Options, and Referrer-Policy headers. |

### 2.2 Frontend Environment Variables

| Variable Name | Required | Default | Example Value | Description |
| :--- | :---: | :---: | :--- | :--- |
| `VITE_API_URL` | Optional | `""` | `https://nexoranet-api.onrender.com` | Production backend API origin. If omitted, relative paths `/api/...` are used (for reverse proxies or `_redirects`). |

---

## 3. Cryptographic Secret Generation Commands

Generate distinct, high-entropy secrets using Python's cryptographic `secrets` module:

```bash
# Generate SECRET_KEY:
python -c "import secrets; print(secrets.token_urlsafe(48))"

# Generate JWT_SECRET_KEY:
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

> [!CAUTION]
> Never commit real secrets to Git or share them in plaintext. Store them exclusively in your hosting provider's encrypted environment variables dashboard.

---

## 4. Free-Tier Cloud Provider Recommendations

NexoraNet is engineered to operate 100% within verified zero-cost free tiers:

1. **Database Tier (PostgreSQL)**:
   - **Neon** (https://neon.tech): Free tier offers 0.5 GB storage, serverless autosuspend, and standard PostgreSQL connection strings.
   - **Supabase** (https://supabase.com): Free tier offers 500 MB database, pooled connection URI (`Transaction Pooler` on port 6543 or direct port 5432).
2. **Backend Web Service**:
   - **Render** (https://render.com): Free Web Service running Docker or native Python with automatic HTTPS and `/api/health` probes.
   - **Railway** (https://railway.app): Starter plan with free monthly execution credits.
3. **Frontend Static Hosting**:
   - **Cloudflare Pages** (https://pages.cloudflare.com): 100% free unlimited static bandwidth, automated global edge CDN, and built-in SPA routing via `_redirects`.
   - **Vercel** (https://vercel.com): Free Hobby tier with unlimited deployments and SPA routing via `vercel.json`.
