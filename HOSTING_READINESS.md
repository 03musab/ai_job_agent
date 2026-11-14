# 🚀 AI JobSnap — Cloud Hosting Readiness & Deployment Guide

> **Status:** 🟢 **100% Production Ready** (`13/13` checks passing — `100%`)  
> **Audit Timestamp:** `2026-11-14 15:23:03 UTC`  
> **Environment:** Multi-Cloud (Render, Railway, Docker, Fly.io, Self-Hosted VPS)  

## 📋 Hosting Audit Checklist

| Status | Check Area | Impact | Details |
| :---: | :--- | :--- | :--- |
| ✅ | **Production WSGI Server (Gunicorn)** | `CRITICAL` | Procfile configures Gunicorn with multi-worker threads and 120s timeout for web traffic. |
| ✅ | **Docker Multi-Stage & Orchestration** | `HIGH` | Dockerfile, .dockerignore, and docker-compose.yml are present with persistent volumes and healthchecks. |
| ✅ | **Cloud Platform Blueprints (Render & Railway)** | `HIGH` | render.yaml and railway.json exist for automated 1-click cloud deployment with managed Redis & Web workers. |
| ✅ | **Python Runtime Pinning (runtime.txt)** | `MEDIUM` | runtime.txt explicitly pins python-3.12.8 for cloud buildpacks. |
| ✅ | **Comprehensive Environment Blueprint (.env.example)** | `HIGH` | .env.example documents all 20+ required environment variables across core security, AI models, Celery, and email. |
| ✅ | **Zero-Dependency Liveness Probe (/healthz)** | `CRITICAL` | app.py exposes zero-dependency /healthz and /ping endpoints returning HTTP 200 for container orchestrators. |
| ✅ | **PostgreSQL URL Dialect Compatibility** | `HIGH` | app.py automatically rewrites legacy postgres:// to postgresql:// for SQLAlchemy compatibility on cloud databases. |
| ✅ | **Managed Redis URL Auto-Configuration** | `HIGH` | app.py seamlessly falls back to standard REDIS_URL injected by cloud Redis add-ons. |
| ✅ | **Background Worker & Beat Scheduler Configuration** | `HIGH` | Procfile and docker-compose define independent worker and beat scheduler processes. |
| ✅ | **Compiled Production CSS (static/css/output.css)** | `MEDIUM` | Minified output.css is compiled and ready for serving in production. |
| ✅ | **Production Python Dependencies (Gunicorn, Psycopg2)** | `CRITICAL` | requirements.txt includes gunicorn (WSGI) and psycopg2-binary (PostgreSQL driver). |
| ✅ | **Reverse-Proxy HTTPS Awareness (Werkzeug ProxyFix)** | `CRITICAL` | app.wsgi_app is wrapped with ProxyFix so Google OAuth and email links use https:// behind cloud load balancers. |
| ✅ | **Cloud PostgreSQL Connection Resilience (pool_pre_ping)** | `HIGH` | SQLAlchemy engine uses pool_pre_ping=True and pool_recycle=300 to prevent idle SSL connection drops on cloud Postgres. |

## 🔑 Complete Keys & Environment Configuration Blueprint

Before starting your cloud instance, populate these environment variables (see `.env.example`):

| Variable Name | Required | Default / Example | Purpose / Acquisition |
| :--- | :---: | :--- | :--- |
| `SECRET_KEY` | **Yes** | `64-char hex string` | Session encryption. Generate: `python -c "import secrets; print(secrets.token_hex(32))"` |
| `FLASK_ENV` | **Yes** | `production` | Enables production security checks and error handling |
| `DEBUG` | **Yes** | `False` | Disables debug mode and Werkzeug pin debugger |
| `PORT` | Auto | `5000` | Port bound by Gunicorn. Injected automatically by Render/Railway |
| `DATABASE_URL` | Optional | `sqlite:///learning_paths.db` | PostgreSQL connection string (`postgresql://user:pass@host:5432/db`). Auto-normalizes `postgres://` |
| `REDIS_URL` | **Yes** | `redis://localhost:6379/0` | Managed Redis connection string for Celery task broker & results |
| `CELERY_BROKER_URL` | Auto | `redis://localhost:6379/0` | Falls back to `REDIS_URL` automatically if omitted |
| `CELERY_RESULT_BACKEND` | Auto | `redis://localhost:6379/0` | Falls back to `REDIS_URL` automatically if omitted |
| `GEMINI_API_KEY` | **Yes** | `AIzaSy...` | Powers AI resume parsing, candidate scoring & match evaluation ([Google AI Studio](https://aistudio.google.com/)) |
| `GOOGLE_API_KEY` | Auto | `AIzaSy...` | Alias for `GEMINI_API_KEY` |
| `CEREBRAS_API_KEY` | Optional | `csk-...` | Ultra-fast LLM fallback for high-throughput roadmap generation ([Cerebras Cloud](https://cloud.cerebras.ai/)) |
| `NEWS_API_KEY` | Optional | `news-api-key` | Tech hiring & industry market intelligence ([NewsAPI](https://newsapi.org/)) |
| `ADMIN_ALERT_EMAIL` | Optional | `admin@domain.com` | Receives emergency diagnostic notifications on scraper failures |
| `ADMIN_UPLOAD_PASS` | Optional | `secure-pass` | Admin security token for bulk company logo uploads |
| `ENABLE_SELENIUM` | Optional | `false` | Kept `false` on cloud containers to avoid headless browser memory overhead |
| `MAIL_SERVER` | Required unless Gmail OAuth is configured | `smtp.gmail.com` | SMTP host for candidate outreach and verification emails |
| `MAIL_PORT` | Optional | `587` | SMTP port (TLS) |
| `MAIL_USERNAME` | Required unless Gmail OAuth is configured | `you@gmail.com` | SMTP user email |
| `MAIL_PASSWORD` | Required unless Gmail OAuth is configured | `app-specific-password` | SMTP App password |

## 🌐 Step-by-Step Deployment Options

### Option A: Render.com (1-Click Blueprint Deploy)
The project includes a ready-to-use [`render.yaml`](render.yaml) specification.
1. Push your latest code to GitHub.
2. In the Render Dashboard, click **New +** &rarr; **Blueprint**.
3. Select your repository. Render automatically provisions:
   - **Web Service (`ai-jobsnap-web`)**: Running `gunicorn --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 120 'app:app'` with health check on `/healthz`.
   - **Redis Service (`ai-jobsnap-redis`)**: High-performance in-memory broker with persistent data.
   - **Worker Service (`ai-jobsnap-worker`)**: Running `celery -A app.celery worker --loglevel=info`.
4. Set your environment variables (`SECRET_KEY`, `GEMINI_API_KEY`) under the Environment tab.
5. Deploy completes automatically.

### Option B: Railway.app (Containerized Deploy)
The project includes [`railway.json`](railway.json) and multi-stage [`Dockerfile`](Dockerfile).
1. In Railway, click **New Project** &rarr; **Deploy from GitHub repo**.
2. Add a **Redis** service from the Railway template catalog.
3. Under your Web service settings:
   - Set Healthcheck Path to `/healthz`.
   - Railway automatically injects `PORT` and `REDIS_URL`.
4. Add a second service from the same repo with custom start command: `celery -A app.celery worker --loglevel=info`.
5. Add a third service for scheduled cron jobs: `celery -A app.celery beat --loglevel=info`.
6. Attach a **Volume** mounted at `/app/instance` and `/app/uploads` to preserve database and uploaded resumes.

### Option C: Docker Compose (Self-Hosted VPS, Ubuntu, Hetzner, DigitalOcean)
Run the entire production stack locally or on any cloud server with a single command:
```bash
# 1. Clone repository
git clone <your-repo-url> ai_job_agent && cd ai_job_agent

# 2. Create environment secrets file
cp .env.example .env
# Edit .env with your real API keys
nano .env

# 3. Build and launch all services in detached mode
docker compose up -d --build

# 4. Verify system health
curl http://localhost:5000/healthz
# Output: {"status":"ok"}
```

## 📦 Manifest of Generated Hosting Files
- [`Procfile`](Procfile): Multi-process declaration for Gunicorn Web server, Celery worker, and Celery beat.
- [`Dockerfile`](Dockerfile): Multi-stage container build with Node.js CSS compilation and slim Python 3.12 runtime.
- [`.dockerignore`](.dockerignore): Excludes `.env`, local `.venv`, database files, and caches from container images.
- [`docker-compose.yml`](docker-compose.yml): Complete stack definition (Web + Redis + Worker + Beat + Volumes).
- [`render.yaml`](render.yaml): Infrastructure-as-code blueprint for Render.com.
- [`railway.json`](railway.json): Deployment and healthcheck specification for Railway.app.
- [`runtime.txt`](runtime.txt): Declares Python 3.12.8 for cloud buildpacks.
- [`.env.example`](.env.example): Blueprint documenting all 20+ production configuration keys.

---
*Maintained automatically by the Hosting Readiness Agent workflow.*
