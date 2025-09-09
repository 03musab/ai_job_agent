# 📘 Project Best Practices

## 1. Project Purpose
This project is a Flask-based “Job Hunter” web application that helps users search and track jobs across multiple sources (currently LinkedIn and Internshala). It features user authentication, saved search profiles, background scraping via Celery workers, job scoring and deduplication, a management dashboard for tracking application status, and automated email reports (including optional Excel attachments) via the Gmail API.

## 2. Project Structure
- app.py
  - Flask application initialization and configuration
  - Celery configuration with scheduled tasks (Celery Beat)
  - Data model and services in one module:
    - dataclass Job: in-memory representation of a job
    - User (Flask-Login-compatible)
    - JobDatabase: SQLite schema creation/migrations and all DB I/O
    - EnhancedJobScraper: scrapers (LinkedIn, Internshala), enrichment, scoring, deduplication
    - SmartEmailer: Gmail API auth, HTML email builder, Excel report generation
    - Jinja2 filter: clean_desc
  - Flask routes (views):
    - GET /health – system readiness probe (pings Celery)
    - GET / – redirect to /dashboard or /login depending on auth status
    - GET, POST /register – user registration
    - GET, POST /login – user login
    - GET /logout – logout
    - GET /dashboard – job list with pagination, sorting, status filters, and search
    - POST /search_jobs – trigger background scraping task
    - POST /save_profile – save a search profile
    - POST /delete_profile/<id> – delete a search profile
    - POST /apply_profile/<id> – run scraping using a saved profile
    - POST /delete_job/<id> – delete a single job
    - POST /delete_selected – bulk delete jobs
    - POST /delete_all_jobs – delete all jobs for current user
    - POST /update_settings – email notification settings
    - POST /update_job_status – update status/notes for a job
    - POST /feedback – like/dislike feedback
  - Celery tasks:
    - app.run_job_hunt_task(user_id, search_terms, location, experience, job_type)
    - app.scheduled_job_hunt_for_all_users() – scheduled twice daily via Celery Beat (09:00 and 18:00 UTC)

- templates/
  - base.html – layout (Bootstrap), navbar, footer, flash handling
  - login.html – login form
  - register.html – registration form
  - dashboard.html – search form, saved profiles, email settings, jobs table, modal, pagination, and client-side helpers

- requirements.txt – Python dependencies
- Procfile – process definitions (web app and Celery beat); add a worker process when deploying
- jobs.db – SQLite database (runtime)
- test_webdriver_launch.py – selenium driver launcher checks (pytest-compatible functions)
- credentials.json / token.pickle – Google API credentials and OAuth tokens (runtime)
- .env – environment variables (not committed; used by utilities/tests)

Notes
- The project is primarily a single-module backend with Jinja templates. Consider modularization (e.g., package with /db, /scrapers, /email, /web) for larger changes.

## 3. Test Strategy
- Frameworks
  - pytest is present in requirements and tests are written in a pytest-compatible style (functions prefixed with test_). Current code includes an ad-hoc WebDriver test script.

- Organization
  - Current tests: test_webdriver_launch.py at project root.
  - Recommended: move tests into tests/ with the following split:
    - tests/unit/ for pure functions (parsing, scoring, utils)
    - tests/integration/ for DB methods, Celery tasks (eager mode), email formatting
    - tests/functional/ for Flask routes (using app.test_client())

- Naming conventions
  - test_<module>_<feature>.py, functions named test_<case>.

- Mocking & isolation guidelines
  - Network I/O (requests): use responses or requests-mock; disable real HTTP in CI.
  - Selenium: mark end-to-end tests as slow; use WebDriver Manager or skip in CI; avoid relying on gevent monkey patch.
  - Gmail API: mock googleapiclient.discovery.build and token refresh flow; never hit real Gmail in tests.
  - SQLite: use in-memory DB (db_path=':memory:') or a temp file; avoid mutating jobs.db in tests.
  - Celery: configure in tests with task_always_eager = True for synchronous execution.

- Coverage expectations
  - Aim for >= 80% coverage. Prioritize:
    - JobDatabase methods: schema init, add_job (dedup), filters, bulk operations
    - EnhancedJobScraper helpers: _extract_salary, _extract_experience, _extract_experience_years, _extract_keywords_from_description, _calculate_relevance_score, dedup logic
    - SmartEmailer: build_smart_html_email on various inputs; create_excel_report with mocked filesystem
    - Flask routes: authentication flow, dashboard filters, status updates, profile CRUD, background task initiation

- Unit vs Integration
  - Unit: string parsing, relevance math, Jinja filters, SQL param construction (no DB calls)
  - Integration: DB read/write with a temporary DB; Celery tasks with eager mode
  - Functional: Flask test client for full route behavior (auth, redirects, flashes, templates rendered)

- Example commands
  - pytest -q
  - pytest -k "unit and not slow"
  - pytest tests/functional -q

## 4. Code Style
- Language & typing
  - Use Python 3 type hints consistently (parameters and returns). The project uses dataclasses and typing (List, Dict, Optional, Tuple) – keep this consistent.
  - Prefer dataclasses for simple data carriers (as with Job).

- Naming conventions
  - Modules/files: snake_case (e.g., job_database.py if splitting).
  - Variables/functions: snake_case.
  - Classes: PascalCase (Job, JobDatabase, EnhancedJobScraper, SmartEmailer).
  - Constants: UPPER_SNAKE_CASE (e.g., SCOPES, ADMIN_ALERT_EMAIL, DRIVER_PATHS).

- Documentation & comments
  - Add docstrings to public functions/classes and non-trivial private helpers.
  - Document edge-cases and external behavior (rate limits, CAPTCHA risks, timezone assumptions).

- Error handling & logging
  - Always log exceptions with context; prefer logger over print.
  - User-facing feedback via Flask flash messages must be generic; sensitive details should only be logged.
  - Wrap network and file I/O in try/except with actionable logs.

- Database access (SQLite)
  - Always use parameterized queries (already followed).
  - Use context managers for connections/cursors where practical.
  - For schema changes, follow existing pattern: PRAGMA table_info + ALTER TABLE to add new columns idempotently.

- Configuration & secrets
  - Read all secrets/URLs from environment variables. Current keys:
    - SECRET_KEY
    - broker_url / CELERY_BROKER_URL (Redis)
    - result_backend / CELERY_RESULT_BACKEND (Redis)
    - ADMIN_ALERT_EMAIL
  - Do not commit credentials.json or token.pickle – provision them securely in deployment.

- Concurrency & async
  - Use Celery (workers + beat) for long-running tasks (scraping, emailing).
  - gevent.monkey.patch_all(ssl=False) is applied globally; be cautious when adding code that depends on unpatched stdlib behavior (e.g., certain subprocess flows). Avoid mixing heavy gevent usage with Selenium.
  - Prefer ThreadPoolExecutor (as used) or Celery subtasks for concurrent I/O; keep sleeps/rate-limiting explicit.

- HTML templates & Jinja2
  - Escape user-provided content by default; use filters sparingly.
  - Keep inline scripts minimal and feature-gated; avoid leaking sensitive data to the client.

## 5. Common Patterns
- Data model
  - Job dataclass used to carry scraped job attributes and computed fields (min/max experience, extracted tools/skills, relevance_score). Use Job.to_dict for report/serialization.

- Deduplication
  - Jobs are deduplicated by md5(title+company+location). Keep this consistent when adding sources; consider normalizing whitespace/case.

- Relevance scoring
  - Combined heuristic using search term matches (title/description), extracted skills/tools/soft-skills, experience fit, location/job_type, and recency multipliers. If updating scoring, maintain determinism and keep default multipliers sane; clamp any user multipliers to reasonable ranges (as implemented).

- Scraping
  - requests + BeautifulSoup with randomized User-Agent and polite sleeps. Selenium (Edge) available for dynamic content but not required by all sources.
  - Be defensive: check for CAPTCHAs/login walls, fallback parsers (lxml -> html.parser), and flexible selectors.
  - Paginate modestly to reduce throttling and infrastructure load.

- Emailing & reports
  - Gmail API OAuth; token refresh using google.auth.transport.requests.Request.
  - Excel report created via pandas/openpyxl with enhanced formatting and clickable links.

- UI & workflow
  - Dashboard: filtering, sorting (whitelisted columns), pagination, CRUD for profiles, bulk delete, status updates, modal details, and copy to clipboard.

## 6. Do's and Don'ts
- Do
  - Use Celery workers for scraping and email sending; keep Flask request handlers fast.
  - Validate and sanitize all external inputs (search terms, locations, URLs).
  - Use environment variables for secrets and infra URLs; provide safe defaults for local.
  - Add new DB columns via idempotent migrations (PRAGMA + ALTER TABLE) to avoid crashes on existing installs.
  - Write unit tests for parsing and scoring helpers before changing heuristics.
  - Rate-limit scrapers and randomize User-Agent strings; anticipate anti-bot measures.
  - Log actionable context (user_id, source, term, page) for scraping/DB operations.
  - When adding a new source, implement a method def scrape_<source>_jobs(self, term: str) -> List[Job] and register in scrape_all_sources.

- Don't
  - Don’t perform scraping or large DB operations inside Flask routes synchronously.
  - Don’t build SQL strings via concatenation; always use parameterized queries.
  - Don’t leak stack traces or sensitive details via flash messages.
  - Don’t commit credentials.json, token.pickle, jobs.db, or other secrets/artifacts.
  - Don’t assume WebDriver binaries exist at hardcoded paths in all envs; prefer WebDriver Manager or env-configured paths.
  - Don’t rely on gevent monkey patching for behavior that needs precise subprocess/thread semantics (e.g., Selenium) without testing.

## 7. Tools & Dependencies
- Core libraries
  - Flask, Flask-Login – web app and user sessions
  - Celery – task queue for scraping and scheduling; Redis broker/backend
  - requests, beautifulsoup4, lxml – HTTP & HTML parsing
  - selenium – browser automation for dynamic pages (optional per source)
  - pandas, openpyxl – Excel report generation
  - google-api-python-client, google-auth, google-auth-oauthlib – Gmail API integration
  - gevent – monkey patching (used globally in app.py)
  - schedule – simple scheduling used in contexts; Celery Beat is authoritative in production
  - sqlite3 – built-in DB for persistence

- Setup instructions (local)
  1) Python environment
     - python -m venv .venv
     - .venv\Scripts\activate (Windows) or source .venv/bin/activate (Unix)
     - pip install -r requirements.txt
  2) Infrastructure
     - Install and run Redis (broker/backend) locally, or set environment variables to a managed Redis.
     - Set env vars (examples):
       - SECRET_KEY=change-me
       - broker_url=redis://localhost:6379/0
       - result_backend=redis://localhost:6379/0
       - ADMIN_ALERT_EMAIL=you@example.com
  3) Google API
     - Place credentials.json from Google Cloud Console (OAuth Client) in project root.
     - First run will create token.pickle after consent flow.
  4) Running processes
     - Web app: python app.py
     - Celery worker: celery -A app.celery worker --loglevel=info
     - Celery beat: celery -A app.celery beat --loglevel=info
     - Procfile (for foreman/honcho/Heroku-like):
       - web: python app.py
       - worker: celery -A app.celery worker --loglevel=info
       - beat: celery -A app.celery beat --loglevel=info
  5) Selenium drivers
     - Prefer webdriver-manager for portability in tests.
     - If using manual drivers, update DRIVER_PATHS in app.py and ensure browser binaries are present.

## 8. Other Notes
- For LLM-generated changes
  - Keep responsibilities scoped:
    - DB logic in JobDatabase; no raw SQL in routes/scrapers/emails.
    - Scraping in EnhancedJobScraper; enrich and return Job objects only.
    - Email composition in SmartEmailer; keep pure-HTML builder side-effect free.
  - Add new DB fields by following the existing migration guard pattern (PRAGMA table_info + ALTER TABLE inside init_db).
  - When adding sources, favor requests/BS4 and resilient selectors; wrap network calls and respect rate-limits.
  - Maintain the scoring pipeline contract: Job -> compute relevance -> filter threshold -> sort -> dedup.

- Edge cases & constraints
  - LinkedIn can present login walls/CAPTCHAs; fail fast and continue with other sources.
  - Gmail tokens may expire or be revoked; handle refresh exceptions gracefully and alert via logs.
  - Timezone: Celery is configured to UTC. If user-facing schedules are needed, add timezone-aware conversions.
  - Very long descriptions: UI uses a clean_desc filter; keep email/report truncation in Job.to_dict consistent.
  - Sorting safety: only allow whitelisted columns in ORDER BY (already enforced).

2. Deeper AI & Intelligence Features
Let's lean into the "AI" part of the "AI Job Agent" name.

AI Cover Letter Generation: You currently have a cover letter template. We could create a feature that uses an AI model to generate a unique, tailored cover letter for a specific job by analyzing the job description and using the details from your profile.
Resume-to-Job Matching: Instead of just scoring based on keywords, you could upload your resume, have the system parse it, and then score new jobs based on how well they align with your actual experience and skills listed in the resume.
Interview Prep Assistant: For any job you move to the "Interview" status, we could add a button that uses AI to generate a list of potential interview questions (behavioral and technical) based on the job description.
3. Enhanced Workflow & Automation
We can make the connection between finding and applying even smoother.

Track "Assisted Apply" Status: Right now, when you click "Assisted Apply," the task runs in the background. We could add UI feedback to track its status, similar to how the scraping task is tracked, so you know when the browser is about to open.

Calendar Integration: For jobs in the "Interview" stage, add an "Add to Calendar" button that creates a Google Calendar event for the interview, pre-filling the company name and job title.