# 🤖 JobSnap — AI Job Agent & Career Automation Platform

**JobSnap** is an end-to-end AI-powered job search, career intelligence, and candidate outreach platform built on Flask, Celery, and Tailwind CSS. It aggregates live job postings across top platforms, analyzes resume compatibility using AI scoring, auto-generates personalized learning roadmaps, assists ATS form-filling, and streamlines candidate/recruiter outreach.

---

## ✨ Key Features

- **Multi-Source Job Aggregator**: Scrapes and indexes live listings from **LinkedIn**, **Internshala**, **Naukri**, and direct career portals in the background.
- **AI Resume Match & Compatibility Scoring**: Analyzes uploaded resumes against job requirements to calculate compatibility percentages, skill matches, and missing qualifications.
- **Career Roadmaps & Skill Gap Analysis**: Dynamically identifies missing skills for target roles and builds actionable learning pathways with curated courses and resources.
- **Assisted 1-Click Form Filling**: Browser-driven assistant helps pre-fill repetitive candidate data across major Applicant Tracking Systems (ATS).
- **Recruiter & Outreach Command Center**:
  - Dedicated Recruiter Dashboard to review inbound applicants, candidate tiers, and pipeline velocity.
  - Automated outreach engine (`outreach_scraper.py`) for prospect sourcing and personalized candidate communication.
- **Waitlist & VIP Access Dispatcher (`send_launch_emails.py`)**:
  - Deliverability-optimized email dispatch system powered by the **Gmail API** with zero-link primary-inbox strategies.
  - Supports dry-run previews, test sending, single/multiple name and email filtering, and full batch broadcasts.
- **Google Calendar & Automated Alerts**:
  - Direct synchronization of application deadlines, interviews, and follow-ups to Google Calendar.
  - Daily email summaries with attached, styled Excel reports (`openpyxl`, `pandas`).
- **Modern Responsive Dashboard**:
  - Re-engineered with modern **Tailwind CSS**, interactive **Chart.js** application funnels, real-time market quotes, and status boards (`New`, `Applied`, `Interview`, `Rejected`, `Offered`).

---

## 🛠️ Tech Stack

| Layer | Technologies |
|---|---|
| **Backend** | Python 3.10+, Flask, Flask-Login, Celery, SQLite (local), PostgreSQL (Render), SQLAlchemy, `gevent` |
| **Frontend** | Tailwind CSS, Bootstrap 5, Jinja2, Chart.js, HTML5 / Vanilla JS |
| **Task Queue & Caching** | Redis (Celery broker & result backend) |
| **Scraping & Automation** | Selenium WebDriver (Edge / Chrome), `BeautifulSoup4`, `requests` |
| **Cloud & APIs** | Google API Client (Gmail & Google Calendar v3), Cloudflare Tunnels |
| **Data & Reports** | `pandas`, `openpyxl`, `PyPDF2` / `pdfminer` (Resume parsing) |
| **DevOps & Process** | Honcho, Procfile, npm / Node.js (Tailwind CLI) |

---

## 📂 Project Structure

```
ai_job_agent/
├── app.py                      # Core Flask app, database models, routes & Celery tasks
├── auth_middleware.py          # Session and authentication guards
├── resume_service.py           # Resume extraction, parsing, and skill evaluation
├── skill_gap_service.py        # Gap analysis comparing candidate vs role requirements
├── roadmap_service.py          # Dynamic learning roadmap generator
├── learning_models.py          # Career progression and skill models
├── role_skill_map.json         # Taxonomy of industry roles and required skills
├── outreach_scraper.py         # Recruiter and candidate outreach scraper
├── send_launch_emails.py       # VIP early-access & launch email broadcast dispatcher
├── jobsnap_waitlist_contacts.csv # Waitlist contacts database
├── credentials.json            # Google OAuth 2.0 client credentials (Gmail/Calendar)
├── token.pickle                # Auto-refreshing OAuth access & refresh tokens
├── start_tunnel.bat            # One-click Cloudflare tunnel runner
├── Procfile                    # Multi-process definition (web, worker, beat)
├── requirements.txt            # Python dependencies
├── package.json                # Tailwind CSS build scripts & frontend tooling
├── tailwind.config.js          # Tailwind styling configuration
├── static/                     # Compiled CSS, images, and frontend scripts
└── templates/                  # Jinja2 templates (dashboard, learning_path, recruiter, etc.)
```

---

## 🚀 Getting Started

### 1. Prerequisites

- **Python 3.10+**
- **Node.js 18+** (for compiling Tailwind CSS)
- **Redis Server** (running locally or via Docker / cloud)
- **Microsoft Edge or Google Chrome** with the matching WebDriver installed

### 2. Installation

```bash
# Clone the repository
git clone https://github.com/your-username/ai_job_agent.git
cd ai_job_agent

# Create and activate virtual environment
python -m venv .venv

# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Install Node dependencies (for Tailwind)
npm install
```

### 3. Environment Configuration

Create a `.env` file in the root directory:

```env
SECRET_KEY=your-super-secret-session-key
broker_url=redis://localhost:6379/0
result_backend=redis://localhost:6379/0
ADMIN_ALERT_EMAIL=admin@example.com

# Optional: Path to custom WebDriver executable
EDGE_DRIVER_PATH="C:\WebDrivers\msedgedriver.exe"
```

### Render PostgreSQL and Pro invitations

The Render blueprint provisions a managed PostgreSQL database and connects it to the web service through `DATABASE_URL`. Login, signup, application records, outreach data, and learning-path data use that same hosted database in production; local development and tests can continue to use SQLite.

The current SQLite database files are not included in deployments. Before switching an existing live installation, make a backup of its `jobs.db`, `outreach.db`, and `instance/learning_paths.db` files while they are still accessible. The app does not automatically migrate them at startup. The Render blueprint links the internal database URL automatically, but the web process stays blocked until migration is verified. After the Render database is available, set `DATABASE_URL` locally to its external connection URL and run:

```powershell
python scripts\migrate_sqlite_to_postgres.py --confirm
```

The migration command creates SQLite backups, requires an empty PostgreSQL target, copies the records, and verifies row counts. After it succeeds, set `DATABASE_MIGRATION_COMPLETE=true` in Render to let the service start against the already-linked internal URL. Do not commit either connection URL. Render's managed PostgreSQL is a separate paid resource; check the current Render dashboard for available plans and pricing. If you cannot back up the existing SQLite files, do not enable the migration flag or cut over.

To enable the Pro invite page, set `ADMIN_USERNAMES` in Render to the username of an existing trusted account. Configure `PUBLIC_APP_URL`, `MAIL_SERVER`, `MAIL_PORT`, `MAIL_USERNAME`, `MAIL_PASSWORD`, and optionally `MAIL_FROM` in Render's environment settings. The page is inaccessible to other logged-in accounts. Admin confirmation sends a one-time password setup email; tests mock mail delivery and never send real email.

### 4. Google API Setup (Gmail & Calendar)

1. Navigate to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project and enable the **Gmail API** and **Google Calendar API**.
3. Create an **OAuth 2.0 Client ID** (Application type: *Desktop App*).
4. Download the JSON credential file and save it as `credentials.json` in the project root.
5. On the first email or calendar action, a browser consent screen will open. Upon authorization, `token.pickle` is automatically generated and kept fresh.

---

## ▶️ Running the Application

### Option A: All-in-One Runner (Honcho)
If you have `honcho` installed, launch all services (Web Server, Celery Worker, Celery Beat) with a single command:

```bash
honcho start
```

### Option B: Separate Terminals

#### Terminal 1 — Compile Tailwind CSS
```bash
npm run watch:css
```

#### Terminal 2 — Flask Web Server
```bash
python app.py
```
*Access the web UI at `http://127.0.0.1:5000`*

#### Terminal 3 — Celery Task Worker
```bash
celery -A app.celery worker --loglevel=info -P gevent
```

#### Terminal 4 — Celery Beat Scheduler
```bash
celery -A app.celery beat --loglevel=info
```

### Option C: Public Tunneling
To securely expose your local instance to the web for mobile testing or demos:
```bash
start_tunnel.bat
```

---

## 📧 Launch & Waitlist Email Dispatcher

JobSnap includes a command-line email dispatcher (`send_launch_emails.py`) with support for targeted previews, dry runs, and batch sending:

```bash
# 1. Dry run preview (Shows recipient list and parsed template without sending)
python send_launch_emails.py --type 2

# 2. Send a test email to your own address
python send_launch_emails.py --type 2 --test-to founder@example.com

# 3. Send VIP Access to specific contacts by name or email
python send_launch_emails.py --type 2 --filter-names zoya nabiha yusuf --send-all --yes

# 4. Broadcast to the entire waitlist
python send_launch_emails.py --type 2 --send-all
```

**Template Types:**
- `--type 1`: High-engagement Early Access Teaser ("The job market is not for beginners 💀")
- `--type 2`: VIP Founding Member Pass (`FOUNDER-VIP` invite code and onboarding steps)

---

## 🧪 Testing

Execute the test suite using `pytest`:

```bash
pytest
```

---

## 📄 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
