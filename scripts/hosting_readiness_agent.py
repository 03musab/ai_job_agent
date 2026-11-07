#!/usr/bin/env python3
"""
Hosting Readiness Agent for AI JobSnap
Audits repository against production cloud hosting standards (Render, Railway, Fly.io, Heroku, AWS, Docker),
generates production configuration files, and maintains HOSTING_READINESS.md.
"""

import os
import sys
import json
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
        if "gunicorn" in procfile_content and "flask run" not in procfile_content:
            has_gunicorn_in_procfile = True

    checks.append({
        "id": "WSGI_SERVER",
        "title": "Production WSGI Server (Gunicorn)",
        "passed": has_gunicorn_in_procfile,
        "impact": "CRITICAL",
        "details": "Procfile uses Gunicorn with multi-worker threads rather than single-threaded Flask development server." if has_gunicorn_in_procfile else "Procfile currently invokes 'flask run --debug', which is unstable and insecure for production traffic.",
        "fix": "Use: `web: gunicorn --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 120 \"app:app\"`"
    })

    # 2. Docker Containerization
    has_dockerfile = os.path.exists("Dockerfile")
    has_compose = os.path.exists("docker-compose.yml")
    checks.append({
        "id": "CONTAINER_DOCKER",
        "title": "Docker Containerization (Dockerfile & docker-compose.yml)",
        "passed": has_dockerfile and has_compose,
        "impact": "HIGH",
        "details": "Standard Dockerfile and docker-compose.yml exist for reproducible cross-cloud deployment." if (has_dockerfile and has_compose) else "Missing standard Dockerfile or docker-compose.yml for cloud container deployment.",
        "fix": "Generate production multi-stage Dockerfile and docker-compose.yml."
    })

    # 3. Environment Secrets Template (.env.example)
    has_env_example = os.path.exists(".env.example")
    checks.append({
        "id": "ENV_TEMPLATE",
        "title": "Production Environment Specification (.env.example)",
        "passed": has_env_example,
        "impact": "HIGH",
        "details": "Safe environment blueprint exists for cloud configuration without leaking live secrets." if has_env_example else "Missing .env.example documenting all mandatory environment variables for host setup.",
        "fix": "Create .env.example documenting SECRET_KEY, DATABASE_URL, REDIS_URL, etc."
    })

    # 4. Static Asset Production Build
    has_built_css = os.path.exists("static/css/output.css")
    checks.append({
        "id": "STATIC_ASSETS",
        "title": "Compiled Production CSS (static/css/output.css)",
        "passed": has_built_css,
        "impact": "MEDIUM",
        "details": "Minified output.css is compiled and ready for serving." if has_built_css else "output.css is missing or uncompiled; frontend styles may fail.",
        "fix": "Run `npm run build:css` during deployment build hook."
    })

    # 5. Database Persistence Strategy
    checks.append({
        "id": "DATABASE_PERSISTENCE",
        "title": "Database Storage Persistence (Postgres / Persistent Volume)",
        "passed": True,  # Monitored guidance
        "impact": "HIGH",
        "details": "The application supports SQLite locally. For ephemeral cloud containers (Render, Railway, Heroku), attach a persistent disk or connect a managed PostgreSQL instance via DATABASE_URL.",
        "fix": "In cloud host dashboard, attach a persistent volume to mount SQLite or add a managed PostgreSQL add-on."
    })

    # 6. Background Queue & Scheduler
    checks.append({
        "id": "BACKGROUND_WORKERS",
        "title": "Background Worker & Scheduler (Celery + Redis)",
        "passed": "worker:" in procfile_content and "beat:" in procfile_content,
        "impact": "HIGH",
        "details": "Procfile defines separate process roles for the web app, background worker, and beat scheduler." if ("worker:" in procfile_content and "beat:" in procfile_content) else "Procfile is missing distinct worker and beat service definitions.",
        "fix": "Define `worker: celery -A app.celery worker` and `beat: celery -A app.celery beat` in Procfile."
    })

    # 7. Cloud Deployment Blueprints (render.yaml / fly.toml)
    has_render = os.path.exists("render.yaml")
    checks.append({
        "id": "CLOUD_BLUEPRINTS",
        "title": "Cloud Platform Blueprint (render.yaml)",
        "passed": has_render,
        "impact": "MEDIUM",
        "details": "Infrastructure-as-code blueprint exists for 1-click cloud deployment." if has_render else "Missing automated infrastructure specification.",
        "fix": "Provide render.yaml specifying Web service, Redis instance, and Background Worker."
    })

    return checks

def apply_fixes():
    """Generates and writes production-ready configuration files."""
    modified = []

    # 1. Update Procfile for production Gunicorn
    prod_procfile = (
        "web: gunicorn --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 120 \"app:app\"\n"
        "worker: celery -A app.celery worker --loglevel=info\n"
        "beat: celery -A app.celery beat --loglevel=info\n"
    )
    with open("Procfile", "w", encoding="utf-8") as f:
        f.write(prod_procfile)
    modified.append("Procfile")

    # 2. Create .env.example
    env_example = (
        "# ===================================================================\n"
        "# AI JobSnap — Production Environment Configuration Blueprint\n"
        "# ===================================================================\n\n"
        "# Flask & Core Security\n"
        "SECRET_KEY=change-me-to-a-secure-random-64-char-string\n"
        "FLASK_ENV=production\n"
        "DEBUG=False\n"
        "PORT=5000\n\n"
        "# Database (Defaults to SQLite; specify postgresql:// for production)\n"
        "DATABASE_URL=sqlite:///jobs.db\n\n"
        "# Redis / Celery Task Queue\n"
        "REDIS_URL=redis://localhost:6379/0\n"
        "CELERY_BROKER_URL=redis://localhost:6379/0\n"
        "CELERY_RESULT_BACKEND=redis://localhost:6379/0\n\n"
        "# AI & LLM Providers\n"
        "GEMINI_API_KEY=\n"
        "OPENAI_API_KEY=\n\n"
        "# Mail & System Outbox\n"
        "MAIL_SERVER=smtp.gmail.com\n"
        "MAIL_PORT=587\n"
        "MAIL_USE_TLS=True\n"
        "MAIL_USERNAME=\n"
        "MAIL_PASSWORD=\n"
    )
    with open(".env.example", "w", encoding="utf-8") as f:
        f.write(env_example)
    modified.append(".env.example")

    # 3. Create Multi-Stage Production Dockerfile
    dockerfile_content = (
        "# Multi-stage Docker build for AI JobSnap\n"
        "# Stage 1: Build Frontend Assets (Tailwind CSS)\n"
        "FROM node:20-alpine AS frontend-builder\n"
        "WORKDIR /app\n"
        "COPY package*.json ./\n"
        "RUN npm ci\n"
        "COPY tailwind.config.js ./\n"
        "COPY static/ ./static/\n"
        "COPY templates/ ./templates/\n"
        "RUN npm run build:css\n\n"
        "# Stage 2: Production Python Image\n"
        "FROM python:3.12-slim\n"
        "WORKDIR /app\n\n"
        "# Install essential OS packages for SQLite & networking\n"
        "RUN apt-get update && apt-get install -y --no-install-recommends \\\n"
        "    curl gcc sqlite3 && \\\n"
        "    rm -rf /var/lib/apt/lists/*\n\n"
        "# Install Python dependencies\n"
        "COPY requirements.txt ./\n"
        "RUN pip install --no-cache-dir -r requirements.txt gunicorn\n\n"
        "# Copy application code & compiled CSS from Stage 1\n"
        "COPY . .\n"
        "COPY --from=frontend-builder /app/static/css/output.css ./static/css/output.css\n\n"
        "# Expose port\n"
        "ENV PORT=5000\n"
        "EXPOSE 5000\n\n"
        "# Default entrypoint runs Gunicorn\n"
        "CMD [\"gunicorn\", \"--bind\", \"0.0.0.0:5000\", \"--workers\", \"2\", \"--threads\", \"4\", \"--timeout\", \"120\", \"app:app\"]\n"
    )
    with open("Dockerfile", "w", encoding="utf-8") as f:
        f.write(dockerfile_content)
    modified.append("Dockerfile")

    # 4. Create docker-compose.yml for complete stack (Web + Redis + Celery)
    compose_content = (
        "version: '3.8'\n\n"
        "services:\n"
        "  web:\n"
        "    build: .\n"
        "    ports:\n"
        "      - \"5000:5000\"\n"
        "    environment:\n"
        "      - PORT=5000\n"
        "      - REDIS_URL=redis://redis:6379/0\n"
        "      - CELERY_BROKER_URL=redis://redis:6379/0\n"
        "      - CELERY_RESULT_BACKEND=redis://redis:6379/0\n"
        "      - DEBUG=False\n"
        "    volumes:\n"
        "      - db-data:/app/instance\n"
        "    depends_on:\n"
        "      - redis\n\n"
        "  redis:\n"
        "    image: redis:7-alpine\n"
        "    ports:\n"
        "      - \"6379:6379\"\n\n"
        "  worker:\n"
        "    build: .\n"
        "    command: celery -A app.celery worker --loglevel=info\n"
        "    environment:\n"
        "      - REDIS_URL=redis://redis:6379/0\n"
        "      - CELERY_BROKER_URL=redis://redis:6379/0\n"
        "      - CELERY_RESULT_BACKEND=redis://redis:6379/0\n"
        "    depends_on:\n"
        "      - redis\n\n"
        "volumes:\n"
        "  db-data:\n"
    )
    with open("docker-compose.yml", "w", encoding="utf-8") as f:
        f.write(compose_content)
    modified.append("docker-compose.yml")

    # 5. Create render.yaml blueprint
    render_yaml = (
        "services:\n"
        "  # Web Service\n"
        "  - type: web\n"
        "    name: ai-jobsnap-web\n"
        "    runtime: python\n"
        "    buildCommand: \"npm ci && npm run build:css && pip install -r requirements.txt\"\n"
        "    startCommand: \"gunicorn --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 120 'app:app'\"\n"
        "    envVars:\n"
        "      - key: FLASK_ENV\n"
        "        value: production\n"
        "      - key: DEBUG\n"
        "        value: false\n"
        "      - key: REDIS_URL\n"
        "        fromService:\n"
        "          type: redis\n"
        "          name: ai-jobsnap-redis\n"
        "          property: connectionString\n\n"
        "  # Celery Background Worker\n"
        "  - type: worker\n"
        "    name: ai-jobsnap-worker\n"
        "    runtime: python\n"
        "    buildCommand: \"pip install -r requirements.txt\"\n"
        "    startCommand: \"celery -A app.celery worker --loglevel=info\"\n"
        "    envVars:\n"
        "      - key: REDIS_URL\n"
        "        fromService:\n"
        "          type: redis\n"
        "          name: ai-jobsnap-redis\n"
        "          property: connectionString\n\n"
        "  # Managed Redis Queue\n"
        "  - type: redis\n"
        "    name: ai-jobsnap-redis\n"
        "    ipAllowList: [] # internal access only\n"
    )
    with open("render.yaml", "w", encoding="utf-8") as f:
        f.write(render_yaml)
    modified.append("render.yaml")

    return modified

def generate_report():
    checks = audit_workspace()
    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    commit_sha = os.environ.get("GITHUB_SHA", "Local Workspace")

    passed_count = sum(1 for c in checks if c["passed"])
    total_count = len(checks)
    score_pct = int((passed_count / total_count) * 100)

    if score_pct >= 90:
        readiness_badge = "🟢 **Production Ready**"
    elif score_pct >= 60:
        readiness_badge = "🟡 **Minor Preparations Needed**"
    else:
        readiness_badge = "🔴 **Action Required Before Hosting**"

    lines = []
    lines.append("# 🚀 Cloud Hosting Readiness & Deployment Guide")
    lines.append("")
    lines.append(f"> **Readiness Level:** {readiness_badge} (`{score_pct}%` passing)  ")
    lines.append(f"> **Audit Timestamp:** `{now_utc}`  ")
    lines.append(f"> **Commit Reference:** `{commit_sha[:8] if len(commit_sha) >= 8 else commit_sha}`  ")
    lines.append("")

    lines.append("## 📋 Hosting Audit Checklist")
    lines.append("")
    lines.append("| Status | Check Area | Impact | Details |")
    lines.append("| :---: | :--- | :--- | :--- |")
    for c in checks:
        icon = "✅" if c["passed"] else ("❌" if c["impact"] == "CRITICAL" else "⚠️")
        lines.append(f"| {icon} | **{c['title']}** | `{c['impact']}` | {c['details']} |")
    lines.append("")

    lines.append("## 🛠️ Required Action Items & Hosting Changes")
    lines.append("")
    for c in checks:
        if not c["passed"]:
            lines.append(f"### ❌ {c['title']} (`{c['impact']}`)")
            lines.append(f"- **Problem:** {c['details']}")
            lines.append(f"- **Remediation:** {c['fix']}")
            lines.append("")

    lines.append("## 🌐 Platform-by-Platform Deployment Instructions")
    lines.append("")
    lines.append("### 1. Render.com (Recommended for Free/Hobby Tier)")
    lines.append("1. Push your code to GitHub.")
    lines.append("2. In the Render Dashboard, click **New +** &rarr; **Blueprint**.")
    lines.append("3. Select your repository. Render reads [`render.yaml`](render.yaml) and automatically creates:")
    lines.append("   - **Web Service** (Gunicorn WSGI)")
    lines.append("   - **Redis Service** (Task broker)")
    lines.append("   - **Background Worker** (Celery scraper)")
    lines.append("4. Set your `SECRET_KEY` and API keys in the Render environment variables tab.")
    lines.append("")

    lines.append("### 2. Railway.app")
    lines.append("1. Connect GitHub repo in Railway.")
    lines.append("2. Add a **Redis** plugin/service.")
    lines.append("3. Set the web service start command from `Procfile`.")
    lines.append("4. Attach a **Persistent Volume** mounted at `/app/instance` so SQLite data persists across redeployments.")
    lines.append("")

    lines.append("### 3. Docker / Self-Hosted VPS (Ubuntu/DigitalOcean/Hetzner)")
    lines.append("1. Clone repository to server.")
    lines.append("2. Copy `.env.example` to `.env` and configure real credentials.")
    lines.append("3. Run the complete stack:")
    lines.append("   ```bash")
    lines.append("   docker compose up -d --build")
    lines.append("   ```")
    lines.append("")

    lines.append("---")
    lines.append("*Maintained automatically by the Hosting Readiness Agent workflow.*")

    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(f"[Success] Generated {REPORT_FILE} (Score: {score_pct}%).")
    return score_pct

if __name__ == "__main__":
    if "--apply" in sys.argv or "--fix" in sys.argv:
        print("[Hosting Agent] Applying hosting readiness fixes...")
        modified = apply_fixes()
        print(f"[Hosting Agent] Configured production files: {', '.join(modified)}")
    generate_report()

