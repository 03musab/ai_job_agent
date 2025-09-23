# 🤖 AI JobSnap

AI JobSnap is a powerful, Flask-based web application designed to automate and streamline your job search. It aggregates job listings from multiple sources, scores them for relevance, and provides a comprehensive dashboard to manage your applications from discovery to offer.


## ✨ Features

-   **Multi-Source Job Scraping:** Aggregates job listings from popular platforms like **LinkedIn** and **Internshala**.
-   **User Authentication:** Secure registration and login for a personalized experience.
-   **Saved Search Profiles:** Create and save multiple search profiles (keywords, location, experience) to run complex searches with a single click.
-   **Background Processing:** Leverages **Celery** and **Redis** for non-blocking, scheduled job scraping, ensuring the UI remains fast and responsive.
-   **AI-Powered Relevance Scoring:** Intelligently scores jobs based on a configurable heuristic (keywords in title/description, skills, experience match) to surface the most relevant opportunities.
-   **Job Management Dashboard:** A central hub to view, filter, sort, and manage all found jobs. Update application status (`New`, `Applied`, `Interview`, `Rejected`, `Offered`) and add personal notes.
-   **Automated Email Reports:** Receive daily or scheduled email summaries of new jobs, with an optional, beautifully formatted **Excel report** attachment via the **Gmail API**.
-   **Assisted Application Filling:** (Experimental) Launches a browser and helps pre-fill application forms on common Applicant Tracking Systems (ATS) to speed up the application process.
-   **Resume-Aware Intelligence:** Upload your resume to enable smarter job-to-resume matching and provide data for the application filler.

## 🛠️ Tech Stack

-   **Backend:** Python, Flask, Celery
-   **Frontend:** HTML, CSS, JavaScript, Bootstrap 5
-   **Database:** SQLite
-   **Task Queue:** Redis (as Celery broker and result backend)
-   **Web Scraping:** `requests`, `BeautifulSoup4`, `selenium`
-   **Email & Reporting:** Google API Client (Gmail), `pandas`, `openpyxl`
-   **Authentication:** Flask-Login
-   **Concurrency:** `gevent`

## 📂 Project Structure

```
.
├── app.py                  # Main Flask app, Celery config, data models, services, routes
├── templates/              # Jinja2 HTML templates
│   ├── base.html
│   ├── dashboard.html
│   ├── login.html
│   └── ...
├── requirements.txt        # Python dependencies
├── Procfile                # Process definitions for deployment (e.g., Heroku)
├── jobs.db                 # SQLite database file (created at runtime)
├── credentials.json        # Google API credentials (required for email)
├── token.pickle            # Google API token (created at runtime)
├── BEST_PRACTICES.md       # In-depth developer documentation
└── README.md               # This file
```

## 🚀 Getting Started

Follow these instructions to get the project up and running on your local machine.

### 1. Prerequisites

-   Python 3.8+
-   Redis (Install and run it locally or use a cloud instance)
-   A modern web browser (like Microsoft Edge) and its corresponding WebDriver.

### 2. Clone the Repository

```bash
git clone https://github.com/your-username/ai-job-agent.git
cd ai-job-agent
```

### 3. Set up Python Environment

```bash
# Create a virtual environment
python -m venv .venv

# Activate it
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root and add the following variables.

```env
# Flask secret key for session management
SECRET_KEY=a-very-secret-key-change-me

# Redis connection URLs for Celery
broker_url=redis://localhost:6379/0
result_backend=redis://localhost:6379/0

# Email address for critical system alerts
ADMIN_ALERT_EMAIL=your-email@example.com

# (Optional) Explicit path to your Selenium Edge WebDriver
# Download from: https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/
EDGE_DRIVER_PATH="C:\WebDrivers\msedgedriver.exe"
```

### 5. Set up Google API for Emailing

1.  Go to the Google Cloud Console.
2.  Create a new project.
3.  Enable the **Gmail API**.
4.  Create an **OAuth 2.0 Client ID** for a **Desktop app**.
5.  Download the credentials JSON file and save it as `credentials.json` in the project root.

The first time you run a feature that sends an email, a browser window will open asking you to authorize the application. After you grant permission, a `token.pickle` file will be created to store your credentials for future runs.

## ▶️ Running the Application

You need to run three separate processes in three different terminals.

### Terminal 1: Start the Flask Web Server

```bash
python app.py
```

The web application will be available at `http://127.0.0.1:5000`.

### Terminal 2: Start the Celery Worker

This process executes the background tasks like scraping and emailing.

```bash
celery -A app.celery worker --loglevel=info
```

### Terminal 3: Start the Celery Beat Scheduler

This process triggers the scheduled tasks (e.g., daily job hunts).

```bash
celery -A app.celery beat --loglevel=info
```

## 💡 Usage

1.  **Register & Login:** Open `http://127.0.0.1:5000` and create an account.
2.  **Update Your Profile:** Go to the "Profile" page and fill in your details, including your name, contact info, and resume. This data is used by the "Assisted Apply" feature.
3.  **Create a Search Profile:** On the dashboard, define a search profile with job keywords (e.g., "Python Developer, Data Engineer"), location, and experience level.
4.  **Run a Search:** Click the "Run" button on a saved profile to start a background job hunt. A progress bar will show the status.
5.  **Manage Jobs:** New jobs will appear on your dashboard. You can sort, filter, and update their status (e.g., change from `New` to `Applied`).
6.  **Configure Email Reports:** In the "Email Settings" section, add your email address and choose your preferences to receive automated reports.

## 🧪 Testing

The project uses `pytest` for testing. To run the test suite:

```bash
pytest
```

For more details on the test strategy, see BEST_PRACTICES.md.

## 🔧 Future Scope 

1.	AI-tailored cover letters + one-click variants — generate multiple personalized cover letters per job (use an LLM + prompt templates).
2.	Resume optimizer with score and fixes — show which keywords/phrases to add to match a job (use embeddings + token-level highlights).
3.	Semantic job matching / embeddings search — rank jobs by semantic similarity to resume/profile (use sentence-transformers).
4.	Auto-tailor resume (selective edit) — produce a short tailored resume PDF for each job (diff + PDF generator).
5.	Smart apply automation with human-in-the-loop — prepare filled form + highlighted fields for quick final review (no CAPTCHA bypass).
6.	Interview prep pack per job — auto-generate key questions, company talk-track and 30–60–90 plan (LLM + company scraping).
7.	Slack/Telegram/WhatsApp push alerts + deep links — immediate notifications with Apply button (webhooks / bot).
8.	Calendar + apply scheduler — schedule applications and reminders; auto-book mock-interviews (ICS + Google Calendar API).
9.	Company enrichment & salary intel — attach Glassdoor/Levels.fyi/similar public stats to job cards (scrape/third party API).
10.	Feedback-driven scoring loop — use user likes/dislikes to retrain ranking weights (store feedback, update multipliers).
11.	Browser-profile sync & safe session sharing — export/import user-data-dir snippets securely (encrypted blobs).
12.	Privacy & secrets vault — encrypt stored credentials and OAuth tokens (use Fernet or OS keyring).
13.	Interactive visual dashboard — heatmaps, source breakdown, skill clouds, timeline (D3/Plotly).
14.	Browser extension + quick-save — clip jobs from any site into the app with one click (Chrome/Edge extension).
15.	Multi-tenant rate-limited scrapers with proxy rotation — scale scraping without getting blocked (proxies + backoff, per-user quotas).

## 🤝 Contributing

Contributions are welcome! Please read BEST_PRACTICES.md for coding standards, architectural patterns, and guidelines before submitting a pull request.

## 📄 License

This project is licensed under the MIT License. See the `LICENSE` file for details.