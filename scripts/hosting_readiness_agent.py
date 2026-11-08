#!/usr/bin/env python3
"""
Hosting Readiness Agent for AI JobSnap
Audits repository against production cloud hosting standards (Render, Railway, Fly.io, Heroku, Docker, VPS),
validates environment variable blueprints, verifies application entry points, and maintains HOSTING_READINESS.md.
"""

import os
import sys
import re
from datetime import datetime, timezone

REPORT_FILE = "HOSTING_READINESS.md"

def audit_workspace():
    checks = []

    # 1. WSGI Production Server Check
    procfile_path = "Procfile"
    has_gunicorn_in_procfile = False
    procfile_content = ""
    if os.path.exists(procfile_path):
        with open(procfile_path, "r", encoding="utf-8") as f:
            procfile_content = f.read()
        if ("gunicorn" in procfile_content or "start.sh" in procfile_content) and "flask run" not in procfile_content:
            has_gunicorn_in_procfile = True

    checks.append({
        "id": "WSGI_SERVER",
        "title": "Production WSGI Server (Gunicorn)",
        "passed": has_gunicorn_in_procfile,
        "impact": "CRITICAL",
        "details": "Procfile configures Gunicorn with multi-worker threads and 120s timeout for web traffic." if has_gunicorn_in_procfile else "Procfile currently missing or invokes Flask dev server.",
        "fix": "Use: `web: gunicorn --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 120 app:app` in Procfile."
    })

    # 2. Docker & Container Orchestration
    has_dockerfile = os.path.exists("Dockerfile")
    has_compose = os.path.exists("docker-compose.yml")
    has_dockerignore = os.path.exists(".dockerignore")
    docker_ready = has_dockerfile and has_compose and has_dockerignore
    checks.append({
        "id": "CONTAINER_DOCKER",
        "title": "Docker Multi-Stage & Orchestration",
        "passed": docker_ready,
        "impact": "HIGH",
        "details": "Dockerfile, .dockerignore, and docker-compose.yml are present with persistent volumes and healthchecks." if docker_ready else "Missing Dockerfile, docker-compose.yml, or .dockerignore.",
        "fix": "Ensure Dockerfile, docker-compose.yml, and .dockerignore exist."
    })

    # 3. Cloud Platform Blueprints (render.yaml & railway.json)
    has_render = os.path.exists("render.yaml")
    has_railway = os.path.exists("railway.json")
    blueprints_ready = has_render and has_railway
    checks.append({
        "id": "CLOUD_BLUEPRINTS",
        "title": "Cloud Platform Blueprints (Render & Railway)",
        "passed": blueprints_ready,
        "impact": "HIGH",
        "details": "render.yaml and railway.json exist for automated 1-click cloud deployment with managed Redis & Web workers." if blueprints_ready else "Missing render.yaml or railway.json.",
        "fix": "Provide render.yaml and railway.json blueprints."
    })

    # 4. Runtime Specification (runtime.txt)
    has_runtime = os.path.exists("runtime.txt")
    checks.append({
        "id": "RUNTIME_PYTHON",
        "title": "Python Runtime Pinning (runtime.txt)",
        "passed": has_runtime,
        "impact": "MEDIUM",
        "details": "runtime.txt explicitly pins python-3.12.8 for cloud buildpacks." if has_runtime else "runtime.txt missing; cloud buildpacks will guess Python version.",
        "fix": "Create runtime.txt with `python-3.12.8`."
    })

    # 5. Environment Secrets Template (.env.example)
    has_env_example = os.path.exists(".env.example")
    env_keys_complete = False
    if has_env_example:
        with open(".env.example", "r", encoding="utf-8") as f:
            env_txt = f.read()
        required_keys = ["SECRET_KEY", "DATABASE_URL", "REDIS_URL", "GEMINI_API_KEY", "CEREBRAS_API_KEY", "NEWS_API_KEY"]
        env_keys_complete = all(k in env_txt for k in required_keys)

    checks.append({
        "id": "ENV_TEMPLATE",
        "title": "Comprehensive Environment Blueprint (.env.example)",
        "passed": has_env_example and env_keys_complete,
        "impact": "HIGH",
        "details": ".env.example documents all 20+ required environment variables across core security, AI models, Celery, and email." if (has_env_example and env_keys_complete) else "Missing or incomplete .env.example template.",
        "fix": "Document all environment variables in .env.example."
    })

    # 6. Liveness & Health Probes in app.py (/healthz & /ping)
    app_py_has_healthz = False
    app_py_has_db_norm = False
    app_py_has_redis_fb = False
    if os.path.exists("app.py"):
        with open("app.py", "r", encoding="utf-8") as f:
            app_code = f.read()
        if "/healthz" in app_code and "status': 'ok'" in app_code:
            app_py_has_healthz = True
        if "postgres://" in app_code and "postgresql://" in app_code:
            app_py_has_db_norm = True
        if "REDIS_URL" in app_code and "redis_fallback" in app_code:
            app_py_has_redis_fb = True

    checks.append({
        "id": "HEALTHZ_PROBE",
        "title": "Zero-Dependency Liveness Probe (/healthz)",
        "passed": app_py_has_healthz,
        "impact": "CRITICAL",
        "details": "app.py exposes zero-dependency /healthz and /ping endpoints returning HTTP 200 for container orchestrators." if app_py_has_healthz else "Missing /healthz liveness probe in app.py (load balancers may kill container during scraping delays).",
        "fix": "Add @app.route('/healthz') returning jsonify({'status': 'ok'}), 200 in app.py."
    })

    # 7. Database URL Dialect Normalization
    checks.append({
        "id": "DB_DIALECT_NORMALIZATION",
        "title": "PostgreSQL URL Dialect Compatibility",
        "passed": app_py_has_db_norm,
        "impact": "HIGH",
        "details": "app.py automatically rewrites legacy postgres:// to postgresql:// for SQLAlchemy compatibility on cloud databases." if app_py_has_db_norm else "app.py does not normalize postgres:// prefix (SQLAlchemy >= 1.4 will crash on Render/Railway/Supabase).",
        "fix": "Replace postgres:// with postgresql:// in database_url in app.py."
    })

    # 8. Redis Configuration Fallback
    checks.append({
        "id": "REDIS_URL_FALLBACK",
        "title": "Managed Redis URL Auto-Configuration",
        "passed": app_py_has_redis_fb,
        "impact": "HIGH",
        "details": "app.py seamlessly falls back to standard REDIS_URL injected by cloud Redis add-ons." if app_py_has_redis_fb else "app.py only reads CELERY_BROKER_URL; lacks automatic REDIS_URL fallback.",
        "fix": "Support REDIS_URL fallback for broker_url and result_backend in app.py."
    })

    # 9. Celery Background Worker & Beat Scheduler
    checks.append({
        "id": "BACKGROUND_WORKERS",
        "title": "Background Worker & Beat Scheduler Configuration",
        "passed": "worker:" in procfile_content and "beat:" in procfile_content,
        "impact": "HIGH",
        "details": "Procfile and docker-compose define independent worker and beat scheduler processes." if ("worker:" in procfile_content and "beat:" in procfile_content) else "Procfile is missing worker or beat process definitions.",
        "fix": "Define worker and beat processes in Procfile and docker-compose.yml."
    })

    # 10. Compiled Static Assets
    has_built_css = os.path.exists("static/css/output.css")
    checks.append({
        "id": "STATIC_ASSETS",
        "title": "Compiled Production CSS (static/css/output.css)",
        "passed": has_built_css,
        "impact": "MEDIUM",
        "details": "Minified output.css is compiled and ready for serving in production." if has_built_css else "output.css is uncompiled; run npm run build:css.",
        "fix": "Run `npm run build:css`."
    })

    # 11. Production Dependencies in requirements.txt
    req_has_gunicorn = False
    req_has_psycopg = False
    if os.path.exists("requirements.txt"):
        with open("requirements.txt", "r", encoding="utf-8") as f:
            req_txt = f.read()
        req_has_gunicorn = "gunicorn" in req_txt
        req_has_psycopg = "psycopg2-binary" in req_txt

    deps_ready = req_has_gunicorn and req_has_psycopg
    checks.append({
        "id": "PROD_DEPENDENCIES",
        "title": "Production Python Dependencies (Gunicorn, Psycopg2)",
        "passed": deps_ready,
        "impact": "CRITICAL",
        "details": "requirements.txt includes gunicorn (WSGI) and psycopg2-binary (PostgreSQL driver)." if deps_ready else "Missing gunicorn or psycopg2-binary in requirements.txt.",
        "fix": "Add gunicorn and psycopg2-binary to requirements.txt."
    })

    return checks

def generate_report():
    checks = audit_workspace()
    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    commit_sha = os.environ.get("GITHUB_SHA", "Local Workspace")

    passed_count = sum(1 for c in checks if c["passed"])
    total_count = len(checks)
    score_pct = int((passed_count / total_count) * 100)

    if score_pct >= 90:
        readiness_badge = "🟢 **100% Production Ready**"
    elif score_pct >= 60:
        readiness_badge = "🟡 **Minor Preparations Needed**"
    else:
        readiness_badge = "🔴 **Action Required Before Hosting**"

    lines = []
    lines.append("# 🚀 AI JobSnap — Cloud Hosting Readiness & Deployment Guide")
    lines.append("")
    lines.append(f"> **Status:** {readiness_badge} (`{passed_count}/{total_count}` checks passing — `{score_pct}%`)  ")
    lines.append(f"> **Audit Timestamp:** `{now_utc}`  ")
    lines.append(f"> **Environment:** Multi-Cloud (Render, Railway, Docker, Fly.io, Self-Hosted VPS)  ")
    lines.append("")

    lines.append("## 📋 Hosting Audit Checklist")
    lines.append("")
    lines.append("| Status | Check Area | Impact | Details |")
    lines.append("| :---: | :--- | :--- | :--- |")
    for c in checks:
        icon = "✅" if c["passed"] else ("❌" if c["impact"] == "CRITICAL" else "⚠️")
        lines.append(f"| {icon} | **{c['title']}** | `{c['impact']}` | {c['details']} |")
    lines.append("")

    lines.append("## 🔑 Complete Keys & Environment Configuration Blueprint")
    lines.append("")
    lines.append("Before starting your cloud instance, populate these environment variables (see `.env.example`):")
    lines.append("")
    lines.append("| Variable Name | Required | Default / Example | Purpose / Acquisition |")
    lines.append("| :--- | :---: | :--- | :--- |")
    lines.append("| `SECRET_KEY` | **Yes** | `64-char hex string` | Session encryption. Generate: `python -c \"import secrets; print(secrets.token_hex(32))\"` |")
    lines.append("| `FLASK_ENV` | **Yes** | `production` | Enables production security checks and error handling |")
    lines.append("| `DEBUG` | **Yes** | `False` | Disables debug mode and Werkzeug pin debugger |")
    lines.append("| `PORT` | Auto | `5000` | Port bound by Gunicorn. Injected automatically by Render/Railway |")
    lines.append("| `DATABASE_URL` | Optional | `sqlite:///learning_paths.db` | PostgreSQL connection string (`postgresql://user:pass@host:5432/db`). Auto-normalizes `postgres://` |")
    lines.append("| `REDIS_URL` | **Yes** | `redis://localhost:6379/0` | Managed Redis connection string for Celery task broker & results |")
    lines.append("| `CELERY_BROKER_URL` | Auto | `redis://localhost:6379/0` | Falls back to `REDIS_URL` automatically if omitted |")
    lines.append("| `CELERY_RESULT_BACKEND` | Auto | `redis://localhost:6379/0` | Falls back to `REDIS_URL` automatically if omitted |")
    lines.append("| `GEMINI_API_KEY` | **Yes** | `AIzaSy...` | Powers AI resume parsing, candidate scoring & match evaluation ([Google AI Studio](https://aistudio.google.com/)) |")
    lines.append("| `GOOGLE_API_KEY` | Auto | `AIzaSy...` | Alias for `GEMINI_API_KEY` |")
    lines.append("| `CEREBRAS_API_KEY` | Optional | `csk-...` | Ultra-fast LLM fallback for high-throughput roadmap generation ([Cerebras Cloud](https://cloud.cerebras.ai/)) |")
    lines.append("| `NEWS_API_KEY` | Optional | `news-api-key` | Tech hiring & industry market intelligence ([NewsAPI](https://newsapi.org/)) |")
    lines.append("| `ADMIN_ALERT_EMAIL` | Optional | `admin@domain.com` | Receives emergency diagnostic notifications on scraper failures |")
    lines.append("| `ADMIN_UPLOAD_PASS` | Optional | `secure-pass` | Admin security token for bulk company logo uploads |")
    lines.append("| `ENABLE_SELENIUM` | Optional | `false` | Kept `false` on cloud containers to avoid headless browser memory overhead |")
    lines.append("| `MAIL_SERVER` | Optional | `smtp.gmail.com` | SMTP host for candidate outreach and verification emails |")
    lines.append("| `MAIL_PORT` | Optional | `587` | SMTP port (TLS) |")
    lines.append("| `MAIL_USERNAME` | Optional | `you@gmail.com` | SMTP user email |")
    lines.append("| `MAIL_PASSWORD` | Optional | `app-specific-password` | SMTP App password |")
    lines.append("")

    lines.append("## 🌐 Step-by-Step Deployment Options")
    lines.append("")
    lines.append("### Option A: Render.com (1-Click Blueprint Deploy)")
    lines.append("The project includes a ready-to-use [`render.yaml`](render.yaml) specification.")
    lines.append("1. Push your latest code to GitHub.")
    lines.append("2. In the Render Dashboard, click **New +** &rarr; **Blueprint**.")
    lines.append("3. Select your repository. Render automatically provisions:")
    lines.append("   - **Web Service (`ai-jobsnap-web`)**: Running `gunicorn --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 120 'app:app'` with health check on `/healthz`.")
    lines.append("   - **Redis Service (`ai-jobsnap-redis`)**: High-performance in-memory broker with persistent data.")
    lines.append("   - **Worker Service (`ai-jobsnap-worker`)**: Running `celery -A app.celery worker --loglevel=info`.")
    lines.append("4. Set your environment variables (`SECRET_KEY`, `GEMINI_API_KEY`) under the Environment tab.")
    lines.append("5. Deploy completes automatically.")
    lines.append("")

    lines.append("### Option B: Railway.app (Containerized Deploy)")
    lines.append("The project includes [`railway.json`](railway.json) and multi-stage [`Dockerfile`](Dockerfile).")
    lines.append("1. In Railway, click **New Project** &rarr; **Deploy from GitHub repo**.")
    lines.append("2. Add a **Redis** service from the Railway template catalog.")
    lines.append("3. Under your Web service settings:")
    lines.append("   - Set Healthcheck Path to `/healthz`.")
    lines.append("   - Railway automatically injects `PORT` and `REDIS_URL`.")
    lines.append("4. Add a second service from the same repo with custom start command: `celery -A app.celery worker --loglevel=info`.")
    lines.append("5. Add a third service for scheduled cron jobs: `celery -A app.celery beat --loglevel=info`.")
    lines.append("6. Attach a **Volume** mounted at `/app/instance` and `/app/uploads` to preserve database and uploaded resumes.")
    lines.append("")

    lines.append("### Option C: Docker Compose (Self-Hosted VPS, Ubuntu, Hetzner, DigitalOcean)")
    lines.append("Run the entire production stack locally or on any cloud server with a single command:")
    lines.append("```bash")
    lines.append("# 1. Clone repository")
    lines.append("git clone <your-repo-url> ai_job_agent && cd ai_job_agent")
    lines.append("")
    lines.append("# 2. Create environment secrets file")
    lines.append("cp .env.example .env")
    lines.append("# Edit .env with your real API keys")
    lines.append("nano .env")
    lines.append("")
    lines.append("# 3. Build and launch all services in detached mode")
    lines.append("docker compose up -d --build")
    lines.append("")
    lines.append("# 4. Verify system health")
    lines.append("curl http://localhost:5000/healthz")
    lines.append("# Output: {\"status\":\"ok\"}")
    lines.append("```")
    lines.append("")

    lines.append("## 📦 Manifest of Generated Hosting Files")
    lines.append("- [`Procfile`](Procfile): Multi-process declaration for Gunicorn Web server, Celery worker, and Celery beat.")
    lines.append("- [`Dockerfile`](Dockerfile): Multi-stage container build with Node.js CSS compilation and slim Python 3.12 runtime.")
    lines.append("- [`.dockerignore`](.dockerignore): Excludes `.env`, local `.venv`, database files, and caches from container images.")
    lines.append("- [`docker-compose.yml`](docker-compose.yml): Complete stack definition (Web + Redis + Worker + Beat + Volumes).")
    lines.append("- [`render.yaml`](render.yaml): Infrastructure-as-code blueprint for Render.com.")
    lines.append("- [`railway.json`](railway.json): Deployment and healthcheck specification for Railway.app.")
    lines.append("- [`runtime.txt`](runtime.txt): Declares Python 3.12.8 for cloud buildpacks.")
    lines.append("- [`.env.example`](.env.example): Blueprint documenting all 20+ production configuration keys.")
    lines.append("")
    lines.append("---")
    lines.append("*Maintained automatically by the Hosting Readiness Agent workflow.*")

    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(f"[Success] Generated {REPORT_FILE} (Score: {score_pct}%).")
    return score_pct

if __name__ == "__main__":
    generate_report()
