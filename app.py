# --- Standard Library Imports ---
import base64
import concurrent.futures
import datetime
import hashlib
import json
import logging
import os
import pickle
import random
import re
import signal
import sqlite3
import sys
import threading
import time
import traceback
from collections import Counter
from dataclasses import dataclass, field
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Dict, List, Optional, Tuple
from urllib.parse import quote_plus, urljoin

# --- Third-Party Imports ---
import docx
import fitz  # PyMuPDF
import gevent.monkey
import pandas as pd
import requests
import schedule
from bs4 import BeautifulSoup
from celery import Celery
from celery.schedules import crontab
from flask import Flask, flash, jsonify, redirect, render_template, request, url_for
from flask_login import (LoginManager, UserMixin, current_user, login_required,
                         login_user, logout_user)
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from selenium import webdriver
from selenium.common.exceptions import (NoSuchElementException, TimeoutException,
                                        WebDriverException as SeleniumWebDriverException)
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait
# Selenium WebDriver-specific imports
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename


import threading
import traceback

if os.environ.get('ENABLE_GEVENT_PATCH', '0') == '1':
    gevent.monkey.patch_all(ssl=False)

# --- Logging Configuration ---
if not logging.getLogger().handlers:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Configurable scoring and scraping constants ---
RELEVANCE_WEIGHTS = {
    'term_in_title': 30,
    'term_in_desc': 10,
    'skill': 5,
    'tool': 4,
    'soft_skill': 3,
    'title_word': 2,
    'exp_match': 20,
    'exp_partial': 10,
    'location': 15,
    'job_type': 10,
}
RECENCY_MULTIPLIERS = {'week': 1.2, 'month': 1.05}
RELEVANCE_MIN_THRESHOLD = float(os.environ.get('RELEVANCE_MIN_THRESHOLD', '10'))
SCRAPE_MAX_WORKERS = int(os.environ.get('SCRAPE_MAX_WORKERS', '5'))
LINKEDIN_DETAIL_MAX_WORKERS = int(os.environ.get('LINKEDIN_DETAIL_MAX_WORKERS', '2'))

# --- Helpers ---

def normalize_for_hash(text: str) -> str:
    """Normalize text for consistent hashing (trim, lowercase, collapse whitespace)."""
    if text is None:
        return ''
    return re.sub(r'\s+', ' ', text.strip().lower())

# --- Celery Configuration ---
def make_celery(app):
    """Create and configure Celery instance."""
    celery = Celery(app.import_name)
    celery.conf.update(app.config)

    # Configure periodic tasks directly within Celery's configuration
    # The beat_schedule below automatically triggers scraping twice a day.
    # Comment it out to prevent automatic scraping on startup.
    # celery.conf.beat_schedule = {
    #     'run-job-hunt-daily-morning': {
    #         'task': 'app.scheduled_job_hunt_for_all_users', # Reference the task by its full path
    #         'schedule': crontab(hour=9, minute=0), # 9:00 AM daily
    #         'args': (), # No arguments for this task
    #         'options': {'queue': 'celery'} # Ensure it uses the default queue
    #     },
    #     'run-job-hunt-daily-evening': {
    #         'task': 'app.scheduled_job_hunt_for_all_users', # Reference the task by its full path
    #         'schedule': crontab(hour=18, minute=0), # 6:00 PM daily
    #         'args': (),
    #         'options': {'queue': 'celery'}
    #     },
    # }
    celery.conf.timezone = 'UTC' # Or your desired timezone, e.g., 'Asia/Kolkata'

    return celery

# Initialize Flask app (top-level, so it's imported by all processes)
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True) # Ensure the upload folder exists

# Use new style Celery config keys (lowercase without CELERY_ prefix), with fallback to old env vars
broker_url = os.environ.get('broker_url') or os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
result_backend = os.environ.get('result_backend') or os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
app.config['broker_url'] = broker_url
app.config['result_backend'] = result_backend
# Enforce secure SECRET_KEY usage
if os.environ.get('FLASK_ENV') == 'production' and app.config['SECRET_KEY'] == 'dev-secret-key-change-in-production':
    logger.critical("SECRET_KEY is using an insecure default in production. Set SECRET_KEY env.")
    raise RuntimeError("Insecure SECRET_KEY in production")
elif app.config['SECRET_KEY'] == 'dev-secret-key-change-in-production':
    logger.warning("Using default SECRET_KEY; do not use in production.")

# Initialize Celery (top-level, so it's imported by all processes)
celery = make_celery(app)

# --- Health Check Endpoint for Scraping Readiness ---
@app.route('/health')
def health():
    try:
        # Increase timeout and add a single retry to avoid false negatives under load
        res = celery.control.ping(timeout=5.0)
        if not res:
            time.sleep(0.5)
            res = celery.control.ping(timeout=5.0)
        if res:
            return jsonify({'status': 'ok', 'message': 'System ready. You can now click Apply to start scraping.'})
        else:
            return jsonify({'status': 'error', 'message': 'Celery worker not responding.'}), 503
    except Exception as e:
        logger.exception("Health check failed")
        return jsonify({'status': 'error', 'message': 'Service unavailable'}), 503

@app.route('/task_status/<task_id>')
@login_required
def task_status(task_id):
    """Endpoint to check the status of a Celery task."""
    task = run_job_hunt_task.AsyncResult(task_id)
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'progress': 0,
            'status': 'Pending...'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'progress': task.info.get('progress', 0),
            'status': task.info.get('status', '')
        }
    else: # Something went wrong in the background
        response = {
            'state': task.state,
            'progress': 100,
            'status': f"Task failed: {str(task.info)}"
        }
    return jsonify(response)

# --- Flask-Login Configuration ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' # Redirect to login page if not authenticated

# --- Driver Paths Configuration ---
DRIVER_PATHS = {
    'edge': r"C:\WebDrivers\msedgedriver.exe",
    'chrome': r"C:\WebDrivers\chromedriver.exe",
    'firefox': r"C:\WebDrivers\geckodriver.exe",
    'chrome_pa': None, # Placeholder for headless Linux environments
    'firefox_pa': None # Placeholder for headless Linux environments
}

# --- Browser Binary Paths (for Windows, specify exact locations if not default) ---
# IMPORTANT: DOUBLE-CHECK THESE PATHS ON YOUR SYSTEM.
CHROME_BINARY_PATH_WINDOWS = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
EDGE_BINARY_PATH_WINDOWS = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
CHROME_BINARY_PATH_PA = '/usr/bin/google-chrome'


# --- Google API Scopes for Gmail and Calendar ---
SCOPES = [
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/calendar'
]

# --- Admin Email for Critical Alerts ---
ADMIN_ALERT_EMAIL = os.environ.get('ADMIN_ALERT_EMAIL', '')


# --- Add a list of common User-Agent strings to mimic different browsers ---
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
]

# --- Description sanitizer and Jinja filter ---

def clean_description(text: str, title: str = None, company: str = None) -> str:
    if not text:
        return ''
    try:
        # Split into lines to allow targeted filtering
        lines = re.split(r'[\r\n]+', text)
        cleaned = []
        patterns = [
            re.compile(r'(₹|rs\.?|lpa|ctc|per\s*annum|/year|/month|stipend)', re.IGNORECASE),
            re.compile(r'\b(actively\s*hiring)\b', re.IGNORECASE),
            re.compile(r'\b(work\s*from\s*home|remote)\b', re.IGNORECASE),
            re.compile(r'\b\d+\s*(?:year|week|day|month)s?\s*ago\b', re.IGNORECASE),
            re.compile(r'\b\d+\s*year\(s\)\b', re.IGNORECASE),
            re.compile(r'\bfresher\b', re.IGNORECASE),
        ]
        t_low = (title or '').strip().lower()
        c_low = (company or '').strip().lower()
        for line in lines:
            l = line.strip()
            if not l:
                continue
            # Skip lines that are exactly the title or company
            if t_low and l.lower() == t_low:
                continue
            if c_low and l.lower() == c_low:
                continue
            # Skip noisy lines
            if any(p.search(l) for p in patterns):
                continue
            cleaned.append(l)
        # Collapse multiple spaces and join back with newlines
        result = '\n'.join(re.sub(r'\s+', ' ', c) for c in cleaned)
        return result.strip()
    except Exception:
        # Fallback: basic whitespace normalization
        return re.sub(r'\s+', ' ', text).strip()

# Register as Jinja filter
@app.template_filter('clean_desc')
def jinja_clean_desc_filter(text: str) -> str:
    return clean_description(text)

@app.context_processor
def inject_now():
    return {'now': datetime.datetime.utcnow()}


@dataclass
class Job:
    """Enhanced Job data structure to store scraped job details."""
    title: str
    company: str
    location: str
    salary: str
    link: str
    description: str
    keywords: List[str]
    skills: List[str]
    experience: str
    job_type: str
    posted_date: str
    source: str
    deadline: str
    relevance_score: float = 0.0

    min_experience_years: Optional[int] = None
    max_experience_years: Optional[int] = None
    extracted_tools: List[str] = field(default_factory=list)
    extracted_soft_skills: List[str] = field(default_factory=list)

    user_feedback: Optional[str] = None

    def to_dict(self):
        """Converts the Job object to a dictionary for easier storage/reporting."""
        return {
            'id': getattr(self, 'id', None),
            'title': self.title,
            'company': self.company,
            'location': self.location,
            'salary': self.salary,
            'link': self.link,
            'description': self.description[:500] + '...' if len(self.description) > 500 else self.description,
            'keywords': ', '.join(self.keywords),
            'skills': ', '.join(self.skills),
            'experience': self.experience,
            'job_type': self.job_type,
            'posted_date': self.posted_date,
            'source': self.source,
            'deadline': self.deadline,
            'relevance_score': self.relevance_score,
            'min_experience_years': self.min_experience_years,
            'max_experience_years': self.max_experience_years,
            'extracted_tools': ', '.join(self.extracted_tools),
            'extracted_soft_skills': ', '.join(self.extracted_soft_skills),
            'user_feedback': self.user_feedback
        }

class User(UserMixin):
    def __init__(self, id, username, password_hash, email_recipients='', email_frequency='daily', send_excel_attachment=True):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.email_recipients = email_recipients
        self.email_frequency = email_frequency
        self.send_excel_attachment = send_excel_attachment

    @staticmethod
    def get(user_id):
        db = JobDatabase()
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, password_hash, email_recipients, email_frequency, send_excel_attachment FROM users WHERE id = ?", (user_id,))
        user_data = cursor.fetchone()
        conn.close()
        if user_data:
            return User(*user_data)
        return None

    @staticmethod
    def get_by_username(username):
        db = JobDatabase()
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, password_hash, email_recipients, email_frequency, send_excel_attachment FROM users WHERE username = ?", (username,))
        user_data = cursor.fetchone()
        conn.close()
        if user_data:
            return User(*user_data)
        return None

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


class JobDatabase:
    """SQLite database for job tracking and deduplication and user data."""

    def __init__(self, db_path="jobs.db"):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        """Initializes the SQLite database table(s) if they don't exist, and performs schema migrations."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # --- Users Table ---
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                email_recipients TEXT DEFAULT '',
                email_frequency TEXT DEFAULT 'daily',
                send_excel_attachment BOOLEAN DEFAULT TRUE
            )
        ''')
        # Perform ALTER TABLE for new user columns if they don't exist
        cursor.execute("PRAGMA table_info(users)")
        user_columns = [col[1] for col in cursor.fetchall()]
        if 'email_recipients' not in user_columns:
            try: cursor.execute("ALTER TABLE users ADD COLUMN email_recipients TEXT DEFAULT ''"); conn.commit(); logger.info("Added email_recipients column to users table.")
            except sqlite3.OperationalError as e: logger.warning(f"email_recipients column already exists or error altering users table: {e}")
        if 'email_frequency' not in user_columns:
            try: cursor.execute("ALTER TABLE users ADD COLUMN email_frequency TEXT DEFAULT 'daily'"); conn.commit(); logger.info("Added email_frequency column to users table.")
            except sqlite3.OperationalError as e: logger.warning(f"email_frequency column already exists or error altering users table: {e}")
        if 'send_excel_attachment' not in user_columns:
            try: cursor.execute("ALTER TABLE users ADD COLUMN send_excel_attachment BOOLEAN DEFAULT TRUE"); conn.commit(); logger.info("Added send_excel_attachment column to users table.")
            except sqlite3.OperationalError as e: logger.warning(f"send_excel_attachment column already exists or error altering users table: {e}")

        # --- Jobs Table ---
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_details (
                user_id INTEGER PRIMARY KEY,
                full_name TEXT,
                email TEXT,
                phone TEXT,
                address TEXT,
                linkedin_url TEXT,
                github_url TEXT,
                portfolio_url TEXT,
                resume_path TEXT,
                cover_letter_template TEXT,
                browser_profile_path TEXT DEFAULT '',
                resume_parsed_data TEXT,
                willing_to_relocate TEXT DEFAULT 'no',
                authorized_to_work TEXT DEFAULT 'no',
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        ''')

        # Perform ALTER TABLE for new user_details columns if they don't exist
        cursor.execute("PRAGMA table_info(user_details)")
        user_details_columns = [col[1] for col in cursor.fetchall()]
        if 'browser_profile_path' not in user_details_columns:
            try:
                cursor.execute("ALTER TABLE user_details ADD COLUMN browser_profile_path TEXT DEFAULT ''")
                conn.commit()
                logger.info("Added browser_profile_path column to user_details table.")
            except sqlite3.OperationalError as e:
                logger.warning(f"browser_profile_path column already exists or error altering user_details table: {e}")
        if 'resume_parsed_data' not in user_details_columns:
            try:
                cursor.execute("ALTER TABLE user_details ADD COLUMN resume_parsed_data TEXT")
                conn.commit()
                logger.info("Added resume_parsed_data column to user_details table.")
            except sqlite3.OperationalError as e:
                logger.warning(f"resume_parsed_data column already exists or error altering user_details table: {e}")
        if 'willing_to_relocate' not in user_details_columns:
            try:
                cursor.execute("ALTER TABLE user_details ADD COLUMN willing_to_relocate TEXT DEFAULT 'no'")
                conn.commit()
                logger.info("Added willing_to_relocate column to user_details table.")
            except sqlite3.OperationalError as e:
                logger.warning(f"willing_to_relocate column already exists or error altering user_details table: {e}")
        if 'authorized_to_work' not in user_details_columns:
            try:
                cursor.execute("ALTER TABLE user_details ADD COLUMN authorized_to_work TEXT DEFAULT 'no'")
                conn.commit()
                logger.info("Added authorized_to_work column to user_details table.")
            except sqlite3.OperationalError as e:
                logger.warning(f"authorized_to_work column already exists or error altering user_details table: {e}")

        cursor.execute("PRAGMA table_info(jobs)")
        jobs_existing_columns = [col[1] for col in cursor.fetchall()]

        # Robust check for table existence
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='jobs'")
        if cursor.fetchone() is None:
            logger.info("Jobs table does not exist, creating it with all columns.")
            cursor.execute('''
                CREATE TABLE jobs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_hash TEXT UNIQUE,
                    title TEXT,
                    company TEXT,
                    location TEXT,
                    salary TEXT,
                    link TEXT,
                    description TEXT,
                    keywords TEXT,
                    skills TEXT,
                    experience TEXT,
                    job_type TEXT,
                    posted_date TEXT,
                    source TEXT,
                    relevance_score REAL,
                    found_date TEXT,
                    applied BOOLEAN DEFAULT FALSE,
                    status TEXT DEFAULT 'new',
                    user_id INTEGER,
                    notes TEXT DEFAULT '',
                    min_experience_years INTEGER,
                    max_experience_years INTEGER,
                    extracted_tools TEXT DEFAULT '',
                    extracted_soft_skills TEXT DEFAULT '',
                    user_feedback TEXT DEFAULT '',
                    deadline TEXT,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                )
            ''')
        else: # Table exists, check for new columns and alter
            if 'notes' not in jobs_existing_columns:
                try: cursor.execute("ALTER TABLE jobs ADD COLUMN notes TEXT DEFAULT ''"); conn.commit(); logger.info("Added notes column to jobs table.")
                except sqlite3.OperationalError as e: logger.warning(f"notes column already exists or error altering jobs table: {e}")
            if 'min_experience_years' not in jobs_existing_columns:
                try: cursor.execute("ALTER TABLE jobs ADD COLUMN min_experience_years INTEGER"); conn.commit(); logger.info("Added min_experience_years column to jobs table.")
                except sqlite3.OperationalError as e: logger.warning(f"min_experience_years column already exists or error altering jobs table: {e}")
            if 'max_experience_years' not in jobs_existing_columns:
                try: cursor.execute("ALTER TABLE jobs ADD COLUMN max_experience_years INTEGER"); conn.commit(); logger.info("Added max_experience_years column to jobs table.")
                except sqlite3.OperationalError as e: logger.warning(f"max_experience_years column already exists or error altering jobs table: {e}")
            if 'extracted_tools' not in jobs_existing_columns:
                try: cursor.execute("ALTER TABLE jobs ADD COLUMN extracted_tools TEXT DEFAULT ''"); conn.commit(); logger.info("Added extracted_tools column to jobs table.")
                except sqlite3.OperationalError as e: logger.warning(f"extracted_tools column already exists or error altering jobs table: {e}")
            if 'extracted_soft_skills' not in jobs_existing_columns:
                try: cursor.execute("ALTER TABLE jobs ADD COLUMN extracted_soft_skills TEXT DEFAULT ''"); conn.commit(); logger.info("Added extracted_soft_skills column to jobs table.")
                except sqlite3.OperationalError as e: logger.warning(f"extracted_soft_skills column already exists or error altering jobs table: {e}")
            if 'user_feedback' not in jobs_existing_columns:
                try:
                    cursor.execute("ALTER TABLE jobs ADD COLUMN user_feedback TEXT DEFAULT ''")
                    conn.commit(); logger.info("Added user_feedback column to jobs table.")
                except sqlite3.OperationalError as e:
                    logger.warning(f"user_feedback column already exists or error altering jobs table: {e}")
            if 'deadline' not in jobs_existing_columns:
                try:
                    cursor.execute("ALTER TABLE jobs ADD COLUMN deadline TEXT")
                    conn.commit(); logger.info("Added deadline column to jobs table.")
                except sqlite3.OperationalError as e:
                    logger.warning(f"deadline column already exists or error altering jobs table: {e}")

        # --- Search Profiles Table ---
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS search_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                profile_name TEXT NOT NULL,
                search_terms TEXT NOT NULL,
                location TEXT,
                experience TEXT,
                job_type TEXT,
                UNIQUE(user_id, profile_name),
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        ''')

        # --- User Custom Scores Table (for AI-powered relevance) ---
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_custom_scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                keyword TEXT NOT NULL, -- The specific keyword/skill/tool (always stored lowercase)
                keyword_type TEXT NOT NULL, -- e.g., 'high_value', 'skill', 'tool', 'soft_skill'
                score_multiplier REAL DEFAULT 1.0, -- Multiplier for this keyword's default score
                UNIQUE(user_id, keyword, keyword_type), -- Ensure unique entry per user/keyword/type
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        ''')

        # --- User Job Feedback Table (for feedback history) ---
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_job_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                job_id INTEGER NOT NULL,
                feedback_type TEXT NOT NULL, -- 'like' or 'dislike'
                timestamp TEXT NOT NULL,
                UNIQUE(user_id, job_id), -- Only one feedback per job per user
                FOREIGN KEY(user_id) REFERENCES users(id),
                FOREIGN KEY(job_id) REFERENCES jobs(id)
            )
        ''')

        conn.commit()
        conn.close()
        logger.info("Database schema check/update complete.")
        if os.environ.get('RUN_JOB_HASH_MIGRATION', '0') == '1':
            logger.info("RUN_JOB_HASH_MIGRATION=1 detected; starting job_hash migration...")
            self.migrate_job_hashes_normalized()

    def add_user(self, username, password_hash):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, password_hash))
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None # Username already exists
        finally:
            conn.close()

    def add_job(self, job: Job, user_id: Optional[int] = None):
        """Adds a job to the database with deduplication and user association."""
        # The hash must be unique per user for the same job to allow multiple users to track it.
        norm = f"{normalize_for_hash(job.title)}|{normalize_for_hash(job.company)}|{normalize_for_hash(job.location)}|{user_id}"
        job_hash = hashlib.md5(norm.encode('utf-8')).hexdigest()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO jobs
                (job_hash, title, company, location, salary, link, description,
                 keywords, skills, experience, job_type, posted_date, source,
                 relevance_score, found_date, user_id, status, notes, deadline,
                 min_experience_years, max_experience_years, extracted_tools, extracted_soft_skills, user_feedback)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                job_hash,  # job_hash
                job.title,  # title
                job.company,  # company
                job.location,  # location
                job.salary,  # salary
                job.link,  # link
                job.description,  # description
                ', '.join(job.keywords),  # keywords
                ', '.join(job.skills),  # skills
                job.experience,  # experience
                job.job_type,  # job_type
                job.posted_date,  # posted_date
                job.source,  # source
                job.relevance_score,  # relevance_score
                datetime.datetime.now().isoformat(),  # found_date
                user_id,  # user_id
                'new',  # status
                '',  # notes
                job.deadline,  # deadline
                job.min_experience_years,  # min_experience_years
                job.max_experience_years,  # max_experience_years
                ', '.join(job.extracted_tools),  # extracted_tools
                ', '.join(job.extracted_soft_skills),  # extracted_soft_skills
                job.user_feedback if job.user_feedback else ''  # user_feedback
            ))
            conn.commit()
            if cursor.rowcount > 0:
                logger.debug(f"Added new job to DB: {job.title} at {job.company} for user {user_id}")
                
                # Create calendar reminder for deadline if available
                if job.deadline and job.deadline != 'N/A':
                    try:
                        calendar_manager = GoogleCalendarManager()
                        job_data = job.to_dict()
                        job_data['id'] = cursor.lastrowid
                        calendar_manager.create_deadline_reminder(job_data, job.deadline)
                        logger.info(f"Created deadline reminder for job: {job.title}")
                    except Exception as e:
                        logger.warning(f"Failed to create deadline reminder: {e}")
                
                return True
            else:
                logger.debug(f"Job already exists in DB (skipped): {job.title} at {job.company} for user {user_id}")
                return False
        except sqlite3.OperationalError as e:
            logger.error(f"SQLite Operational Error (likely schema mismatch during job insert): {e}.")
            # Log with the corrected order for accurate debugging
            correct_values = (job_hash, job.title, job.company, job.location, job.salary, job.link, job.description, ', '.join(job.keywords), ', '.join(job.skills), job.experience, job.job_type, job.posted_date, job.source, job.relevance_score, datetime.datetime.now().isoformat(), user_id, 'new', '', job.deadline, job.min_experience_years, job.max_experience_years, ', '.join(job.extracted_tools), ', '.join(job.extracted_soft_skills), job.user_feedback if job.user_feedback else '')
            logger.error("Attempting to insert values: %s", correct_values)
            return False
        except Exception as e:
            logger.error(f"Error adding job to database: {e}")
            return False
        finally:
            conn.close()

    def get_jobs_for_user(self, user_id: int, limit=100, offset=0,
                             sort_by='found_date', sort_order='DESC',
                             search_query: Optional[str] = None,
                             status_filter: Optional[str] = None,
                             location_filter: Optional[str] = None,
                             job_type_filter: Optional[str] = None) -> Tuple[List[Dict], int]:
        """Retrieves jobs for a specific user from the database, with filters and pagination."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query_columns = """
            id, job_hash, title, company, location, salary, link, description,
            keywords, skills, experience, job_type, posted_date, source,
            relevance_score, found_date, applied, status, user_id, notes, deadline,
            min_experience_years, max_experience_years, extracted_tools, extracted_soft_skills, user_feedback
        """
        query = f"SELECT {query_columns} FROM jobs WHERE user_id = ?"
        params = [user_id]

        if search_query:
            # Handle special search formats like "id:123"
            if search_query.startswith('id:'):
                job_id = search_query.split(':', 1)[1].strip()
                if job_id.isdigit():
                    query += " AND id = ?"
                    params.append(int(job_id))
                else:
                    # Invalid ID format, no results
                    query += " AND 1 = 0"
            else:
                # Regular text search
                search_pattern = f"%{search_query}%"
                query += " AND (title LIKE ? OR company LIKE ? OR description LIKE ? OR notes LIKE ? OR keywords LIKE ? OR skills LIKE ? OR extracted_tools LIKE ? OR extracted_soft_skills LIKE ?)"
                params.extend([search_pattern, search_pattern, search_pattern, search_pattern, search_pattern, search_pattern, search_pattern, search_pattern])

        if status_filter and status_filter != 'all':
            query += " AND status = ?"
            params.append(status_filter)

        if location_filter:
            location_pattern = f"%{location_filter}%"
            query += " AND location LIKE ?"
            params.append(location_pattern)

        if job_type_filter and job_type_filter != 'all':
            query += " AND job_type = ?"
            params.append(job_type_filter)

        count_query = f"SELECT COUNT(*) FROM ({query})"
        cursor.execute(count_query, params)
        total_count = cursor.fetchone()[0]

        # Safely construct ORDER BY clause
        allowed_sort_columns = ['found_date', 'title', 'company', 'location', 'relevance_score']
        if sort_by not in allowed_sort_columns:
            sort_by = 'found_date' # Default to safe column
        sort_order = 'ASC' if sort_order.upper() == 'ASC' else 'DESC' # Ensure valid order

        query += f" ORDER BY {sort_by} {sort_order} LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        cursor.execute(query, params)
        jobs_raw = cursor.fetchall()

        column_names = [description[0] for description in cursor.description]
        jobs = [dict(zip(column_names, job_tuple)) for job_tuple in jobs_raw]

        conn.close()
        logger.info(f"Retrieved {len(jobs)} jobs for user {user_id} (Total: {total_count}).")
        return jobs, total_count

    def save_search_profile(self, user_id: int, profile_name: str, search_terms: str,
                            location: str, experience: str, job_type: str) -> Optional[int]:
        """Saves a search profile for a user. Returns profile ID on success, None on failure."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO search_profiles
                (user_id, profile_name, search_terms, location, experience, job_type)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, profile_name, search_terms, location, experience, job_type))
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            logger.warning(f"Attempted to save duplicate profile name '{profile_name}' for user {user_id}.")
            return None
        except Exception as e:
            logger.error(f"Error saving search profile: {e}")
            return None
        finally:
            conn.close()

    def get_search_profiles(self, user_id: int) -> List[Dict]:
        """Retrieves all saved search profiles for a user."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, profile_name, search_terms, location, experience, job_type FROM search_profiles WHERE user_id = ?", (user_id,))
        profiles_raw = cursor.fetchall()
        column_names = [description[0] for description in cursor.description]
        conn.close()

        profiles = [dict(zip(column_names, profile_tuple)) for profile_tuple in profiles_raw]
        return profiles

    def get_search_profile_by_id(self, profile_id: int, user_id: int) -> Optional[Dict]:
        """Retrieves a single search profile by ID and user ID."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, profile_name, search_terms, location, experience, job_type FROM search_profiles WHERE id = ? AND user_id = ?", (profile_id, user_id))
        profile_data = cursor.fetchone()
        column_names = [description[0] for description in cursor.description]
        conn.close()
        if profile_data:
            return dict(zip(column_names, profile_data))
        return None

    def delete_search_profile(self, profile_id: int, user_id: int) -> bool:
        """Deletes a search profile for a user."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM search_profiles WHERE id = ? AND user_id = ?", (profile_id, user_id))
        conn.commit()
        rows_affected = cursor.rowcount
        conn.close()
        return rows_affected > 0

    def update_user_settings(self, user_id: int, email_recipients: str, email_frequency: str, send_excel_attachment: bool) -> bool:
        """Updates user's email notification settings."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('''
                UPDATE users SET
                    email_recipients = ?,
                    email_frequency = ?,
                    send_excel_attachment = ?
                WHERE id = ?
            ''', (email_recipients, email_frequency, int(bool(send_excel_attachment)), user_id))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error updating user settings for user {user_id}: {e}")
            return False
        finally:
            conn.close()

    def get_user_settings(self, user_id: int) -> Optional[Dict]:
        """Retrieves a user's email notification settings."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT email_recipients, email_frequency, send_excel_attachment FROM users WHERE id = ?", (user_id,))
        settings_data = cursor.fetchone()
        conn.close()
        if settings_data: return {'email_recipients': settings_data[0], 'email_frequency': settings_data[1], 'send_excel_attachment': bool(settings_data[2])}
        return None

    def update_job_status_and_notes(self, job_id: int, user_id: int, status: str, notes: str) -> bool:
        """Updates the application status and notes for a specific job."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('''
                UPDATE jobs SET status = ?, notes = ? WHERE id = ? AND user_id = ?
            ''', (status, notes, job_id, user_id))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error updating job status/notes for job {job_id}, user {user_id}: {e}")
            return False
        finally:
            conn.close()

    def record_job_feedback(self, user_id: int, job_id: int, feedback_type: str) -> bool:
        """Records user feedback for a job and updates the job's feedback status."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE jobs SET user_feedback = ? WHERE id = ? AND user_id = ?", (feedback_type, job_id, user_id))
            cursor.execute("INSERT OR REPLACE INTO user_job_feedback (user_id, job_id, feedback_type, timestamp) VALUES (?, ?, ?, ?)",
                           (user_id, job_id, feedback_type, datetime.datetime.now().isoformat()))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error recording job feedback for user {user_id}, job {job_id}: {e}")
            return False
        finally:
            conn.close()

    def delete_job(self, job_id: int, user_id: int) -> bool:
        """Deletes a specific job for a user."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM jobs WHERE id = ? AND user_id = ?", (job_id, user_id))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error deleting job {job_id} for user {user_id}: {e}")
            return False
        finally:
            conn.close()

    def delete_jobs(self, job_ids: List[int], user_id: int) -> int:
        """Deletes multiple jobs for a user."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            placeholders = ','.join(['?'] * len(job_ids))
            cursor.execute(f"DELETE FROM jobs WHERE id IN ({placeholders}) AND user_id = ?", (*job_ids, user_id))
            deleted_count = cursor.rowcount
            conn.commit()
            return deleted_count
        except Exception as e:
            logger.error(f"Error deleting multiple jobs for user {user_id}: {e}")
            return 0
        finally:
            conn.close()

    def delete_all_jobs(self, user_id: int) -> int:
        """Deletes all jobs for a user."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM jobs WHERE user_id = ?", (user_id,))
            deleted_count = cursor.rowcount
            conn.commit()
            return deleted_count
        except Exception as e:
            logger.error(f"Error deleting all jobs for user {user_id}: {e}")
            return 0
        finally:
            conn.close()

    def get_job_status_counts(self, user_id: int) -> Dict[str, int]:
        """Retrieves the count of jobs for each status for a specific user."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Initialize counts to ensure all statuses are present, even if they are 0.
        status_counts = {
            'new': 0,
            'applied': 0,
            'interview': 0,
            'rejected': 0,
            'offered': 0
        }

        try:
            cursor.execute("SELECT status, COUNT(*) FROM jobs WHERE user_id = ? AND status IS NOT NULL GROUP BY status", (user_id,))
            rows = cursor.fetchall()
            for status, count in rows:
                if status in status_counts:
                    status_counts[status] = count
            return status_counts
        except Exception as e:
            logger.error(f"Error getting job status counts for user {user_id}: {e}")
            return status_counts # Return default counts on error
        finally:
            conn.close()

    def update_custom_score(self, user_id: int, keyword: str, keyword_type: str, change_multiplier: float) -> None:
        """Adjusts the custom relevance score multiplier for a specific keyword for a user."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT score_multiplier FROM user_custom_scores WHERE user_id = ? AND keyword = ? AND keyword_type = ?",
                           (user_id, keyword, keyword_type))
            row = cursor.fetchone()

            if row:
                new_multiplier = row[0] * (1 + change_multiplier)
                new_multiplier = max(0.5, min(2.0, new_multiplier)) # Clamp multiplier to prevent extreme values
                cursor.execute("UPDATE user_custom_scores SET score_multiplier = ? WHERE user_id = ? AND keyword = ? AND keyword_type = ?",
                               (new_multiplier, user_id, keyword, keyword_type))
            else:
                initial_multiplier = 1.0 * (1 + change_multiplier)
                initial_multiplier = max(0.5, min(2.0, initial_multiplier))
                cursor.execute("INSERT INTO user_custom_scores (user_id, keyword, keyword_type, score_multiplier) VALUES (?, ?, ?, ?)",
                               (user_id, keyword, keyword_type, initial_multiplier))
            conn.commit()
        except Exception as e:
            logger.error(f"Error updating custom score for user {user_id}, keyword '{keyword}' type '{keyword_type}': {e}")
        finally:
            conn.close()

    def get_custom_scores(self, user_id: int) -> Dict[Tuple[str, str], float]:
        """Retrieves all custom score multipliers for a given user."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT keyword, keyword_type, score_multiplier FROM user_custom_scores WHERE user_id = ?", (user_id,))
        rows = cursor.fetchall()
        conn.close()

        custom_scores = {}
        for row in rows:
            keyword, keyword_type, multiplier = row
            custom_scores[(keyword, keyword_type)] = multiplier
        return custom_scores

    def migrate_job_hashes_normalized(self) -> None:
        """One-time migration to recompute job_hash using normalized title/company/location and user_id."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            # Fetch user_id to make the hash user-specific
            cursor.execute("SELECT id, title, company, location, job_hash, user_id FROM jobs")
            rows = cursor.fetchall()
            updated = 0
            for id_, title, company, location, old_hash, user_id in rows:
                # Recompute hash with user_id
                norm = f"{normalize_for_hash(title)}|{normalize_for_hash(company)}|{normalize_for_hash(location)}|{user_id}"
                new_hash = hashlib.md5(norm.encode('utf-8')).hexdigest()
                if new_hash != old_hash:
                    try:
                        cursor.execute("UPDATE jobs SET job_hash = ? WHERE id = ?", (new_hash, id_))
                        updated += 1
                    except sqlite3.IntegrityError:
                        logger.warning(f"Skipping job id {id_} due to hash collision during migration (likely a true duplicate for the same user).")
                        continue
            conn.commit()
            logger.info(f"Job hash migration complete. Updated {updated} rows.")
        except sqlite3.OperationalError as e:
            if "no such column: user_id" in str(e):
                logger.warning("Skipping job_hash migration: 'user_id' column not found in 'jobs' table. This is expected on very old schemas.")
            else:
                logger.error(f"Job hash migration failed with an operational error: {e}")
        except Exception as e:
            logger.error(f"Job hash migration failed: {e}")
        finally:
            conn.close()

    def get_user_details(self, user_id: int) -> Optional[Dict]:
        """Retrieves a user's application details."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row # This allows accessing columns by name
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user_details WHERE user_id = ?", (user_id,))
        details_data = cursor.fetchone()
        conn.close()
        if details_data:
            return dict(details_data)
        return None

    def save_user_details(self, user_id: int, details: Dict) -> bool:
        """Saves or updates a user's application details."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            # Using INSERT OR REPLACE (UPSERT) for simplicity
            cursor.execute('''
                INSERT OR REPLACE INTO user_details (
                    user_id, full_name, email, phone, address,
                    linkedin_url, github_url, portfolio_url,
                    resume_path, cover_letter_template, browser_profile_path,
                    resume_parsed_data, willing_to_relocate, authorized_to_work
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                details.get('full_name'), details.get('email'), details.get('phone'),
                details.get('address'), details.get('linkedin_url'), details.get('github_url'),
                details.get('portfolio_url'), details.get('resume_path'),
                details.get('cover_letter_template'), details.get('browser_profile_path'),
                details.get('resume_parsed_data'),
                details.get('willing_to_relocate'),
                details.get('authorized_to_work')
            ))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error saving user details for user {user_id}: {e}")
            return False
        finally:
            conn.close()


class ResumeParser:
    """Parses resume files to extract structured data for automated form filling."""
    def parse(self, file_path: str) -> Dict:
        """Parses a resume file (PDF, DOCX) and extracts structured data."""
        text = ""
        try:
            if file_path.lower().endswith('.pdf'):
                text = self._parse_pdf(file_path)
            elif file_path.lower().endswith('.docx'):
                text = self._parse_docx(file_path)
            else:
                logger.warning(f"Unsupported resume file format: {file_path}")
                return {}
        except Exception as e:
            logger.error(f"Failed to parse resume file {file_path}: {e}")
            return {}

        # NOTE: The following are simple heuristic-based extractions.
        # A production system would benefit from a more advanced NLP model.
        work_experience = self._extract_work_experience(text)
        skills = self._extract_skills(text)

        return {
            'raw_text': text,
            'skills': skills,
            'work_experience': work_experience,
        }

    def _parse_pdf(self, file_path: str) -> str:
        with fitz.open(file_path) as doc:
            text = "".join(page.get_text() for page in doc)
        return text

    def _parse_docx(self, file_path: str) -> str:
        doc = docx.Document(file_path)
        return "\n".join([para.text for para in doc.paragraphs])

    def _extract_skills(self, text: str) -> List[str]:
        known_skills = ['python', 'java', 'c++', 'javascript', 'react', 'angular', 'vue', 'sql', 'nosql', 'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'html', 'css', 'typescript']
        found_skills = []
        text_lower = text.lower()
        for skill in known_skills:
            if re.search(r'\b' + re.escape(skill) + r'\b', text_lower):
                found_skills.append(skill)
        return list(set(found_skills))

    def _extract_work_experience(self, text: str) -> List[Dict]:
        # This is a simplified regex for demonstration. It looks for "Title at Company (Date - Date)".
        experiences = []
        pattern = re.compile(r'([\w\s]+)\s+at\s+([\w\s]+)\s+\(([\w\s]+)\s*-\s*([\w\s]+)\)', re.IGNORECASE)
        for match in pattern.finditer(text):
            experiences.append({'title': match.group(1).strip(),'company': match.group(2).strip(),'start_date': match.group(3).strip(),'end_date': match.group(4).strip(),'description': ''})
        return experiences


class EnhancedJobScraper:
    """Advanced job scraper with multiple sources and strategies."""
    
    def __init__(self, search_terms: List[str], location: Optional[str],
                 experience: Optional[str], job_type: Optional[str], user_id: int, task=None):
        self.search_terms = search_terms
        self.location = location
        self.experience = experience
        self.job_type = job_type
        self.user_id = user_id
        self.task = task
        self.db = JobDatabase()
        self.custom_scores = self.db.get_custom_scores(self.user_id)
        self.session = None  # Avoid shared Session across threads
        
        # Placeholder for common skills/tools/soft skills (can be expanded)
        self.common_skills = ['python', 'java', 'javascript', 'react', 'angular', 'vue', 'nodejs', 'express', 'django', 'flask', 'sql', 'nosql', 'mongodb', 'postgresql', 'mysql', 'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'git', 'github', 'gitlab', 'jenkins', 'ci/cd', 'agile', 'scrum', 'rest api', 'graphql', 'html', 'css', 'redux', 'typescript', 'webpack', 'babel', 'selenium', 'jira', 'confluence', 'tableau', 'power bi', 'excel', 'gcp', 'azure', 'terraform', 'ansible', 'puppet', 'chef', 'splunk', 'elk stack', 'grafana', 'prometheus']
        self.soft_skills = ['communication', 'teamwork', 'problem-solving', 'leadership', 'adaptability', 'time management', 'critical thinking', 'creativity', 'interpersonal', 'collaboration', 'attention to detail', 'analytical']
        self.tools_platforms = ['jira', 'trello', 'asana', 'slack', 'microsoft teams', 'zoom', 'google workspace', 'salesforce', 'zendesk', 'servicenow', 'github actions', 'jenkins', 'gitlab ci']
        
        self.selenium_driver = None

    def _init_selenium_driver(self):
        """Initializes a Selenium WebDriver instance with randomized user-agent."""
        try:
            options = EdgeOptions()
            options.use_chromium = True
            options.add_argument('--headless=new')
            options.add_argument('--disable-gpu')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            random_user_agent = random.choice(USER_AGENTS)
            options.add_argument(f"user-agent={random_user_agent}")
            
            # Optional: allow disabling via env (default disabled unless explicitly enabled)
            if os.environ.get('ENABLE_SELENIUM', '0') != '1':
                logger.info("Selenium disabled. Set ENABLE_SELENIUM=1 to enable.")
                self.selenium_driver = None
                return False

            driver_path = os.environ.get('EDGE_DRIVER_PATH', DRIVER_PATHS.get('edge'))
            if not driver_path or not os.path.exists(driver_path):
                logger.error("Edge WebDriver not found. Set EDGE_DRIVER_PATH env or update DRIVER_PATHS['edge'].")
                self.selenium_driver = None
                return False

            service = EdgeService(executable_path=driver_path)
            self.selenium_driver = webdriver.Edge(service=service, options=options)
            self.selenium_driver.set_page_load_timeout(30)
            logger.info("✅ Selenium WebDriver initialized successfully.")
            return True
        except FileNotFoundError:
            logger.error(f"WebDriver executable not found for Edge. Please check DRIVER_PATHS configuration.")
            self.selenium_driver = None
            return False
        except Exception as e:
            logger.error(f"An unexpected error occurred during WebDriver initialization: {e}", exc_info=True)
            self.selenium_driver = None
            return False

    def _close_selenium_driver(self):
        """Closes the Selenium WebDriver if it's open."""
        if self.selenium_driver:
            self.selenium_driver.quit()
            self.selenium_driver = None
            logger.info("Selenium WebDriver closed.")

    def _safe_find_element(self, by, value, timeout=10, el=None):
        """Safely finds a single element with an explicit wait."""
        context = el if el else self.selenium_driver
        if context is None: return None
        try:
            return WebDriverWait(context, timeout).until(
                EC.presence_of_element_located((by, value))
            )
        except (TimeoutException, SeleniumWebDriverException):
            logger.warning(f"Element not found within {timeout}s: {by}={value}")
            return None

    def _safe_find_elements(self, by, value, timeout=10, el=None):
        """Safely finds multiple elements with an explicit wait."""
        context = el if el else self.selenium_driver
        if context is None: return []
        try:
            return WebDriverWait(context, timeout).until(
                EC.presence_of_all_elements_located((by, value))
            )
        except (TimeoutException, SeleniumWebDriverException):
            logger.warning(f"No elements found within {timeout}s: {by}={value}")
            return []
            
    def _extract_experience_years(self, text: str) -> Tuple[Optional[int], Optional[int]]:
        """Extracts min and max experience years from a given text string."""
        min_exp, max_exp = None, None
        if not text:
            return min_exp, max_exp
        text_lower = text.lower()

        # Try explicit numeric patterns first
        match_range = re.search(r'(\d+)\s*-\s*(\d+)\s*(?:years?|yrs?)', text_lower)
        if match_range:
            min_exp = int(match_range.group(1))
            max_exp = int(match_range.group(2))
        else:
            match_plus = re.search(r'(\d+)\s*\+\s*(?:years?|yrs?)', text_lower)
            if match_plus:
                min_exp = int(match_plus.group(1))
                max_exp = None
            else:
                match_single = re.search(r'(\d+)\s*(?:years?|yrs?)', text_lower)
                if match_single:
                    min_exp = int(match_single.group(1))
                    max_exp = int(match_single.group(1))
                else:
                    # Heuristic fallbacks from seniority cues
                    if 'entry level' in text_lower or 'junior' in text_lower:
                        min_exp, max_exp = 0, 2
                    elif 'mid level' in text_lower or 'intermediate' in text_lower:
                        min_exp, max_exp = 3, 7
                    elif 'senior' in text_lower or 'lead' in text_lower or 'staff' in text_lower:
                        min_exp, max_exp = 8, None

        return min_exp, max_exp

    def _extract_keywords_from_description(self, description: str, keywords_list: List[str]) -> List[str]:
        """Extracts relevant keywords from job description."""
        found_keywords = []
        desc_lower = description.lower()
        for keyword in keywords_list:
            if keyword.lower() in desc_lower:
                found_keywords.append(keyword)
        return list(set(found_keywords))

    def _get_multiplier(self, key: str, types: List[str], default: float = 1.0) -> float:
        """Return the first matching custom score multiplier for the given key across possible types."""
        for t in types:
            val = self.custom_scores.get((key, t))
            if val is not None:
                return float(val)
        return default

    def _calculate_relevance_score(self, job: Job) -> float:
        """
        Calculates a relevance score for a job based on search terms,
        extracted keywords, experience level, and user-defined custom scores.
        """
        score = 0.0
        job_title_lower = job.title.lower()
        job_description_lower = job.description.lower()

        for term in self.search_terms:
            if term.lower() in job_title_lower:
                score += RELEVANCE_WEIGHTS['term_in_title'] * self._get_multiplier(term.lower(), ['keyword', 'keywords'])
            elif term.lower() in job_description_lower:
                score += RELEVANCE_WEIGHTS['term_in_desc'] * self._get_multiplier(term.lower(), ['keyword', 'keywords'])

        for skill in job.skills:
            score += RELEVANCE_WEIGHTS['skill'] * self._get_multiplier(skill.lower(), ['skill', 'skills'])
        for tool in job.extracted_tools:
            score += RELEVANCE_WEIGHTS['tool'] * self._get_multiplier(tool.lower(), ['tool', 'tools', 'tools_platforms'])
        for soft_skill in job.extracted_soft_skills:
            score += RELEVANCE_WEIGHTS['soft_skill'] * self._get_multiplier(soft_skill.lower(), ['soft_skill', 'soft_skills'])

        for word in re.findall(r'\b\w+\b', job_title_lower):
            score += RELEVANCE_WEIGHTS['title_word'] * self._get_multiplier(word, ['title_word', 'title'])

        if self.experience:
            user_min_exp, user_max_exp = self._extract_experience_years(self.experience)
            if user_min_exp is not None:
                if job.min_experience_years is not None and job.max_experience_years is not None:
                    if max(user_min_exp, job.min_experience_years) <= min(user_max_exp if user_max_exp is not None else float('inf'), job.max_experience_years if job.max_experience_years is not None else float('inf')):
                        score += RELEVANCE_WEIGHTS['exp_match']
                elif job.min_experience_years is not None and job.max_experience_years is None:
                    if user_min_exp >= job.min_experience_years:
                        score += RELEVANCE_WEIGHTS['exp_match']
                elif job.min_experience_years is None and user_max_exp is None:
                    score += RELEVANCE_WEIGHTS['exp_match'] * 0.5 # Partial match for open-ended
                elif job.min_experience_years is None:
                    exp_match_keywords = self._extract_keywords_from_description(job.experience, re.findall(r'\b\w+\b', self.experience.lower()))
                    if exp_match_keywords:
                        score += RELEVANCE_WEIGHTS['exp_partial']

        if self.location and self.location.lower() in job.location.lower():
            score += RELEVANCE_WEIGHTS['location']

        if self.job_type and self.job_type.lower() in job.job_type.lower():
            score += RELEVANCE_WEIGHTS['job_type']

        try:
            if 'ago' in job.posted_date.lower():
                num, unit = job.posted_date.lower().replace('posted', '').replace('ago', '').strip().split(' ')[:2]
                num = int(num)
                if 'hour' in unit:
                    posted_date = datetime.datetime.now() - datetime.timedelta(hours=num)
                elif 'day' in unit:
                    posted_date = datetime.datetime.now() - datetime.timedelta(days=num)
                elif 'week' in unit:
                    posted_date = datetime.datetime.now() - datetime.timedelta(weeks=num)
                elif 'month' in unit:
                    posted_date = datetime.datetime.now() - datetime.timedelta(days=num * 30)
                else:
                    posted_date = datetime.datetime.min
            else:
                posted_date = datetime.datetime.strptime(job.posted_date, '%Y-%m-%d')
        except (ValueError, AttributeError):
            posted_date = datetime.datetime.min

        days_ago = (datetime.datetime.now() - posted_date).days
        if days_ago <= 7:
            score *= RECENCY_MULTIPLIERS['week']
        elif days_ago <= 30:
            score *= RECENCY_MULTIPLIERS['month']

        return round(score, 2)


    def scrape_linkedin_jobs(self, term: str) -> List[Job]:
        """
        Updated LinkedIn scraper: robust, stealthy, paginated, and handles anti-bot measures.
        """
        logger.info(f"[LinkedIn] Scraping for term '{term}' in {self.location or 'All Locations'}...")
        jobs = []
        seen_links = set()
        max_pages = 3  # Limit pages to avoid throttling
        base_url = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
        proxies = None  # Add proxy support if needed

        for page in range(max_pages):
            logger.info(f"[LinkedIn] --- Starting scrape for page {page + 1} of {max_pages} for term '{term}' ---")
            params = {
                'keywords': term,
                'location': self.location,
                'start': page * 25,
                'count': 25
            }
            headers = {'User-Agent': random.choice(USER_AGENTS)}
            try:
                logger.info(f"[LinkedIn] Sending request to LinkedIn for job list (page {page + 1})...")
                time.sleep(random.uniform(2, 5))  # Random delay to avoid detection
                response = requests.get(base_url, params=params, headers=headers, timeout=15, proxies=proxies)

                if response.status_code != 200:
                    logger.warning(f"[LinkedIn] LinkedIn returned status {response.status_code} on page {page + 1}. Stopping further requests.")
                    break

                if b'captcha' in response.content.lower() or b'login' in response.content.lower():
                    logger.warning(f"[LinkedIn] Bot detection or login wall hit on page {page + 1}. Stopping scrape for this term.")
                    break

                try:
                    soup = BeautifulSoup(response.content, 'lxml')
                except Exception:
                    soup = BeautifulSoup(response.content, 'html.parser')

                # More robust selector for job cards
                job_cards = soup.select('div.job-card-container, div.base-card, li.job-result-card')
                if not job_cards:
                    logger.info(f"[LinkedIn] No job cards found on page {page + 1}. Stopping for this term.")
                    break

                logger.info(f"[LinkedIn] Found {len(job_cards)} job cards on page {page + 1}.")
                job_details = []

                for card in job_cards:
                    try:
                        # More robust selectors with fallbacks
                        title_elem = card.select_one('h3.base-search-card__title, h3.job-card-list__title')
                        title = title_elem.text.strip() if title_elem else 'N/A'

                        company_elem = card.select_one('h4.base-search-card__subtitle, h4.job-card-container__company-name')
                        company = company_elem.text.strip() if company_elem else 'N/A'

                        location_elem = card.select_one('span.job-search-card__location, span.job-card-container__metadata-item')
                        location = location_elem.text.strip() if location_elem else 'N/A'

                        link_elem = card.select_one('a.base-card__full-link, a.job-card-container__link')
                        link = link_elem.get('href') if link_elem and link_elem.get('href') else 'N/A'
                        # Add a fallback for the link
                        if link == 'N/A':
                            link_elem = card.find('a', href=True)
                            if link_elem:
                                link = link_elem.get('href')

                        if link in seen_links or link == 'N/A':
                            continue
                        seen_links.add(link)

                        posted_date_elem = card.find('time')
                        posted_date = posted_date_elem.text.strip() if posted_date_elem else 'N/A'

                        job_details.append({
                            'title': title,
                            'company': company,
                            'location': location,
                            'link': link,
                            'posted_date': posted_date
                        })
                    except Exception as e:
                        logger.warning(f"[LinkedIn] Error extracting job card: {e}", exc_info=True)
                        continue

                logger.info(f"[LinkedIn] Now fetching full job descriptions for {len(job_details)} jobs on page {page + 1}...")

                def fetch_description(job):
                    try:
                        logger.info(f"[LinkedIn] Fetching job detail page: {job['link']}")
                        detail_headers = {'User-Agent': random.choice(USER_AGENTS)}
                        time.sleep(random.uniform(2.5, 5.5)) # Increased delay to avoid 429 errors
                        resp = requests.get(job['link'], headers=detail_headers, timeout=15)

                        if resp.status_code == 200:
                            detail_soup = BeautifulSoup(resp.content, 'lxml')
                            desc_elem = detail_soup.find('div', class_=lambda x: x and 'description' in x)
                            description = desc_elem.get_text(separator=' ', strip=True) if desc_elem else 'N/A'
                            logger.info(f"[LinkedIn] Successfully fetched description for job: {job['title']} at {job['company']}")
                        else:
                            description = 'N/A'
                            logger.warning(f"[LinkedIn] Failed to fetch job detail page (status {resp.status_code}) for {job['link']}")
                    except Exception as e:
                        logger.warning(f"[LinkedIn] Error fetching job detail page: {e}")
                        description = 'N/A'

                    job['description'] = description
                    job['source'] = 'LinkedIn'
                    return job

                with concurrent.futures.ThreadPoolExecutor(max_workers=LINKEDIN_DETAIL_MAX_WORKERS) as executor:
                    enriched_jobs = list(executor.map(fetch_description, job_details))

                logger.info(f"[LinkedIn] Finished fetching all job descriptions for page {page + 1}.")
                for job in enriched_jobs:
                    jobs.append(self._create_job_object_from_raw_data(job))

                if len(job_cards) < 10:
                    logger.info(f"[LinkedIn] Less than 10 jobs found on page {page + 1}, assuming last page.")
                    break
            except requests.exceptions.RequestException as e:
                logger.error(f"[LinkedIn] Network error on page {page + 1} for '{term}': {e}", exc_info=True)
                continue
            except Exception as e:
                logger.error(f"[LinkedIn] Unexpected error on page {page + 1} for '{term}': {e}", exc_info=True)
                continue

        logger.info(f"[LinkedIn] ✅ Finished scraping. Total jobs scraped for '{term}': {len(jobs)}.")
        return jobs
    
    def scrape_internshala_jobs(self, term: str) -> List[Job]:
        """
        Enhanced Internshala scraper with improved resilience, better error handling,
        and support for the latest website structure (2025).
        """
        logger.info(f"[Internshala] Starting enhanced scrape for term '{term}' in {self.location or 'All Locations'}...")
        jobs = []
        seen_links = set()
        max_pages = 5  # Increased to get more results
        
        # Enhanced URL generation with better slug handling
        term_slug = self._create_url_slug(term)
        base_url = "https://internshala.com/jobs/"
        
        # Determine URL format based on location
        url_params = self._build_url_params(term_slug)
        
        if self.location:
            is_remote = self.location.lower() in ['remote', 'work from home', 'wfh', 'online']
            
            if is_remote:
                base_url += f"work-from-home/{term_slug}/"
                logger.info(f"[Internshala] Using remote job URL: {base_url}")
            else:
                # Handle location-specific searches
                primary_location = self.location.split(',')[0].strip()
                location_slug = self._create_url_slug(primary_location)
                base_url += f"{term_slug}-in-{location_slug}/"
                logger.info(f"[Internshala] Using location-based URL: {base_url}")
        else:
            base_url += f"{term_slug}/"
            logger.info(f"[Internshala] Using general job URL: {base_url}")
        
        job_details_from_list = []
        
        # Enhanced session with better configuration
        with requests.Session() as session:
            session.headers.update({
                'User-Agent': random.choice(USER_AGENTS),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'Accept-Language': 'en-US,en;q=0.9,hi;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Cache-Control': 'no-cache',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'same-origin'
            })
            
            # Set initial referer
            referer = 'https://internshala.com/'
            
            for page in range(1, max_pages + 1):
                url = f"{base_url}?page={page}" if page > 1 else base_url
                
                try:
                    logger.info(f"[Internshala] Scraping page {page}: {url}")
                    session.headers['Referer'] = referer
                    
                    # Randomized delay to avoid detection
                    time.sleep(random.uniform(2.5, 5.0))
                    
                    response = session.get(url, timeout=20)
                    referer = url
                    
                    if response.status_code == 404:
                        logger.warning(f"[Internshala] Page not found (404): {url}")
                        break
                    elif response.status_code == 403:
                        logger.warning(f"[Internshala] Access forbidden (403). Possible rate limiting.")
                        time.sleep(10)  # Wait longer if blocked
                        continue
                    elif response.status_code != 200:
                        logger.warning(f"[Internshala] HTTP {response.status_code} on page {page}")
                        break
                    
                    soup = BeautifulSoup(response.content, 'lxml')
                    
                    # Enhanced page validation
                    if self._is_no_results_page(soup):
                        logger.info(f"[Internshala] No results found on page {page}")
                        break
                    
                    # Multiple selectors for job cards (fallback approach)
                    job_cards = self._extract_job_cards(soup)
                    
                    if not job_cards:
                        logger.info(f"[Internshala] No job cards found on page {page}")
                        break
                    
                    logger.info(f"[Internshala] Found {len(job_cards)} job cards on page {page}")
                    
                    # Process each job card
                    for card in job_cards:
                        job_data = self._parse_job_card(card, seen_links)
                        if job_data:
                            job_details_from_list.append(job_data)
                    
                except requests.exceptions.Timeout:
                    logger.error(f"[Internshala] Timeout on page {page}")
                    break
                except requests.exceptions.RequestException as e:
                    logger.error(f"[Internshala] Network error on page {page}: {e}")
                    break
                except Exception as e:
                    logger.error(f"[Internshala] Unexpected error while scraping list page {page}: {e}", exc_info=True)
                    break
    
        if not job_details_from_list:
            logger.info(f"[Internshala] No jobs found for term '{term}'")
            return []
    
        logger.info(f"[Internshala] Found {len(job_details_from_list)} unique jobs. Fetching details...")
    
        # Fetch job details with enhanced concurrency
        with concurrent.futures.ThreadPoolExecutor(max_workers=SCRAPE_MAX_WORKERS) as executor:
            future_to_job = {
                executor.submit(self._fetch_job_details, job_data): job_data 
                for job_data in job_details_from_list
            }
            
            for future in concurrent.futures.as_completed(future_to_job):
                try:
                    enriched_job = future.result()
                    if enriched_job:
                        jobs.append(self._create_job_object_from_raw_data(enriched_job))
                except Exception as e:
                    logger.error(f"[Internshala] Error processing job detail: {e}")
    
        logger.info(f"[Internshala] ✅ Enhanced scrape completed. Total jobs: {len(jobs)}")
        return jobs

    def _create_url_slug(self, text: str) -> str:
        """Create URL-friendly slug from text."""
        slug = text.lower().strip()
        slug = re.sub(r'[^\w\s-]', '', slug)
        slug = re.sub(r'[\s_-]+', '-', slug)
        return slug.strip('-')

    def _build_url_params(self, term_slug: str) -> dict:
        """Build URL parameters for search."""
        return {
            'category': '',
            'type': 'job',
            'location': self.location or '',
            'search': term_slug
        }

    def _is_no_results_page(self, soup: BeautifulSoup) -> bool:
        """Check if page shows no results."""
        no_result_indicators = [
            '.no_internship_found',
            '.no-results',
            '.empty-state',
            '[data-testid="no-results"]'
        ]
        
        for selector in no_result_indicators:
            if soup.select_one(selector):
                return True
        
        # Check for text indicators
        page_text = soup.get_text().lower()
        if any(phrase in page_text for phrase in ['no jobs found', 'no results', 'no internships found']):
            return True
        
        return False

    def _extract_job_cards(self, soup: BeautifulSoup) -> list:
        """Extract job cards using multiple selectors."""
        selectors = [
            '.internship_meta',
            '.job_container',
            '.individual_internship',
            '[data-testid="job-card"]',
            '.search_results .container-fluid > div'
        ]
        
        for selector in selectors:
            cards = soup.select(selector)
            if cards:
                logger.debug(f"[Internshala] Found job cards using selector: {selector}")
                return cards
        
        return []

    def _parse_job_card(self, card: BeautifulSoup, seen_links: set) -> Optional[Dict]:
        """Parse individual job card."""
        try:
            # Enhanced link extraction
            link_selectors = [
                '.profile a',
                '.view_detail_button',
                '.job_title a',
                'a[href*="/job/"]',
                'a[href*="/jobs/detail/"]'
            ]
            
            link_elem = None
            for selector in link_selectors:
                link_elem = card.select_one(selector)
                if link_elem and link_elem.get('href'):
                    break
            
            if not link_elem or not link_elem.get('href'):
                return None
            
            href = link_elem['href']
            link = urljoin('https://internshala.com', href)
            
            if link in seen_links:
                return None
            seen_links.add(link)
            
            # Enhanced title extraction
            title_selectors = ['.profile a', '.job_title', '.heading_4_5 a', 'h3 a', 'h4 a']
            title = self._extract_text_by_selectors(card, title_selectors) or 'N/A'
            
            # Enhanced company extraction
            company_selectors = ['.company_name', '.company a', '.subtitle', '[data-testid="company-name"]']
            company = self._extract_text_by_selectors(card, company_selectors) or 'N/A'
            
            # Enhanced location extraction
            location_selectors = ['#location_names', '.location', '.job_location', '[data-testid="location"]']
            location = self._extract_text_by_selectors(card, location_selectors) or 'N/A'
            
            # Extract salary if available on card
            salary_selectors = ['.stipend', '.salary', '.package', '[data-testid="salary"]']
            salary = self._extract_text_by_selectors(card, salary_selectors) or 'N/A'
            
            return {
                'title': title,
                'company': company,
                'location': location,
                'salary': salary,
                'link': link,
            }
            
        except Exception as e:
            logger.warning(f"[Internshala] Error parsing job card: {e}")
            return None

    def _extract_text_by_selectors(self, element: BeautifulSoup, selectors: List[str]) -> Optional[str]:
        """Extract text using multiple selector fallbacks."""
        for selector in selectors:
            elem = element.select_one(selector)
            if elem:
                text = elem.get_text(strip=True)
                if text and text != 'N/A':
                    return text
        return None

    def _fetch_job_details(self, job_data: Dict) -> Optional[Dict]:
        """Fetch detailed job information."""
        link = job_data['link']
        
        try:
            logger.debug(f"[Internshala] Fetching details: {link}")
            
            # Randomized delay
            time.sleep(random.uniform(1.5, 3.5))
            
            headers = {
                'User-Agent': random.choice(USER_AGENTS),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': 'https://internshala.com/jobs/'
            }
            
            response = requests.get(link, headers=headers, timeout=20)
            
            if response.status_code != 200:
                logger.warning(f"[Internshala] Failed to fetch {link} (status: {response.status_code})")
                return None
            
            soup = BeautifulSoup(response.content, 'lxml')
            
            # Enhanced description extraction
            description = self._extract_description(soup)
            
            # Enhanced salary extraction (if not already found)
            if job_data.get('salary', 'N/A') == 'N/A':
                salary_selectors = ['.stipend', '.salary_container', '.ctc', '.package_container']
                job_data['salary'] = self._extract_text_by_selectors(soup, salary_selectors) or 'N/A'
            
            # Extract posted date
            posted_date = self._extract_posted_date(soup)
            
            # Extract skills/requirements
            skills = self._extract_skills(soup)
            
            # Extract experience
            experience = self._extract_experience(soup)
            
            # Extract job type
            job_type = self._extract_job_type(soup)
            
            # Extract application deadline
            deadline = self._extract_deadline(soup)
            
            job_data.update({
                'description': description,
                'posted_date': posted_date,
                'skills': skills,
                'experience': experience,
                'job_type': job_type,
                'deadline': deadline,
                'source': 'Internshala'
            })
            
            return job_data
            
        except Exception as e:
            logger.error(f"[Internshala] Error fetching details for {link}: {e}")
            return None

    def _create_job_object_from_raw_data(self, raw_data: Dict) -> Job:
        """Helper to create a Job object and calculate its relevance score."""
        salary = raw_data.get('salary', '')
        experience = raw_data.get('experience', '')

        # Use combined textual context (title, description, raw experience) for extraction
        title_txt = raw_data.get('title', '') or ''
        desc_txt = raw_data.get('description', '') or ''
        exp_txt = raw_data.get('experience', '') or ''
        combined_text = ' '.join([t for t in [title_txt, desc_txt, exp_txt] if t]).strip()
        if combined_text and (not salary or salary == 'N/A'):
            salary = self._extract_salary(combined_text)
        
        job_obj = Job(
            title=raw_data.get('title', ''),
            company=raw_data.get('company', ''),
            location=raw_data.get('location', ''),
            salary=salary,
            link=raw_data.get('link', ''),
            description=raw_data.get('description', ''),
            keywords=self.search_terms,
            skills=raw_data.get('skills') or self._extract_keywords_from_description(combined_text or desc_txt, self.common_skills),
            experience=experience,
            job_type=raw_data.get('job_type', 'Full-time'),
            posted_date=raw_data.get('posted_date', ''),
            source=raw_data.get('source', ''),
            deadline=raw_data.get('deadline', 'N/A')
        )
        # Derive experience years and keyword families from a broader context for robustness
        context_for_years = combined_text or job_obj.description
        job_obj.min_experience_years, job_obj.max_experience_years = self._extract_experience_years(context_for_years)
        job_obj.extracted_tools = self._extract_keywords_from_description(combined_text or job_obj.description, self.tools_platforms)
        job_obj.extracted_soft_skills = self._extract_keywords_from_description(combined_text or job_obj.description, self.soft_skills)
        job_obj.relevance_score = self._calculate_relevance_score(job_obj)
        return job_obj
        
    def _extract_salary(self, text: str) -> str:
        """Extracts salary information from text using regex patterns."""
        if not text:
            return "N/A"
        patterns = [
            # ₹ 30,00,000 - 33,00,000 /year or /month or per annum
            r'₹\s*[\d,]+(?:\s*-\s*[\d,]+)?\s*(?:/\s*year|/\s*month|per\s*annum|pa)?',
            # Rs. 15,00,000 - 20,00,000 per annum
            r'rs\.?\s*[\d,]+(?:\s*-\s*[\d,]+)?\s*(?:/\s*year|/\s*month|per\s*annum|pa)?',
            # 12 - 18 LPA, 12.5-15 lpa
            r'(?:\d+(?:\.\d+)?)\s*-\s*(?:\d+(?:\.\d+)?)\s*(?:lpa|lakhs?)',
            # CTC: ₹ 20,00,000 - 30,00,000
            r'ctc\s*[:\-]?\s*₹?\s*[\d,]+(?:\s*-\s*[\d,]+)?',
        ]
        for pattern in patterns:
            m = re.search(pattern, text, re.IGNORECASE)
            if m:
                return m.group(0).strip()
        return "N/A"

    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Extract job description with multiple fallbacks."""
        description_selectors = [
            '.internship_details .text-container',
            '.job_description',
            '.description_container',
            '.internship_details',
            '[data-testid="job-description"]'
        ]
        
        for selector in description_selectors:
            elem = soup.select_one(selector)
            if elem:
                description = elem.get_text(separator='\n', strip=True)
                if description and len(description) > 10:
                    return description
        
        return 'N/A'

    def _extract_posted_date(self, soup: BeautifulSoup) -> str:
        """Extract posted date."""
        date_selectors = [
            '.posted_on_container .status-container',
            '.posted_date',
            '.job_posted_date',
            '[data-testid="posted-date"]'
        ]
        
        posted_date = self._extract_text_by_selectors(soup, date_selectors)
        
        if posted_date:
            # Clean up posted date text
            posted_date = re.sub(r'Posted on\s*', '', posted_date, flags=re.IGNORECASE)
            posted_date = posted_date.strip()
        
        return posted_date or 'N/A'

    def _extract_skills(self, soup: BeautifulSoup) -> List[str]:
        """Extract required skills."""
        skills_selectors = [
            '.round_tabs_container .round_tabs',
            '.skills_required .skill',
            '.requirements .skill',
            '[data-testid="skill-tag"]'
        ]
        
        skills = []
        for selector in skills_selectors:
            skill_elements = soup.select(selector)
            if skill_elements:
                skills = [elem.get_text(strip=True) for elem in skill_elements]
                break
        
        return [skill for skill in skills if skill and skill.strip()]

    def _extract_experience(self, soup: BeautifulSoup) -> str:
        """Extract experience requirements."""
        # Look for experience section
        experience_headings = soup.find_all(['h3', 'h4', 'h5'], 
                                          string=re.compile(r'Experience|Experience Required', re.I))
        
        for heading in experience_headings:
            next_elem = heading.find_next_sibling(['div', 'p', 'span'])
            if next_elem:
                experience_text = next_elem.get_text(strip=True)
                if experience_text:
                    return experience_text
        
        # Fallback selectors
        exp_selectors = [
            '.experience_required',
            '.experience_container',
            '[data-testid="experience"]'
        ]
        
        return self._extract_text_by_selectors(soup, exp_selectors) or 'N/A'

    def _extract_job_type(self, soup: BeautifulSoup) -> str:
        """Extract job type (Full-time, Part-time, etc.)."""
        type_selectors = [
            '.job_type',
            '.employment_type',
            '.type_container',
            '[data-testid="job-type"]'
        ]
        
        job_type = self._extract_text_by_selectors(soup, type_selectors)
        
        if not job_type:
            # Infer from URL or content
            url = soup.find('link', {'rel': 'canonical'})
            if url and 'internship' in url.get('href', '').lower():
                return 'Internship'
            else:
                return 'Full-time'  # Default assumption for jobs
        
        return job_type

    def _extract_deadline(self, soup: BeautifulSoup) -> str:
        """Extract application deadline."""
        deadline_selectors = [
            '.application_deadline',
            '.last_date',
            '.deadline_container',
            '[data-testid="deadline"]'
        ]
        
        return self._extract_text_by_selectors(soup, deadline_selectors) or 'N/A'

    def scrape_all_sources(self) -> List[Job]:
        """Scrapes jobs from all configured sources concurrently."""
        all_jobs = []
        scraper_methods = {
            'LinkedIn': self.scrape_linkedin_jobs,
            'Internshala': self.scrape_internshala_jobs
        }

        if self.task:
            self.task.update_state(state='PROGRESS', meta={'status': 'Initializing scrapers for multiple sources...', 'progress': 10})

        total_scrapers = len(self.search_terms) * len(scraper_methods)
        scrapers_done = 0
        progress_start = 10
        progress_range = 70 # Scraping happens between 10% and 80%

        with concurrent.futures.ThreadPoolExecutor(max_workers=SCRAPE_MAX_WORKERS) as executor:
            future_to_source = {}
            for name, method in scraper_methods.items():
                for term in self.search_terms:
                    future = executor.submit(method, term)
                    future_to_source[future] = f"{name}-{term}"
            
            for future in concurrent.futures.as_completed(future_to_source):
                source_info = future_to_source[future]
                try:
                    jobs_from_source = future.result()
                    all_jobs.extend(jobs_from_source)
                    logger.info(f"Finished scraping {source_info}. Found {len(jobs_from_source)} jobs.")
                    
                    scrapers_done += 1
                    progress = progress_start + int((scrapers_done / total_scrapers) * progress_range)
                    if self.task:
                        self.task.update_state(state='PROGRESS', meta={'status': f'Finished scraping {source_info}. Found {len(jobs_from_source)} jobs.', 'progress': progress})

                except Exception as exc:
                    logger.error(f'{source_info} generated an exception: {exc}', exc_info=True)
                    
        logger.info(f"Total jobs scraped across all sources before deduplication: {len(all_jobs)}.")
        
        if self.task:
            self.task.update_state(state='PROGRESS', meta={'status': 'Deduplicating and scoring jobs...', 'progress': 85})

        unique_jobs = {}
        for job in all_jobs:
            norm = f"{normalize_for_hash(job.title)}|{normalize_for_hash(job.company)}|{normalize_for_hash(job.location)}"
            key = hashlib.md5(norm.encode('utf-8')).hexdigest()
            if key not in unique_jobs or job.relevance_score > unique_jobs[key].relevance_score:
                unique_jobs[key] = job
        
        filtered_jobs = list(unique_jobs.values())
        filtered_jobs = [job for job in filtered_jobs if job.title and job.title != 'N/A' and job.link and job.link != 'N/A']

        # Location filtering removed: all jobs are included regardless of location.

        if self.task:
            self.task.update_state(state='PROGRESS', meta={'status': 'Filtering by relevance score...', 'progress': 88})

        high_relevance_jobs = [job for job in filtered_jobs if job.relevance_score >= RELEVANCE_MIN_THRESHOLD]
        high_relevance_jobs.sort(key=lambda x: x.relevance_score, reverse=True)
        
        logger.info(f"Jobs count after filtering by relevance_score >= 10: {len(high_relevance_jobs)}.")
        
        source_counts = Counter(job.source for job in high_relevance_jobs)
        for source, count in source_counts.items():
            logger.info(f"Final jobs from {source}: {count}.")
            
        return high_relevance_jobs[:50]

class ApplicationFiller:
    """Automated job application filler for various ATS platforms"""
    
    def __init__(self, driver: webdriver.Remote, user_details: Dict):
        self.driver = driver
        self.user_details = user_details
        self.wait = WebDriverWait(driver, 10)
        # Extract parsed data and preferences for easier access
        self.resume_data = self.user_details.get('parsed_resume', {})
        self.preferences = {
            'willing_to_relocate': self.user_details.get('willing_to_relocate', 'no'),
            'authorized_to_work': self.user_details.get('authorized_to_work', 'no')
        }
        
    def fill(self, url: str) -> bool:
        """Fill application form based on URL pattern"""
        try:
            self.driver.get(url)
            time.sleep(2)  # Allow page to load
            
            # This is a generic flag to indicate if we should try answering questions.
            # Specific implementations for Lever, Greenhouse etc. will call this.
            should_answer_questions = True
            
            if "greenhouse.io" in url:
                return self.fill_greenhouse()
            elif "jobs.lever.co" in url:
                return self.fill_lever()
            elif "workday.com" in url or "myworkdayjobs.com" in url:
                return self.fill_workday()
            elif "bamboohr.com" in url:
                return self.fill_bamboohr()
            elif "smartrecruiters.com" in url:
                return self.fill_smartrecruiters()
            elif "jobvite.com" in url:
                return self.fill_jobvite()
            else:
                # For unknown sites, we still try the generic fill and question answering
                filled_generic = self.fill_generic()
                if filled_generic and should_answer_questions:
                    self.answer_custom_questions()
                logger.info(f"Attempting generic form fill for: {url}")
                return self.fill_generic()
                
        except Exception as e:
            logger.error(f"Error filling application at {url}: {str(e)}")
            return False

    def safe_send_keys(self, element, text: str) -> bool:
        """Safely send keys to an element"""
        try:
            if element and text:
                element.clear()
                element.send_keys(text)
                return True
        except Exception as e:
            logger.warning(f"Failed to send keys: {str(e)}")
        return False

    def find_element_by_multiple_selectors(self, selectors: List[str], timeout: int = 5):
        """Try multiple selectors to find an element"""
        for selector in selectors:
            try:
                if selector.startswith('//'):
                    element = WebDriverWait(self.driver, timeout).until(
                        EC.presence_of_element_located((By.XPATH, selector))
                    )
                elif selector.startswith('#'):
                    element = WebDriverWait(self.driver, timeout).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                else: # Assumes NAME or other simple locators if not XPath/CSS
                    element = WebDriverWait(self.driver, timeout).until(
                        EC.presence_of_element_located((By.NAME, selector))
                    )
                return element
            except TimeoutException:
                continue
        return None

    def fill_greenhouse(self) -> bool:
        """Fill Greenhouse application forms"""
        logger.info("Filling Greenhouse application...")
        
        try:
            # Common Greenhouse field mappings
            field_mappings = {
                'first_name': ['first_name', 'firstName', '#first_name'],
                'last_name': ['last_name', 'lastName', '#last_name'],
                'email': ['email', 'email_address', '#email'],
                'phone': ['phone', 'phone_number', '#phone'],
                'resume': ['resume', 'resume_file', 'input[type="file"]'],
                'cover_letter': ['cover_letter', 'coverLetter', 'cover_letter_text'],
                'linkedin': ['linkedin', 'linkedin_url', '#linkedin']
            }
            
            # Fill basic fields
            for field_key, selectors in field_mappings.items():
                if field_key in self.user_details:
                    element = self.find_element_by_multiple_selectors(selectors)
                    if element:
                        if field_key == 'resume' and element.get_attribute('type') == 'file':
                            element.send_keys(self.user_details[field_key])
                        else:
                            self.safe_send_keys(element, self.user_details[field_key])
            
            self.handle_dropdowns()
            self.answer_custom_questions()
            self.fill_custom_questions()
            return True
        except Exception as e:
            logger.error(f"Error in Greenhouse form fill: {str(e)}")
            return False

    def fill_lever(self) -> bool:
        """Fill Lever application forms"""
        logger.info("Filling Lever application...")
        try:
            self.safe_send_keys(self.find_element_by_multiple_selectors(['input[name="name"]']), self.user_details.get('full_name', ''))
            self.safe_send_keys(self.find_element_by_multiple_selectors(['input[name="email"]']), self.user_details.get('email', ''))
            self.safe_send_keys(self.find_element_by_multiple_selectors(['input[name="phone"]']), self.user_details.get('phone', ''))
            resume_upload = self.find_element_by_multiple_selectors(['input[name="resume"]', 'input[type="file"]'])
            if resume_upload and 'resume' in self.user_details:
                resume_upload.send_keys(self.user_details['resume'])
            self.answer_custom_questions()
            return True
        except Exception as e:
            logger.error(f"Error in Lever form fill: {str(e)}")
            return False

    def fill_workday(self) -> bool:
        """Fill Workday application forms"""
        logger.info("Filling Workday application...")
        try:
            time.sleep(3)
            self.safe_send_keys(self.find_element_by_multiple_selectors(['input[data-automation-id="firstName"]']), self.user_details.get('first_name', ''))
            self.safe_send_keys(self.find_element_by_multiple_selectors(['input[data-automation-id="lastName"]']), self.user_details.get('last_name', ''))
            self.safe_send_keys(self.find_element_by_multiple_selectors(['input[data-automation-id="email"]']), self.user_details.get('email', ''))
            self.safe_send_keys(self.find_element_by_multiple_selectors(['input[data-automation-id="phone"]']), self.user_details.get('phone', ''))
            self.answer_custom_questions()
            return True
        except Exception as e:
            logger.error(f"Error in Workday form fill: {str(e)}")
            return False

    def fill_bamboohr(self) -> bool:
        logger.info("Filling BambooHR application...")
        try:
            self.safe_send_keys(self.find_element_by_multiple_selectors(['input[name*="firstName"]']), self.user_details.get('first_name', ''))
            self.safe_send_keys(self.find_element_by_multiple_selectors(['input[name*="lastName"]']), self.user_details.get('last_name', ''))
            self.safe_send_keys(self.find_element_by_multiple_selectors(['input[name*="email"]']), self.user_details.get('email', ''))
            self.safe_send_keys(self.find_element_by_multiple_selectors(['input[name*="phone"]']), self.user_details.get('phone', ''))
            self.answer_custom_questions()
            return True
        except Exception as e:
            logger.error(f"Error in BambooHR form fill: {str(e)}")
            return False

    def fill_smartrecruiters(self) -> bool:
        logger.info("Filling SmartRecruiters application...")
        try:
            self.safe_send_keys(self.find_element_by_multiple_selectors(['input[name="firstName"]']), self.user_details.get('first_name', ''))
            self.safe_send_keys(self.find_element_by_multiple_selectors(['input[name="lastName"]']), self.user_details.get('last_name', ''))
            self.safe_send_keys(self.find_element_by_multiple_selectors(['input[name="email"]']), self.user_details.get('email', ''))
            self.answer_custom_questions()
            return True
        except Exception as e:
            logger.error(f"Error in SmartRecruiters form fill: {str(e)}")
            return False

    def fill_jobvite(self) -> bool:
        logger.info("Filling Jobvite application...")
        try:
            self.safe_send_keys(self.find_element_by_multiple_selectors(['input[name="firstName"]']), self.user_details.get('first_name', ''))
            self.safe_send_keys(self.find_element_by_multiple_selectors(['input[name="lastName"]']), self.user_details.get('last_name', ''))
            self.safe_send_keys(self.find_element_by_multiple_selectors(['input[name="email"]']), self.user_details.get('email', ''))
            self.safe_send_keys(self.find_element_by_multiple_selectors(['input[name="phone"]']), self.user_details.get('phone', ''))
            self.answer_custom_questions()
            return True
        except Exception as e:
            logger.error(f"Error in Jobvite form fill: {str(e)}")
            return False

    def fill_generic(self) -> bool:
        logger.info("Attempting generic form fill...")
        try:
            self.safe_send_keys(self.find_element_by_multiple_selectors(['input[name*="first"]', 'input[placeholder*="first name"]']), self.user_details.get('first_name', ''))
            self.safe_send_keys(self.find_element_by_multiple_selectors(['input[name*="last"]', 'input[placeholder*="last name"]']), self.user_details.get('last_name', ''))
            self.safe_send_keys(self.find_element_by_multiple_selectors(['input[name*="full"]', 'input[placeholder*="full name"]']), self.user_details.get('full_name', ''))
            self.safe_send_keys(self.find_element_by_multiple_selectors(['input[type="email"]', 'input[name*="email"]']), self.user_details.get('email', ''))
            self.safe_send_keys(self.find_element_by_multiple_selectors(['input[type="tel"]', 'input[name*="phone"]']), self.user_details.get('phone', ''))
            return True
        except Exception as e:
            logger.error(f"Error in generic form fill: {str(e)}")
            return False

    def handle_dropdowns(self):
        try:
            if 'experience_level' in self.user_details:
                exp_dropdown = self.find_element_by_multiple_selectors(['select[name*="experience"]', 'select[id*="experience"]'])
                if exp_dropdown: Select(exp_dropdown).select_by_visible_text(self.user_details['experience_level'])
            if 'country' in self.user_details:
                country_dropdown = self.find_element_by_multiple_selectors(['select[name*="country"]', 'select[id*="country"]'])
                if country_dropdown: Select(country_dropdown).select_by_visible_text(self.user_details['country'])
        except Exception as e:
            logger.warning(f"Error handling dropdowns: {str(e)}")

    def fill_custom_questions(self):
        try:
            for textarea in self.driver.find_elements(By.TAG_NAME, "textarea"):
                label = self.get_field_label(textarea)
                if label and 'custom_answers' in self.user_details:
                    answer = self.user_details.get('custom_answers', {}).get(label.lower(), self.user_details.get('default_answer', ''))
                    self.safe_send_keys(textarea, answer)
        except Exception as e:
            logger.warning(f"Error filling custom questions: {str(e)}")

    def get_field_label(self, element):
        try:
            field_id = element.get_attribute('id')
            if field_id: return self.driver.find_element(By.CSS_SELECTOR, f'label[for="{field_id}"]').text.strip()
            return element.find_element(By.XPATH, '..').text.strip()
        except: return None

    def answer_custom_questions(self):
        """Finds and answers custom questions on a page."""
        logger.info("[AssistApply] Searching for custom questions to answer...")
        # Generic selectors for question containers. LinkedIn uses the 'jobs-easy-apply-form-section__grouping' class.
        question_containers = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'form-question') or contains(@class, 'jobs-easy-apply-form-section__grouping') or contains(@class, 'fb-form-element')]")
        
        if not question_containers:
            logger.info("[AssistApply] No custom question containers found.")
            return

        for container in question_containers:
            try:
                label_el = container.find_element(By.TAG_NAME, 'label')
                question_text = label_el.text
                if not question_text:
                    continue

                answer = self._generate_answer(question_text)
                if answer is None:
                    logger.info(f"[AssistApply] No answer generated for question: '{question_text}'")
                    continue

                # Find the input/select/textarea associated with the label
                input_id = label_el.get_attribute('for')
                if input_id:
                    input_el = self.driver.find_element(By.ID, input_id)
                else: # Fallback for inputs not linked by 'for'
                    input_el = container.find_element(By.CSS_SELECTOR, 'input, select, textarea')

                # Now fill the element based on its type
                if input_el.tag_name == 'select':
                    self._select_answer(input_el, answer)
                elif input_el.get_attribute('type') in ['radio', 'checkbox']:
                    self._check_answer(container, answer)
                else: # Text input or textarea
                    self.safe_send_keys(input_el, answer)
                
                logger.info(f"[AssistApply] Answered '{question_text}' with '{answer}'")
                time.sleep(0.5) # Small delay after answering

            except NoSuchElementException:
                continue # Skip if a container doesn't have the expected structure
            except Exception as e:
                logger.warning(f"[AssistApply] Error processing a question container: {e}")

    def _generate_answer(self, question_text: str) -> Optional[str]:
        """Generates an answer based on question text and user data."""
        q_lower = question_text.lower()

        # Years of experience
        match = re.search(r'(?:how many|how much) years of experience.* with ([\w\s\+\#\.\-]+)\??', q_lower)
        if match:
            skill = match.group(1).strip().replace('.', r'\.') # Sanitize for regex
            return self._calculate_years_for_skill(skill)

        # Relocation
        if 'relocate' in q_lower or 'commute' in q_lower or 'relocation' in q_lower:
            return 'Yes' if self.preferences['willing_to_relocate'] == 'yes' else 'No'

        # Work Authorization & Sponsorship
        # Check for sponsorship first, as it's a more specific keyword.
        if 'sponsorship' in q_lower or 'visa' in q_lower:
            # If authorized, you don't need sponsorship.
            return 'No' if self.preferences['authorized_to_work'] == 'yes' else 'Yes'
        
        if 'legally authorized' in q_lower or 'work authorization' in q_lower or 'work permit' in q_lower or 'right to work' in q_lower:
            # This question is "Are you authorized?".
            if self.preferences['authorized_to_work'] == 'yes':
                return 'Yes'
            else:
                # Return a more specific string to help match dropdowns like "No, I require sponsorship".
                return 'No, I require sponsorship'

        # EEO Questions - Default to "Decline to self-identify" for privacy and safety.
        if 'gender' in q_lower or 'race' in q_lower or 'ethnicity' in q_lower or 'veteran' in q_lower or 'disability' in q_lower:
            return 'Decline to self-identify'

        return None

    def _calculate_years_for_skill(self, skill_name: str) -> str:
        """Calculates total years of experience for a skill from parsed resume data."""
        work_experience = self.resume_data.get('work_experience', [])
        if not work_experience:
            return "0"

        # This is a simplified date parser for demonstration
        def parse_date(date_str):
            if 'present' in date_str.lower(): return datetime.datetime.now()
            for fmt in ('%b %Y', '%B %Y', '%Y'):
                try: return datetime.datetime.strptime(date_str, fmt)
                except ValueError: pass
            return None

        relevant_periods = []
        for job in work_experience:
            context = (job.get('title', '') + ' ' + job.get('description', '')).lower()
            if re.search(r'\b' + re.escape(skill_name.lower()) + r'\b', context):
                start = parse_date(job.get('start_date', ''))
                end = parse_date(job.get('end_date', 'Present'))
                if start and end:
                    relevant_periods.append((start, end))
        
        if not relevant_periods: return "0"

        relevant_periods.sort(key=lambda x: x[0])
        merged = []
        for start, end in relevant_periods:
            if not merged or start > merged[-1][1]: merged.append([start, end])
            else: merged[-1][1] = max(merged[-1][1], end)
        
        total_days = sum((end - start).days for start, end in merged)
        return str(round(total_days / 365.25))

    def _select_answer(self, select_el: webdriver.remote.webelement.WebElement, answer: str):
        """Selects an answer in a dropdown, trying partial text match."""
        try:
            select = Select(select_el)
            for option in select.options:
                if answer.lower() in option.text.lower():
                    select.select_by_visible_text(option.text); return
        except Exception as e: logger.warning(f"Could not select '{answer}' in dropdown: {e}")

    def _check_answer(self, container: webdriver.remote.webelement.WebElement, answer: str):
        """Finds and clicks a radio button or checkbox within a container."""
        try:
            options = container.find_elements(By.CSS_SELECTOR, 'input[type="radio"], input[type="checkbox"]')
            for option in options:
                if answer.lower() in option.find_element(By.XPATH, '..').text.lower():
                    option.click(); return
        except Exception as e: logger.warning(f"Could not check '{answer}' radio/checkbox: {e}")

    def submit_application(self) -> bool:
        try:
            submit_selectors = [
                'input[type="submit"]',
                'button[type="submit"]',
                'button[name*="submit"]',
                '.submit-btn',
                '[data-automation-id="submitApplication"]',
                '//button[contains(text(), "Submit")]',
                '//button[contains(text(), "Apply")]'
            ]
            submit_btn = self.find_element_by_multiple_selectors(submit_selectors)
            if submit_btn and submit_btn.is_enabled():
                submit_btn.click()
                logger.info("Application submitted successfully!")
                return True
            else:
                logger.warning("Submit button not found or not enabled")
                return False
        except Exception as e:
            logger.error(f"Error submitting application: {str(e)}")
            return False


class GoogleCalendarManager:
    """Enhanced Google Calendar integration for job application tracking."""
    def __init__(self):
        self.calendar_service = self.authenticate_calendar()
        self.job_alerts_calendar_id = None
        self.user_name = None
        self._initialize_calendar()
    
    def authenticate_calendar(self):
        """Authenticate with Google Calendar API using shared credentials."""
        # Use the same authentication as Gmail since we share the token
        gmail_service = SmartEmailer().authenticate_gmail()
        if not gmail_service:
            return None
        
        # Get the credentials from the gmail service
        creds = None
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        
        if not creds or not creds.valid:
            logger.error("No valid credentials for Calendar API")
            return None
        
        try:
            return build('calendar', 'v3', credentials=creds)
        except Exception as e:
            logger.error(f"Failed to build Calendar service: {e}")
            return None
    
    def _initialize_calendar(self):
        """Initialize the Job Alerts calendar and get user info."""
        if not self.calendar_service:
            return
        
        try:
            # Get user's name from their primary calendar
            primary_calendar = self.calendar_service.calendars().get(calendarId='primary').execute()
            self.user_name = primary_calendar.get('summary', 'User')
            
            # Find or create "Job Alerts" calendar
            self.job_alerts_calendar_id = self._get_or_create_job_alerts_calendar()
            
        except Exception as e:
            logger.error(f"Failed to initialize calendar: {e}")
    
    def _get_or_create_job_alerts_calendar(self) -> Optional[str]:
        """Find existing Job Alerts calendar or create a new one."""
        try:
            # List all calendars to find existing "Job Alerts" calendar
            calendar_list = self.calendar_service.calendarList().list().execute()
            
            for calendar in calendar_list.get('items', []):
                if calendar.get('summary') == 'Job Alerts':
                    logger.info(f"Found existing Job Alerts calendar: {calendar['id']}")
                    return calendar['id']
            
            # Create new "Job Alerts" calendar if not found
            calendar_body = {
                'summary': 'Job Alerts',
                'description': f'Automated job application tracking for {self.user_name}',
                'timeZone': 'UTC'
            }
            
            created_calendar = self.calendar_service.calendars().insert(body=calendar_body).execute()
            calendar_id = created_calendar['id']
            
            # Set calendar color to a nice blue
            calendar_list_entry = {
                'id': calendar_id,
                'colorId': '9'  # Blue color
            }
            self.calendar_service.calendarList().patch(
                calendarId=calendar_id, 
                body=calendar_list_entry
            ).execute()
            
            logger.info(f"Created new Job Alerts calendar: {calendar_id}")
            return calendar_id
            
        except Exception as e:
            logger.error(f"Failed to get/create Job Alerts calendar: {e}")
            return 'primary'  # Fallback to primary calendar
    
    def _get_existing_event_id(self, job_id: int, event_type: str) -> Optional[str]:
        """Check if an event already exists for this job to prevent duplicates."""
        if not self.job_alerts_calendar_id:
            return None
        
        try:
            # Search for existing events with this job ID in the description
            search_query = f"Job ID: {job_id}"
            events = self.calendar_service.events().list(
                calendarId=self.job_alerts_calendar_id,
                q=search_query,
                maxResults=50
            ).execute()
            
            for event in events.get('items', []):
                description = event.get('description', '')
                if f"Job ID: {job_id}" in description and event_type.lower() in event.get('summary', '').lower():
                    return event.get('id')
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to check for existing events: {e}")
            return None
    
    def _delete_existing_event(self, event_id: str):
        """Delete an existing calendar event."""
        try:
            self.calendar_service.events().delete(
                calendarId=self.job_alerts_calendar_id,
                eventId=event_id
            ).execute()
            logger.info(f"Deleted existing calendar event: {event_id}")
        except Exception as e:
            logger.error(f"Failed to delete existing event {event_id}: {e}")
    
    def create_interview_event(self, job_data: Dict) -> Optional[str]:
        """Create a calendar event when job status changes to 'interview'."""
        if not self.calendar_service or not self.job_alerts_calendar_id:
            logger.warning("Calendar service not available. Skipping interview event creation.")
            return None
        
        try:
            job_id = job_data.get('id')
            
            # Check for existing interview event and delete it
            existing_event_id = self._get_existing_event_id(job_id, 'interview')
            if existing_event_id:
                self._delete_existing_event(existing_event_id)
            
            # Default to next business day at 10 AM if no specific time provided
            interview_date = datetime.datetime.now() + datetime.timedelta(days=1)
            # Skip to Monday if it's weekend
            while interview_date.weekday() > 4:  # 0-4 is Mon-Fri
                interview_date += datetime.timedelta(days=1)
            
            interview_date = interview_date.replace(hour=10, minute=0, second=0, microsecond=0)
            end_time = interview_date + datetime.timedelta(hours=1)
            
            event = {
                'summary': f'🎯 Interview: {job_data.get("title", "Job")} at {job_data.get("company", "Company")}',
                'description': self._build_interview_description(job_data),
                'start': {
                    'dateTime': interview_date.isoformat(),
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': 'UTC',
                },
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'popup', 'minutes': 24 * 60},  # 1 day before
                        {'method': 'popup', 'minutes': 60},       # 1 hour before
                    ],
                },
                'colorId': '9',  # Blue color for interviews
            }
            
            result = self.calendar_service.events().insert(
                calendarId=self.job_alerts_calendar_id, 
                body=event
            ).execute()
            logger.info(f"Created interview calendar event in Job Alerts calendar: {result.get('id')}")
            return result.get('id')
            
        except Exception as e:
            logger.error(f"Failed to create interview calendar event: {e}")
            return None
    
    def create_deadline_reminder(self, job_data: Dict, deadline_str: str) -> Optional[str]:
        """Create a calendar reminder for application deadlines."""
        if not self.calendar_service or not self.job_alerts_calendar_id or not deadline_str or deadline_str == 'N/A':
            return None
        
        try:
            job_id = job_data.get('id')
            
            # Check for existing deadline event and delete it
            existing_event_id = self._get_existing_event_id(job_id, 'deadline')
            if existing_event_id:
                self._delete_existing_event(existing_event_id)
            
            # Parse deadline string (you might need to improve this parsing)
            deadline_date = self._parse_deadline(deadline_str)
            if not deadline_date:
                return None
            
            # Create all-day event for the deadline
            event = {
                'summary': f'⏰ Application Deadline: {job_data.get("title", "Job")} at {job_data.get("company", "Company")}',
                'description': self._build_deadline_description(job_data),
                'start': {
                    'date': deadline_date.strftime('%Y-%m-%d'),
                },
                'end': {
                    'date': deadline_date.strftime('%Y-%m-%d'),
                },
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'popup', 'minutes': 24 * 60 * 3},  # 3 days before
                        {'method': 'popup', 'minutes': 24 * 60},      # 1 day before
                    ],
                },
                'colorId': '11',  # Red color for deadlines
            }
            
            result = self.calendar_service.events().insert(
                calendarId=self.job_alerts_calendar_id, 
                body=event
            ).execute()
            logger.info(f"Created deadline reminder in Job Alerts calendar: {result.get('id')}")
            return result.get('id')
            
        except Exception as e:
            logger.error(f"Failed to create deadline reminder: {e}")
            return None
    
    def create_followup_reminder(self, job_data: Dict, status: str) -> Optional[str]:
        """Create follow-up reminders based on job status and company response patterns."""
        if not self.calendar_service or not self.job_alerts_calendar_id:
            return None
        
        try:
            job_id = job_data.get('id')
            
            # Check for existing follow-up event and delete it
            existing_event_id = self._get_existing_event_id(job_id, 'follow-up')
            if existing_event_id:
                self._delete_existing_event(existing_event_id)
            
            followup_date = self._calculate_followup_date(status)
            if not followup_date:
                return None
            
            followup_time = followup_date.replace(hour=9, minute=0, second=0, microsecond=0)
            end_time = followup_time + datetime.timedelta(minutes=30)
            
            event = {
                'summary': f'📞 Follow-up: {job_data.get("title", "Job")} at {job_data.get("company", "Company")}',
                'description': self._build_followup_description(job_data, status),
                'start': {
                    'dateTime': followup_time.isoformat(),
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': 'UTC',
                },
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'popup', 'minutes': 60},  # 1 hour before
                    ],
                },
                'colorId': '5',  # Yellow color for follow-ups
            }
            
            result = self.calendar_service.events().insert(
                calendarId=self.job_alerts_calendar_id, 
                body=event
            ).execute()
            logger.info(f"Created follow-up reminder in Job Alerts calendar: {result.get('id')}")
            return result.get('id')
            
        except Exception as e:
            logger.error(f"Failed to create follow-up reminder: {e}")
            return None
    
    def _build_interview_description(self, job_data: Dict) -> str:
        """Build detailed description for interview calendar event."""
        skills_list = job_data.get('skills', '').split(',')[:5] if job_data.get('skills') else []
        skills_text = ', '.join([skill.strip() for skill in skills_list]) if skills_list else 'Review job requirements'
        
        description = f"""🎯 INTERVIEW PREPARATION CHECKLIST for {self.user_name}

📋 Job Details:
• Position: {job_data.get('title', 'N/A')}
• Company: {job_data.get('company', 'N/A')}
• Location: {job_data.get('location', 'N/A')}
• Experience Level: {job_data.get('experience', 'N/A')}
• Job Type: {job_data.get('job_type', 'N/A')}
• Relevance Score: {job_data.get('relevance_score', 'N/A')}%

🔍 Pre-Interview Research (Complete 24-48 hours before):
□ Company mission, values, and recent news/press releases
□ Research interviewer(s) on LinkedIn
□ Review company's products/services and competitors
□ Understand the role's responsibilities and requirements
□ Prepare 3-5 thoughtful questions about the role/company
□ Practice common behavioral and technical questions

💼 Materials to Prepare:
□ 3-5 printed copies of updated resume
□ Portfolio/work samples relevant to the role
□ List of professional references with contact info
□ Notebook and pen for taking notes
□ Business cards (if you have them)
□ Directions and parking information

⚡ Key Skills & Experience to Highlight:
{skills_text}

🗣️ STAR Method Examples to Prepare:
□ Situation: Challenging project or problem you faced
□ Task: What you needed to accomplish
□ Action: Specific steps you took to address it
□ Result: Positive outcome and what you learned

❓ Questions to Ask Them:
□ "What does success look like in this role after 6 months?"
□ "What are the biggest challenges facing the team/department?"
□ "How would you describe the company culture?"
□ "What opportunities are there for professional development?"
□ "What are the next steps in the interview process?"

📝 Your Notes:
{job_data.get('notes', 'No additional notes')}

🔗 Original Job Posting: {job_data.get('link', 'N/A')}
📧 Follow-up: Send thank-you email within 24 hours after interview

---
Generated by AI Job Hunter for {self.user_name}
Job ID: {job_data.get('id', 'N/A')}
"""
        return description
    
    def _build_deadline_description(self, job_data: Dict) -> str:
        """Build description for deadline reminder."""
        return f"""⏰ APPLICATION DEADLINE TODAY for {self.user_name}!

📋 Job Details:
• Position: {job_data.get('title', 'N/A')}
• Company: {job_data.get('company', 'N/A')}
• Location: {job_data.get('location', 'N/A')}
• Experience Required: {job_data.get('experience', 'N/A')}
• Job Type: {job_data.get('job_type', 'N/A')}
• Relevance Score: {job_data.get('relevance_score', 'N/A')}%

✅ FINAL APPLICATION CHECKLIST - Complete Today:
□ Resume tailored specifically for {job_data.get('company', 'this company')}
□ Custom cover letter highlighting relevant experience and enthusiasm
□ Portfolio/work samples that demonstrate relevant skills
□ Professional references list (if requested)
□ Review all application requirements one final time
□ Proofread everything for typos and formatting
□ Submit application before 11:59 PM today!

🎯 Key Skills to Emphasize:
{', '.join(job_data.get('skills', '').split(',')[:3]) if job_data.get('skills') else 'Review job requirements'}

💡 Last-Minute Tips:
• Use keywords from the job description in your application
• Quantify your achievements with specific numbers/results
• Show genuine interest in the company and role
• Follow application instructions exactly as specified

📝 Your Notes:
{job_data.get('notes', 'No additional notes')}

🔗 Apply Here: {job_data.get('link', 'N/A')}

⚠️ URGENT: This is your final reminder - deadline is TODAY!

---
Generated by AI Job Hunter for {self.user_name}
Job ID: {job_data.get('id', 'N/A')}
"""
    
    def _build_followup_description(self, job_data: Dict, status: str) -> str:
        """Build description for follow-up reminder."""
        status_descriptions = {
            'applied': {
                'action': 'Send polite follow-up email asking about application timeline and next steps',
                'template': f"Hi [Hiring Manager], I hope this message finds you well. I recently submitted my application for the {job_data.get('title', '')} position at {job_data.get('company', '')} and wanted to follow up on the status. I remain very enthusiastic about this opportunity and would appreciate any updates on your timeline for next steps. Thank you for your time and consideration.",
                'tips': '• Keep it brief and professional\n• Show continued interest\n• Ask about timeline, not decision\n• Include your contact information'
            },
            'interview': {
                'action': 'Send thank-you note within 24 hours and reiterate your strong interest',
                'template': f"Dear [Interviewer Name], Thank you for taking the time to meet with me yesterday about the {job_data.get('title', '')} position. I enjoyed our conversation about [specific topic discussed] and am even more excited about the opportunity to contribute to {job_data.get('company', '')}. Please let me know if you need any additional information. I look forward to hearing about next steps.",
                'tips': '• Send within 24 hours\n• Reference specific conversation points\n• Reiterate key qualifications\n• Keep it concise but personal'
            },
            'offered': {
                'action': 'Respond to job offer professionally - accept, negotiate, or request more time',
                'template': f"Dear [Hiring Manager], Thank you for extending the offer for the {job_data.get('title', '')} position at {job_data.get('company', '')}. I am excited about this opportunity and would like to [accept/discuss terms/request additional time to consider]. [Include specific next steps or questions]. I appreciate your time and look forward to your response.",
                'tips': '• Respond promptly (within 2-3 business days)\n• Be gracious regardless of your decision\n• If negotiating, be specific and reasonable\n• Confirm details in writing'
            },
            'rejected': {
                'action': 'Request constructive feedback and maintain professional relationship for future opportunities',
                'template': f"Dear [Hiring Manager], Thank you for informing me about your decision regarding the {job_data.get('title', '')} position. While I'm disappointed, I understand these decisions are difficult. I would greatly appreciate any feedback you could share about my application or interview to help me improve. I remain interested in {job_data.get('company', '')} and would welcome the opportunity to be considered for future roles that match my background.",
                'tips': '• Stay positive and professional\n• Ask for specific feedback\n• Express continued interest in company\n• Keep the door open for future opportunities'
            }
        }
        
        status_info = status_descriptions.get(status, {
            'action': 'Follow up on application status',
            'template': f"Hi [Name], I wanted to follow up on my application for the {job_data.get('title', '')} position. I remain very interested in this opportunity and would appreciate any updates on the timeline. Thank you for your time and consideration.",
            'tips': '• Keep it professional and brief'
        })
        
        return f"""📞 FOLLOW-UP REMINDER - {status.upper()} STATUS

📋 Job Details:
• Position: {job_data.get('title', 'N/A')}
• Company: {job_data.get('company', 'N/A')}
• Location: {job_data.get('location', 'N/A')}
• Current Status: {status.title()}
• Relevance Score: {job_data.get('relevance_score', 'N/A')}%

🎯 Action Required:
{status_info['action']}

📧 Email Template:
{status_info['template']}

💡 Best Practices:
{status_info['tips']}

📝 Your Notes:
{job_data.get('notes', 'No notes available')}

🔗 Job Link: {job_data.get('link', 'N/A')}

---
Generated by AI Job Hunter for {self.user_name}
"""
    
    def _parse_deadline(self, deadline_str: str) -> Optional[datetime.datetime]:
        """Parse deadline string into datetime object."""
        if not deadline_str or deadline_str == 'N/A':
            return None
        
        try:
            # Try common date formats
            formats = [
                '%Y-%m-%d',
                '%m/%d/%Y',
                '%d/%m/%Y',
                '%B %d, %Y',
                '%b %d, %Y',
                '%d %B %Y',
                '%d %b %Y'
            ]
            
            for fmt in formats:
                try:
                    return datetime.datetime.strptime(deadline_str.strip(), fmt)
                except ValueError:
                    continue
            
            # If no format matches, try to extract date from text
            import re
            date_match = re.search(r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})', deadline_str)
            if date_match:
                month, day, year = date_match.groups()
                return datetime.datetime(int(year), int(month), int(day))
            
            logger.warning(f"Could not parse deadline: {deadline_str}")
            return None
            
        except Exception as e:
            logger.error(f"Error parsing deadline '{deadline_str}': {e}")
            return None
    
    def _calculate_followup_date(self, status: str) -> Optional[datetime.datetime]:
        """Calculate appropriate follow-up date based on status."""
        now = datetime.datetime.now()
        
        followup_delays = {
            'applied': 14,    # 2 weeks after application
            'interview': 1,   # 1 day after interview (thank you note)
            'offered': 3,     # 3 days to respond to offer
            'rejected': 30,   # 1 month later for feedback/networking
        }
        
        days = followup_delays.get(status)
        if days is None:
            return None
        
        followup_date = now + datetime.timedelta(days=days)
        
        # Skip weekends for follow-ups
        while followup_date.weekday() > 4:  # 0-4 is Mon-Fri
            followup_date += datetime.timedelta(days=1)
        
        return followup_date


class SmartEmailer:
    """Enhanced email system with better formatting and attachments using Gmail API."""
    def __init__(self):
        self.gmail_service = self.authenticate_gmail()

    def authenticate_gmail(self):
        creds = None
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        
        # Check if we have the required scopes
        if creds and creds.valid:
            # Verify we have both Gmail and Calendar scopes
            if not all(scope in (creds.scopes or []) for scope in SCOPES):
                logger.info("Token missing required scopes. Re-authenticating...")
                creds = None
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    # FIX: Use google.auth.transport.requests.Request() for token refresh
                    creds.refresh(Request())
                except Exception as e:
                    logger.warning(f"Failed to refresh token, re-authenticating: {e}")
                    creds = None
            
            if not creds:
                try:
                    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                    creds = flow.run_local_server(port=0)
                except Exception as e:
                    logger.critical(f"Failed to authenticate with Google APIs: {e}")
                    return None
        
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        
        return build('gmail', 'v1', credentials=creds)

    def create_excel_report(self, jobs: List[Job]) -> str:
        from openpyxl.styles import Font, PatternFill, Alignment, Border, Side, GradientFill
        from openpyxl.utils import get_column_letter
        filename = f"jobs_report_{datetime.date.today().strftime('%Y%m%d')}.xlsx"
        job_data = [job.to_dict() for job in jobs]
        # Remove 'id' and 'source' columns if present and add row number
        df = pd.DataFrame(job_data)
        if 'id' in df.columns:
            df = df.drop(columns=['id'])
        if 'source' in df.columns:
            df = df.drop(columns=['source'])
        df.insert(0, 'No.', range(1, len(df) + 1))
        try:
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Jobs', index=False)
                workbook = writer.book
                worksheet = writer.sheets['Jobs']
                # --- Add Title Row ---
                title = f"Job Report – {datetime.date.today().strftime('%B %d, %Y')} (Total: {len(jobs)})"
                worksheet.insert_rows(1)
                worksheet.merge_cells(start_row=1, start_column=1, end_row=1, end_column=worksheet.max_column)
                title_cell = worksheet.cell(row=1, column=1)
                title_cell.value = title
                title_cell.font = Font(size=16, bold=True, color="FFFFFF")
                title_cell.fill = GradientFill(stop=("4F81BD", "1E90FF"))
                title_cell.alignment = Alignment(horizontal="center", vertical="center")
                # --- Header Styling ---
                header_font = Font(bold=True, color="FFFFFF")
                header_fill = GradientFill(stop=("4F81BD", "1E90FF"))
                for cell in worksheet[2]:
                    cell.font = header_font
                    cell.fill = header_fill
                    cell.alignment = Alignment(horizontal="center", vertical="center")
                worksheet.freeze_panes = worksheet['A3']
                # --- Column Widths and Alternating Row Colors ---
                for i, column in enumerate(worksheet.columns, 1):
                    max_length = max((len(str(cell.value)) if cell.value else 0) for cell in column)
                    worksheet.column_dimensions[get_column_letter(i)].width = min(max_length + 4, 50)
                alt_fill = PatternFill("solid", fgColor="F2F2F2")
                for row in worksheet.iter_rows(min_row=3, max_row=worksheet.max_row):
                    if (row[0].row % 2) == 1:
                        for cell in row:
                            cell.fill = alt_fill
                # --- Borders for all cells ---
                thin = Side(border_style="thin", color="CCCCCC")
                for row in worksheet.iter_rows(min_row=1, max_row=worksheet.max_row, min_col=1, max_col=worksheet.max_column):
                    for cell in row:
                        cell.border = Border(top=thin, left=thin, right=thin, bottom=thin)
                # --- Highlight High/Medium/Low Relevance ---
                rel_col = None
                for idx, cell in enumerate(worksheet[2], 1):
                    if cell.value and 'relevance' in str(cell.value).lower():
                        rel_col = idx
                        break
                if rel_col:
                    for row in worksheet.iter_rows(min_row=3, max_row=worksheet.max_row):
                        try:
                            val = float(row[rel_col-1].value)
                            if val >= 60:
                                for cell in row:
                                    cell.font = Font(bold=True)
                                    cell.fill = PatternFill("solid", fgColor="C6EFCE")
                                row[rel_col-1].value = f"🟢 {val}"
                            elif val >= 30:
                                row[rel_col-1].fill = PatternFill("solid", fgColor="FFF2CC")
                                row[rel_col-1].value = f"🟡 {val}"
                            else:
                                row[rel_col-1].fill = PatternFill("solid", fgColor="F8CBAD")
                                row[rel_col-1].value = f"🔴 {val}"
                        except:
                            continue
                # --- Make Links Clickable and Button Style ---
                link_col = None
                for idx, cell in enumerate(worksheet[2], 1):
                    if cell.value and 'link' in str(cell.value).lower():
                        link_col = idx
                        break
                if link_col:
                    for row in worksheet.iter_rows(min_row=3, max_row=worksheet.max_row):
                        cell = row[link_col-1]
                        if cell.value and cell.value.startswith('http'):
                            cell.hyperlink = cell.value
                            cell.value = 'Apply Now →'
                            cell.font = Font(bold=True, color="1565C0")
                            cell.fill = PatternFill("solid", fgColor="E3F2FD")
                            cell.alignment = Alignment(horizontal="center")
                # --- Highlight Salary Column ---
                salary_col = None
                for idx, cell in enumerate(worksheet[2], 1):
                    if cell.value and 'salary' in str(cell.value).lower():
                        salary_col = idx
                        break
                if salary_col:
                    for row in worksheet.iter_rows(min_row=3, max_row=worksheet.max_row):
                        cell = row[salary_col-1]
                        cell.fill = PatternFill("solid", fgColor="FFF2CC")
                # --- Improve Header Names ---
                header_map = {
                    'title': 'Job Title',
                    'company': 'Company',
                    'location': 'Location',
                    'salary': 'Salary / Stipend',
                    'link': 'Job Link',
                    'description': 'Description',
                    'keywords': 'Keywords',
                    'skills': 'Skills',
                    'experience': 'Experience',
                    'job_type': 'Job Type',
                    'posted_date': 'Posted Date',
                    'relevance_score': 'Relevance Score',
                    'min_experience_years': 'Min Exp (yrs)',
                    'max_experience_years': 'Max Exp (yrs)',
                    'extracted_tools': 'Tools',
                    'extracted_soft_skills': 'Soft Skills',
                    'user_feedback': 'User Feedback',
                }
                for idx, cell in enumerate(worksheet[2], 1):
                    if cell.value in header_map:
                        cell.value = header_map[cell.value]
                # --- Add Footer Row ---
                footer_row = worksheet.max_row + 1
                worksheet.merge_cells(start_row=footer_row, start_column=1, end_row=footer_row, end_column=worksheet.max_column)
                footer_cell = worksheet.cell(row=footer_row, column=1)
                footer_cell.value = f"End of Report – {datetime.date.today().strftime('%B %d, %Y')}"
                footer_cell.font = Font(italic=True, color="888888")
                footer_cell.alignment = Alignment(horizontal="center")
            logger.info(f"Excel report created: {filename}.")
            return filename
        except Exception as e:
            logger.error(f"Error creating Excel report: {e}")
            return ""

    def build_smart_html_email(self, jobs: List[Job]) -> str:
        if not jobs:
            logger.info("No jobs to include in the email report. Sending 'no jobs' email.")
            return """
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
                    .container { max-width: 600px; margin: 0 auto; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }
                    .header { background: linear-gradient(45deg, #FF6B6B, #4ECDC4); color: white; padding: 30px; text-align: center; }
                    .content { padding: 30px; text-align: center; }
                    .emoji { font-size: 48px; margin-bottom: 20px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🔍 Daily Job Hunt Report</h1>
                        <p>No matches found today</p>
                    </div>
                    <div class="content">
                        <div class="emoji">😴</div>
                        <h2>No new jobs found matching your criteria today</h2>
                        <p>Don't worry! The job hunter is still running and will continue searching for opportunities that match your profile.</p>
                    </div>
                </div>
            </body>
            </html>
            """
        
        total_jobs = len(jobs)
        avg_relevance = sum(job.relevance_score for job in jobs) / len(jobs) if jobs else 0
        high_relevance_jobs = [job for job in jobs if job.relevance_score >= 60]
        
        company_counts = Counter(job.company for job in jobs)
        salary_jobs = [job for job in jobs if job.salary != 'N/A']
        remote_jobs = [job for job in jobs if 'remote' in job.location.lower() or 'remote' in job.job_type.lower()]
        source_counts = Counter(job.source for job in jobs)
        skill_counts = Counter(s for job in jobs for s in job.skills)
        experience_levels = Counter()
        for job in jobs:
            exp_key = job.experience.lower()
            if 'fresher' in exp_key or 'entry' in exp_key:
                experience_levels['Entry Level'] += 1
            elif 'senior' in exp_key or 'lead' in exp_key or 'manager' in exp_key:
                experience_levels['Senior Level'] += 1
            else:
                experience_levels['Mid Level'] += 1

        top_companies = sorted(company_counts.items(), key=lambda x: x[1], reverse=True)[:6]
        top_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:8]
        top_sources = sorted(source_counts.items(), key=lambda x: x[1], reverse=True)
        top_jobs = sorted(jobs, key=lambda x: x.relevance_score, reverse=True)[:10]

        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Daily Job Intelligence Report</title>
            <style>
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                body {{ 
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; 
                    line-height: 1.6; 
                    color: #2c3e50; 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    padding: 20px;
                }}
                .email-container {{ 
                    max-width: 800px; 
                    margin: 0 auto; 
                    background: #ffffff; 
                    border-radius: 16px; 
                    overflow: hidden; 
                    box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                }}
                .header {{ 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white; 
                    text-align: center; 
                    padding: 40px 20px; 
                    position: relative;
                    overflow: hidden;
                }}
                .header::before {{
                    content: '';
                    position: absolute;
                    top: -50%;
                    left: -50%;
                    width: 200%;
                    height: 200%;
                    background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="50" cy="50" r="2" fill="rgba(255,255,255,0.1)"/></svg>') repeat;
                    animation: float 20s infinite linear;
                }}
                @keyframes float {{ from {{ transform: translateX(-50px) translateY(-50px); }} to {{ transform: translateX(50px) translateY(50px); }} }}
                .header h1 {{ font-size: 2.5rem; margin-bottom: 10px; position: relative; z-index: 1; }}
                .header p {{ font-size: 1.1rem; opacity: 0.9; position: relative; z-index: 1; }}
                
                .summary-stats {{ 
                    display: grid; 
                    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); 
                    gap: 20px; 
                    padding: 30px; 
                    background: #f8f9fa;
                }}
                .stat-card {{ 
                    background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
                    border-radius: 12px; 
                    padding: 20px; 
                    text-align: center; 
                    border: 1px solid rgba(0,0,0,0.05);
                    transition: transform 0.2s ease, box-shadow 0.2s ease;
                    position: relative;
                    overflow: hidden;
                }}
                .stat-card::before {{
                    content: '';
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    height: 3px;
                    background: linear-gradient(90deg, #667eea, #764ba2, #f093fb);
                }}
                .stat-card:hover {{ transform: translateY(-2px); box-shadow: 0 10px 25px rgba(0,0,0,0.1); }}
                .stat-number {{ 
                    font-size: 2rem; 
                    font-weight: 700; 
                    background: linear-gradient(135deg, #667eea, #764ba2);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    background-clip: text;
                    margin-bottom: 5px;
                }}
                .stat-label {{ font-size: 0.9rem; color: #6c757d; font-weight: 500; }}
                
                .content-section {{ padding: 30px; }}
                .insights {{ margin-bottom: 30px; }}
                .insights h2 {{ 
                    font-size: 1.8rem; 
                    margin-bottom: 20px; 
                    color: #2c3e50;
                    display: flex;
                    align-items: center;
                    gap: 10px;
                }}
                .insights h3 {{ 
                    font-size: 1.2rem; 
                    margin: 20px 0 10px 0; 
                    color: #495057;
                    display: flex;
                    align-items: center;
                    gap: 8px;
                }}
                
                .tag-container {{ 
                    display: flex; 
                    flex-wrap: wrap; 
                    gap: 8px; 
                    margin-bottom: 20px; 
                }}
                .tag {{ 
                    background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
                    color: #1565c0;
                    padding: 6px 14px; 
                    border-radius: 20px; 
                    font-size: 0.85rem; 
                    font-weight: 500; 
                    border: 1px solid rgba(21, 101, 192, 0.2);
                    transition: all 0.2s ease;
                }}
                .tag:hover {{ 
                    background: linear-gradient(135deg, #bbdefb 0%, #90caf9 100%);
                    transform: translateY(-1px);
                }}
                
                .jobs-section h2 {{ 
                    font-size: 1.8rem; 
                    margin-bottom: 25px; 
                    color: #2c3e50;
                    display: flex;
                    align-items: center;
                    gap: 10px;
                }}
                .job-card {{ 
                    background: #ffffff;
                    border: 1px solid #e9ecef;
                    border-radius: 12px; 
                    padding: 25px; 
                    margin-bottom: 20px; 
                    transition: all 0.3s ease;
                    position: relative;
                    overflow: hidden;
                }}
                .job-card::before {{
                    content: '';
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    height: 4px;
                    background: linear-gradient(90deg, #667eea, #764ba2);
                    transform: scaleX(0);
                    transition: transform 0.3s ease;
                }}
                .job-card:hover {{ 
                    box-shadow: 0 10px 30px rgba(102, 126, 234, 0.15);
                    transform: translateY(-2px);
                    border-color: #667eea;
                }}
                .job-card:hover::before {{ transform: scaleX(1); }}
                
                .job-title {{ 
                    font-size: 1.3rem; 
                    font-weight: 600; 
                    margin-bottom: 8px;
                }}
                .job-title a {{ 
                    color: #667eea; 
                    text-decoration: none; 
                    transition: color 0.2s ease;
                }}
                .job-title a:hover {{ color: #764ba2; }}
                
                .job-company {{ 
                    font-weight: 600; 
                    color: #495057; 
                    font-size: 1.1rem; 
                    margin-bottom: 12px;
                }}
                .job-meta {{ 
                    display: flex; 
                    flex-wrap: wrap; 
                    gap: 15px; 
                    margin: 12px 0; 
                    font-size: 0.9rem; 
                    color: #6c757d; 
                }}
                .job-meta-item {{ 
                    display: flex; 
                    align-items: center; 
                    gap: 5px;
                    background: #f8f9fa;
                    padding: 4px 10px;
                    border-radius: 15px;
                    font-weight: 500;
                }}
                .job-description {{ 
                    font-size: 0.95rem; 
                    margin: 15px 0; 
                    color: #495057; 
                    line-height: 1.6;
                    background: #f8f9fa;
                    padding: 15px;
                    border-radius: 8px;
                    border-left: 4px solid #667eea;
                }}
                
                .btn {{ 
                    display: inline-block; 
                    padding: 12px 24px; 
                background: linear-gradient(135deg, #134e5e 0%, #71b280 50%, #a8e6cf 100%);
                    color: white; 
                    text-decoration: none; 
                    border-radius: 25px; 
                    font-size: 0.9rem; 
                    font-weight: 600;
                    margin-top: 15px; 
                    transition: all 0.3s ease;
                    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
                }}
                .btn:hover {{ 
                    transform: translateY(-2px);
                    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
                    text-decoration: none;
                    color: white;
                }}
                
                .footer {{ 
                    background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
                    color: white;
                    text-align: center; 
                    padding: 30px 20px; 
                    margin-top: 20px; 
                }}
                .footer h3 {{ margin-bottom: 15px; font-size: 1.3rem; }}
                .footer p {{ margin: 8px 0; opacity: 0.9; }}
                
                .relevance-badge {{
                    position: absolute;
                    top: 15px;
                    right: 15px;
                    background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
                    color: white;
                    padding: 5px 12px;
                    border-radius: 15px;
                    font-size: 0.8rem;
                    font-weight: 600;
                }}
                
                @media (max-width: 600px) {{
                    .email-container {{ margin: 10px; border-radius: 12px; }}
                    .header h1 {{ font-size: 2rem; }}
                    .summary-stats {{ grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 15px; padding: 20px; }}
                    .content-section {{ padding: 20px; }}
                    .job-card {{ padding: 20px; }}
                    .job-meta {{ flex-direction: column; gap: 8px; }}
                    .job-meta-item {{ align-self: flex-start; }}
                }}
            </style>
        </head>
        <body>
            <div class="email-container">
                <div class="header">
                    <h1>🧠 Daily Job Intelligence Report</h1>
                    <p>{datetime.date.today().strftime('%B %d, %Y')}</p>
                </div>
                
                <div class="summary-stats">
                    <div class="stat-card">
                        <div class="stat-number">{total_jobs}</div>
                        <div class="stat-label">New Jobs</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{len(high_relevance_jobs)}</div>
                        <div class="stat-label">High Relevance</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{avg_relevance:.0f}%</div>
                        <div class="stat-label">Avg Relevance</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{len(salary_jobs)}</div>
                        <div class="stat-label">With Salary</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{len(remote_jobs)}</div>
                        <div class="stat-label">Remote</div>
                    </div>
                </div>
                
                <div class="content-section">
                    <div class="insights">
                        <h2>📊 Market Insights</h2>
                        
                        <h3>🏢 Top Hiring Companies</h3>
                        <div class="tag-container">
                            {' '.join(f'<span class="tag">{c} ({n})</span>' for c, n in top_companies)}
                        </div>
                        
                        <h3>🛠️ In-Demand Skills</h3>
                        <div class="tag-container">
                            {' '.join(f'<span class="tag">{s} ({n})</span>' for s, n in top_skills)}
                        </div>
                        
                        <h3>📱 Job Sources</h3>
                        <div class="tag-container">
                            {' '.join(f'<span class="tag">{src} ({cnt})</span>' for src, cnt in top_sources)}
                        </div>
                        
                        <h3>👨‍💼 Experience Levels</h3>
                        <div class="tag-container">
                            {' '.join(f'<span class="tag">{lvl} ({cnt})</span>' for lvl, cnt in experience_levels.items())}
                        </div>
                    </div>
                    
                    <div class="jobs-section">
                        <h2>🎯 Top Job Matches</h2>
                        {''.join(f'''
<div class="job-card">
    <div class="relevance-badge">{job.relevance_score:.0f}% Match</div>
    <div class="job-title">
        {f'<a href="{job.link}" target="_blank">{job.title}</a>' if job.title and job.title != 'N/A' and job.link and job.link != 'N/A' else (job.title if job.title and job.title != 'N/A' else '')}
    </div>
    <div class="job-company">{job.company}</div>
    <div class="job-meta">
        {f'<span class="job-meta-item">📍 {job.location}</span>' if job.location and job.location != 'N/A' else ''}
        {f'<span class="job-meta-item">💰 {job.salary}</span>' if job.salary and job.salary != 'N/A' else ''}
        {f'<span class="job-meta-item">👨‍💼 {job.experience}</span>' if job.experience and job.experience != 'N/A' else ''}
        {f'<span class="job-meta-item">🔗 {job.source}</span>' if job.source and job.source != 'N/A' else ''}
        {f'<span class="job-meta-item">📅 {job.posted_date}</span>' if job.posted_date and job.posted_date != 'N/A' else ''}
    </div>
    <div class="job-description">
        {job.description[:300]}{"..." if len(job.description) > 300 else ""}
    </div>
    {f'''<div class="tag-container">
        {' '.join(f'<span class="tag">{s}</span>' for s in (job.skills + job.extracted_tools)[:6])}
    </div>''' if job.skills or job.extracted_tools else ''}
    <a href="{job.link}" class="btn" target="_blank">Apply Now →</a>
</div>
''' for job in top_jobs)}
                    </div>
                </div>
                
                <div class="footer">
                    <h3>🤖 AI-Powered Job Intelligence</h3>
                    <p>Scanned <strong>{total_jobs}</strong> jobs from <strong>{len(top_sources)}</strong> sources</p>
                    <p>Next scan: {(datetime.datetime.now() + datetime.timedelta(hours=12)).strftime('%I:%M %p')}</p>
                    <p style="margin-top: 20px; font-size: 0.9rem; opacity: 0.8;">
                        Built with ❤️ by your Super Job Agent
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        return html

    def send_email(self, subject: str, html_content: str, attachment_path: Optional[str] = None, recipients: List[str] = None):
        """Sends an email with HTML content and an optional attachment using Gmail API."""
        if recipients is None:
            recipients = [ADMIN_ALERT_EMAIL] # Default to admin if no recipients specified

        if not self.gmail_service:
            logger.critical("Email not sent: Gmail service not authenticated.")
            return

        message = MIMEMultipart()
        message['to'] = ', '.join(recipients)
        message['subject'] = subject
        message.attach(MIMEText(html_content, 'html'))
        
        if attachment_path and os.path.exists(attachment_path):
            try:
                with open(attachment_path, 'rb') as f:
                    mime_base = MIMEBase('application', 'octet-stream')
                    mime_base.set_payload(f.read())
                    encoders.encode_base64(mime_base)
                    mime_base.add_header('Content-Disposition', f'attachment; filename="{os.path.basename(attachment_path)}"')
                    message.attach(mime_base)
                logger.info(f"Attached file: {os.path.basename(attachment_path)} to email.")
            except Exception as e:
                logger.error(f"Error attaching file {attachment_path}: {e}")
        
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        try:
            self.gmail_service.users().messages().send(userId='me', body={'raw': raw}).execute()
            logger.info(f"📧 Email sent successfully to {recipients}!")
        except Exception as e:
            logger.error(f"Error sending email to {recipients}: {e}")

class JobHunter:
    """Main class to run the job alert system."""
    def __init__(self, user_id: int, search_terms: List[str], location: str, experience: str = "", job_type: str = "", task=None):
        self.user_id = user_id
        self.search_terms = search_terms
        self.location = location
        self.experience = experience
        self.job_type = job_type
        self.task = task
        self.db = JobDatabase()
        self.scraper = EnhancedJobScraper(search_terms=self.search_terms, location=self.location, experience=self.experience, job_type=self.job_type, user_id=self.user_id, task=self.task)
        self.emailer = SmartEmailer()
        
    def run(self):
        """Orchestrates the entire job search and alert process."""
        logger.info(f"🔍 Starting job hunt for user {self.user_id} with terms: {self.search_terms}, location: {self.location}")
        if self.task:
            self.task.update_state(state='PROGRESS', meta={'status': 'Starting job hunt...', 'progress': 5})

        logger.info("Calling scraper.scrape_all_sources()...")
        jobs = self.scraper.scrape_all_sources()
        logger.info(f"Scraper returned {len(jobs)} jobs.")
        
        if self.task:
            self.task.update_state(state='PROGRESS', meta={'status': f'Scraping complete. Found {len(jobs)} potential jobs. Saving to database...', 'progress': 90})

        # Store new jobs in the database for the specific user
        new_jobs_count = 0
        for job in jobs:
            if self.db.add_job(job, self.user_id):
                new_jobs_count += 1
        logger.info(f"💾 Added {new_jobs_count} new jobs to the database for user {self.user_id}.")

        # Retrieve user settings for email
        user_settings = self.db.get_user_settings(self.user_id)
        email_recipients = user_settings.get('email_recipients') if user_settings else ADMIN_ALERT_EMAIL
        send_excel_attachment = user_settings.get('send_excel_attachment') if user_settings else True

        if not jobs:
            logger.info(f"📊 Found 0 new jobs matching criteria for user {self.user_id} today. No email will be sent.")
            # Optionally send a "no jobs found" email
            # html = self.emailer.build_smart_html_email([])
            # self.emailer.send_email(f"No New Job Matches - {datetime.date.today().strftime('%b %d, %Y')}", html)
            return
            
        if self.task:
            self.task.update_state(state='PROGRESS', meta={'status': 'Generating email report...', 'progress': 95})

        html = self.emailer.build_smart_html_email(jobs)
        excel_file = ""
        if send_excel_attachment:
            excel_file = self.emailer.create_excel_report(jobs)
        
        subject = f"🧠 {len(jobs)} New Job Matches – {datetime.date.today().strftime('%b %d, %Y')}"
        
        # Pass the recipients list directly
        self.emailer.send_email(subject, html, attachment_path=excel_file, recipients=email_recipients.split(','))
        
        if os.path.exists(excel_file):
            os.remove(excel_file)
            logger.info(f"Cleaned up Excel report: {excel_file}.")

        logger.info(f"🤖 Super Job Agent finished its run for user {self.user_id}.")

# --- Celery Tasks ---
@celery.task(bind=True, name='app.run_job_hunt_task')
def run_job_hunt_task(self, user_id: int, search_terms: List[str], location: str, experience: str, job_type: str):
    """Celery task to run the job hunt for a specific user and search profile."""
    logger.info(f"Celery task {self.request.id} started for user {user_id} with terms {search_terms} at {location}.")
    try:
        logger.info(f"Creating JobHunter instance for user {user_id}.")
        hunter = JobHunter(user_id=user_id, search_terms=search_terms, location=location, experience=experience, job_type=job_type, task=self)
        logger.info(f"Running JobHunter.run() for user {user_id}.")
        hunter.run()
        logger.info(f"Celery task {self.request.id} completed successfully for user {user_id}.")
        return {'status': 'Complete! Your dashboard will now reload.', 'progress': 100}
    except Exception as e:
        logger.error(f"Celery task {self.request.id} failed for user {user_id}: {e}", exc_info=True)
        self.update_state(state='FAILURE', meta={'status': 'Task failed!', 'error': str(e), 'progress': 100})
        # Consider sending an admin alert email here
        # SmartEmailer().send_email("CRITICAL: Job Hunt Task Failed", f"Task for user {user_id} failed with error: {traceback.format_exc()}", recipients=[ADMIN_ALERT_EMAIL])
        raise

# In app.py
@celery.task(name='app.assisted_apply_task')
def assisted_apply_task(user_id: int, job_id: int):
    """
    Launches a NON-headless browser and uses ApplicationFiller to pre-fill a job application.
    Uses a pre-existing browser profile if configured by the user, to maintain login sessions.
    """
    db = JobDatabase()
    conn = sqlite3.connect(db.db_path)
    conn.row_factory = sqlite3.Row # Use row_factory for dict-like access
    cursor = conn.cursor()

    # 1. Fetch user_details and job_link from DB
    cursor.execute("SELECT * FROM user_details WHERE user_id = ?", (user_id,))
    user_details_raw = cursor.fetchone()

    if not user_details_raw:
        logger.error(f"[AssistApply] No user_details found for user_id {user_id}. Aborting. Please add your details to the database.")
        conn.close()
        return {'status': 'error', 'message': 'User details not found in database.'}

    user_details = dict(user_details_raw)

    # Load parsed resume data from the JSON string in the database
    try:
        user_details['parsed_resume'] = json.loads(user_details.get('resume_parsed_data', '{}') or '{}')
    except (json.JSONDecodeError, TypeError):
        user_details['parsed_resume'] = {}
        logger.warning(f"[AssistApply] Could not load/parse resume data for user {user_id}. Answering will be limited.")

    # Remap DB keys to what the ApplicationFiller bot expects
    if user_details.get('linkedin_url'):
        user_details['linkedin'] = user_details['linkedin_url']
    if user_details.get('resume_path'):
        # Ensure the path is absolute for the Celery worker
        user_details['resume'] = os.path.abspath(user_details['resume_path'])
    if user_details.get('cover_letter_template'):
        user_details['cover_letter'] = user_details['cover_letter_template']

    # Add first/last name for compatibility with the filler bot
    full_name = user_details.get('full_name', '')
    if full_name:
        name_parts = full_name.split(' ')
        user_details['first_name'] = name_parts[0]
        user_details['last_name'] = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''

    cursor.execute("SELECT link FROM jobs WHERE id = ? AND user_id = ?", (job_id, user_id))
    job_link_raw = cursor.fetchone()
    conn.close()

    if not job_link_raw or not job_link_raw['link']:
        logger.error(f"[AssistApply] No job link found for job_id {job_id}. Aborting.")
        return {'status': 'error', 'message': 'Job link not found.'}

    job_link = job_link_raw['link']
    logger.info(f"[AssistApply] Starting for user {user_id} on job {job_id} -> {job_link}")

    # 2. Launch a NON-headless Selenium browser
    driver = None
    try:
        options = EdgeOptions()
        options.use_chromium = True
        options.add_argument("--start-maximized")
        options.add_experimental_option("detach", True) # This is key to keeping the browser open

        # Explicitly set the browser binary location to improve robustness.
        edge_binary_paths = [
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
        ]
        for path in edge_binary_paths:
            if os.path.exists(path):
                options.binary_location = path
                logger.info(f"[AssistApply] Setting Edge binary location to: {path}")
                break

        browser_profile_path_input = user_details.get('browser_profile_path', '').strip()
        if browser_profile_path_input:
            # NEW CHECK: If user provided path to executable, log a clear error and fallback.
            if browser_profile_path_input.lower().endswith('.exe'):
                logger.error(f"[AssistApply] CONFIGURATION ERROR: The Browser Profile Path is set to an executable file ('{browser_profile_path_input}'). It should be a directory path ending in 'User Data'. Please correct this in your profile. Falling back to a temporary profile.")
                browser_profile_path_input = '' # Clear the invalid path to proceed with fallback

        if browser_profile_path_input:
            # The user_data_dir should be the parent of the profile folder (e.g., 'Default', 'Profile 1')
            # We'll try to auto-correct if the user provides the full path to the profile sub-directory.
            user_data_dir = browser_profile_path_input
            profile_directory = "Default"

            path_basename = os.path.basename(user_data_dir)
            if path_basename.lower() == 'default' or path_basename.lower().startswith('profile '):
                profile_directory = path_basename
                user_data_dir = os.path.dirname(user_data_dir)
                logger.info(f"[AssistApply] User-provided path seems to be a full profile path. Auto-adjusting to User Data Dir: '{user_data_dir}' and Profile: '{profile_directory}'")

            if os.path.isdir(user_data_dir):
                # NEW: Check for a lock file, which indicates the browser is likely running.
                lock_file_path = os.path.join(user_data_dir, 'SingletonLock')
                if os.path.exists(lock_file_path):
                    logger.warning(f"[AssistApply] WARNING: A lock file was found at '{lock_file_path}'. This strongly indicates that Edge is already running with this profile. Please close all Edge windows and processes (check Task Manager for 'msedge.exe') before trying again.")

                logger.info(f"[AssistApply] Using browser session from User Data Dir: '{user_data_dir}' with Profile: '{profile_directory}'")
                options.add_argument(f"user-data-dir={user_data_dir}")
                options.add_argument(f"profile-directory={profile_directory}")
            else:
                logger.warning(f"[AssistApply] The derived User Data Directory '{user_data_dir}' (from your input '{browser_profile_path_input}') is not a valid directory. Falling back to a new temporary profile. Please check your profile settings.")
        else:
            logger.info("[AssistApply] No browser profile path configured in your profile. Starting with a new temporary profile. You may need to log in to job sites.")

        driver_path = os.environ.get('EDGE_DRIVER_PATH', DRIVER_PATHS.get('edge'))
        if not driver_path or not os.path.exists(driver_path):
            raise FileNotFoundError("Edge WebDriver executable not found on the worker machine. Please check the server configuration (EDGE_DRIVER_PATH).")

        service = EdgeService(executable_path=driver_path)
        logger.info("[AssistApply] Attempting to initialize Edge WebDriver...")
        time.sleep(1) # A small delay can sometimes help prevent race conditions
        driver = webdriver.Edge(service=service, options=options)
        
        filler = ApplicationFiller(driver, user_details)
        filler.fill(job_link)
        logger.info(f"[AssistApply] Form filling process initiated for {job_link}. The browser window is now open for your review and final submission.")
    except FileNotFoundError as e:
        logger.critical(f"[AssistApply] CONFIGURATION ERROR: {e}", exc_info=True)
        if driver: driver.quit()
    except SeleniumWebDriverException as e:
        if "session not created" in str(e).lower():
            logger.error(f"[AssistApply] CRITICAL ERROR: Could not create browser session. This often happens if the browser is already running with the same user profile. Please close all Edge windows and try again.", exc_info=False)
            logger.debug(f"Full SessionNotCreatedException: {e}") # Log the full trace for debugging if needed
        else:
            logger.error(f"[AssistApply] A browser automation error occurred. This might be due to a driver/browser version mismatch or a browser crash.", exc_info=True)
        if driver: driver.quit()
    except Exception as e:
        logger.error(f"An error occurred during assisted_apply_task for job {job_id}: {e}", exc_info=True)
        if driver: driver.quit() # Close browser on error


@celery.task(name='app.scheduled_job_hunt_for_all_users')
def scheduled_job_hunt_for_all_users():
    db = JobDatabase()
    conn = sqlite3.connect(db.db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username FROM users")
    users = cursor.fetchall()
    conn.close()

    for user_id, username in users:
        profiles = db.get_search_profiles(user_id)
        if not profiles:
            logger.info(f"User {username} (ID: {user_id}) has no saved search profiles. Skipping scheduled hunt.")
            continue

        for profile in profiles:
            search_terms = [term.strip() for term in profile['search_terms'].split(',') if term.strip()]
            location = profile['location']
            experience = profile['experience']
            job_type = profile['job_type']
            
            logger.info(f"Scheduling job hunt for user {username} (ID: {user_id}) with profile '{profile['profile_name']}'.")
            # Directly call the task, as this is now a Celery Beat scheduled task
            run_job_hunt_task.delay(user_id, search_terms, location, experience, job_type)


# --- Flask Routes ---
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password_hash = generate_password_hash(password)
        db = JobDatabase()
        user_id = db.add_user(username, password_hash)
        if user_id:
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Username already exists. Please choose a different one.', 'danger')
    return render_template('register.html', now=datetime.datetime.now())

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db_user = User.get_by_username(username)
        if db_user and check_password_hash(db_user.password_hash, password):
            login_user(db_user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', now=datetime.datetime.now())

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    db = JobDatabase()
    if request.method == 'POST':
        # Get existing details to not lose the resume path if not updated
        existing_details = db.get_user_details(current_user.id) or {}
        
        details = {
            'full_name': request.form.get('full_name'),
            'email': request.form.get('email'),
            'phone': request.form.get('phone'),
            'address': request.form.get('address'),
            'linkedin_url': request.form.get('linkedin_url'),
            'github_url': request.form.get('github_url'),
            'portfolio_url': request.form.get('portfolio_url'),
            'cover_letter_template': request.form.get('cover_letter_template'),
            'resume_path': existing_details.get('resume_path'),
            'browser_profile_path': request.form.get('browser_profile_path', '').strip(),
            'willing_to_relocate': request.form.get('willing_to_relocate', 'no'),
            'authorized_to_work': request.form.get('authorized_to_work', 'no')
        }

        # Handle resume file upload
        if 'resume' in request.files:
            file = request.files['resume']
            if file and file.filename != '':
                # Save to a user-specific subfolder to avoid name collisions
                user_upload_dir = os.path.join(app.config['UPLOAD_FOLDER'], str(current_user.id))
                os.makedirs(user_upload_dir, exist_ok=True)
                filename = secure_filename(file.filename)
                file_path = os.path.join(user_upload_dir, filename)
                file.save(file_path)
                details['resume_path'] = file_path

                # NEW: Parse the resume and store the structured data as JSON
                parser = ResumeParser()
                parsed_data = parser.parse(file_path)
                details['resume_parsed_data'] = json.dumps(parsed_data) if parsed_data else None
            else: # No new file uploaded, keep the old parsed data
                details['resume_parsed_data'] = existing_details.get('resume_parsed_data')
        else: # No file in request, also keep old parsed data
            details['resume_parsed_data'] = existing_details.get('resume_parsed_data')
        
        if db.save_user_details(current_user.id, details):
            flash('Profile updated successfully!', 'success')
        else:
            flash('Failed to update profile.', 'danger')
        return redirect(url_for('profile'))

    user_details = db.get_user_details(current_user.id)
    return render_template('profile.html', user_details=user_details)

@app.route('/dashboard')
@login_required
def dashboard():
    db = JobDatabase()
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)
    offset = (page - 1) * limit
    sort_by = request.args.get('sort_by', 'found_date')
    sort_order = request.args.get('sort_order', 'DESC')
    search_query = request.args.get('search_query', '')
    status_filter = request.args.get('status_filter', 'all')
    location_filter = request.args.get('location_filter', '')
    job_type_filter = request.args.get('job_type_filter', 'all')
    view_mode = 'detailed'  # Always use detailed view

    jobs, total_jobs = db.get_jobs_for_user(
        current_user.id,
        limit=limit,
        offset=offset,
        sort_by=sort_by,
        sort_order=sort_order,
        search_query=search_query,
        status_filter=status_filter,
        location_filter=location_filter,
        job_type_filter=job_type_filter
    )
    
    # Add status colors to jobs
    def add_status_colors(job):
        status_colors = {
            'new': {'bg': '#f3f4f6', 'text': '#374151'},
            'applied': {'bg': '#dcfce7', 'text': '#166534'},
            'interview': {'bg': '#e0e7ff', 'text': '#3730a3'},
            'offered': {'bg': '#fef3c7', 'text': '#92400e'},
            'rejected': {'bg': '#fee2e2', 'text': '#991b1b'},
            'withdrawn': {'bg': '#f3f4f6', 'text': '#6b7280'}
        }
        status = job.get('status', 'new')
        colors = status_colors.get(status, status_colors['new'])
        job['status_color'] = colors['bg']
        job['status_text_color'] = colors['text']
        return job
    
    jobs = [add_status_colors(job) for job in jobs]
    
    saved_profiles = db.get_search_profiles(current_user.id)
    user_settings = db.get_user_settings(current_user.id)
    
    total_pages = (total_jobs + limit - 1) // limit if limit > 0 else 1

    # Generate a window of page numbers for pagination controls
    page_window = 2  # Number of pages to show before and after the current page
    start_page = max(1, page - page_window)
    end_page = min(total_pages, page + page_window)
    if end_page < start_page: # Handle case where total_pages is very small
        end_page = start_page
    pagination_pages = range(start_page, end_page + 1)

    return render_template('dashboard.html', 
                           jobs=jobs, 
                           saved_profiles=saved_profiles,
                           user_settings=user_settings,
                           current_page=page,
                           total_pages=total_pages,
                           limit=limit,
                           pagination_pages=pagination_pages,
                           sort_by=sort_by,
                           sort_order=sort_order,
                           search_query=search_query,
                           status_filter=status_filter,
                           location_filter=location_filter,
                           job_type_filter=job_type_filter,
                           total_jobs=total_jobs,
                           view_mode=view_mode,
                           now=datetime.datetime.now())

@app.route('/search_jobs', methods=['POST'])
@login_required
def search_jobs():
    search_terms_str = request.form.get('search_terms', '')
    location = request.form.get('location', '')
    experience = request.form.get('experience', '')
    job_type = request.form.get('job_type', '')

    search_terms = [term.strip() for term in search_terms_str.split(',') if term.strip()]

    if not search_terms:
        flash('Please enter at least one search term.', 'warning')
        return redirect(url_for('dashboard'))

    # Trigger the Celery task for job scraping
    try:
        task = run_job_hunt_task.delay(current_user.id, search_terms, location, experience, job_type)
        logger.info(f"Celery task {task.id} enqueued for user {current_user.id} with terms '{search_terms_str}'.")
        return jsonify({'status': 'success', 'task_id': task.id})
    except Exception as e:
        logger.error(f"Failed to enqueue Celery task for user {current_user.id} with terms '{search_terms_str}': {e}", exc_info=True)
        return jsonify({'status': 'error', 'message': 'Failed to start search. Celery worker might be down.'}), 500

@app.route('/save_profile', methods=['POST'])
@login_required
def save_profile():
    # Handle both JSON and form data
    if request.is_json:
        data = request.get_json()
        profile_name = data.get('profile_name')
        search_terms = data.get('search_terms')
        location = data.get('location', '')
        experience = data.get('experience', '')
        job_type = data.get('job_type', '')
    else:
        profile_name = request.form['profile_name']
        search_terms = request.form['search_terms']
        location = request.form['location']
        experience = request.form.get('experience', '')
        job_type = request.form.get('job_type', '')

    if not profile_name or not search_terms:
        if request.is_json:
            return jsonify({'error': 'Profile name and search terms are required'}), 400
        flash('Profile name and search terms are required', 'danger')
        return redirect(url_for('dashboard'))

    db = JobDatabase()
    profile_id = db.save_search_profile(current_user.id, profile_name, search_terms, location, experience, job_type)
    
    if profile_id:
        if request.is_json:
            return jsonify({
                'success': True,
                'message': f"Search profile '{profile_name}' saved successfully!",
                'profile_id': profile_id
            })
        flash(f"Search profile '{profile_name}' saved successfully!", 'success')
    else:
        if request.is_json:
            return jsonify({'error': f"Failed to save profile. A profile with name '{profile_name}' might already exist."}), 400
        flash(f"Failed to save profile. A profile with name '{profile_name}' might already exist.", 'danger')
    
    return redirect(url_for('dashboard'))

@app.route('/delete_profile/<int:profile_id>', methods=['POST'])
@login_required
def delete_profile(profile_id):
    db = JobDatabase()
    if db.delete_search_profile(profile_id, current_user.id):
        flash('Search profile deleted successfully!', 'success')
    else:
        flash('Failed to delete search profile.', 'danger')
    return redirect(url_for('dashboard'))

@app.route('/apply_profile/<int:profile_id>', methods=['POST'])
@login_required
def apply_profile(profile_id):
    db = JobDatabase()
    try:
        profile = db.get_search_profile_by_id(profile_id, current_user.id)
        if not profile:
            return jsonify({'error': 'Profile not found or access denied.'}), 404
        
        # Always return JSON for apply_profile since it's used by JavaScript
        return jsonify({
            'success': True,
            'profile': {
                'profile_name': profile['profile_name'],
                'search_terms': profile['search_terms'],
                'location': profile['location'] or '',
                'experience': profile['experience'] or '',
                'job_type': profile['job_type'] or ''
            }
        })
        
        # Note: Original behavior for starting search task is now handled by the search form
    except Exception as e:
        logger.error(f"Failed to apply profile for user {current_user.id} from profile {profile_id}: {e}", exc_info=True)
        return jsonify({'error': 'Failed to apply profile.'}), 500

@app.route('/delete_job/<int:job_id>', methods=['POST'])
@login_required
def delete_job(job_id):
    db = JobDatabase()
    if db.delete_job(job_id, current_user.id):
        flash('Job deleted successfully.', 'success')
    else:
        flash('Job not found or could not be deleted.', 'error')
    return redirect(url_for('dashboard'))

@app.route('/delete_selected', methods=['POST'])
@login_required
def delete_selected():
    job_ids = request.form.getlist('job_ids')
    job_ids = [int(jid) for jid in job_ids if jid.isdigit()]
    if not job_ids:
        flash('No jobs selected for deletion.', 'warning')
        return redirect(url_for('dashboard'))
    
    db = JobDatabase()
    deleted_count = db.delete_jobs(job_ids, current_user.id)
    if deleted_count > 0:
        flash(f'Successfully deleted {deleted_count} job(s).', 'success')
    else:
        flash('No jobs were deleted. They may not exist or belong to you.', 'error')
    return redirect(url_for('dashboard'))

@app.route('/delete_all_jobs', methods=['POST'])
@login_required
def delete_all_jobs():
    db = JobDatabase()
    deleted_count = db.delete_all_jobs(current_user.id)
    if deleted_count > 0:
        flash(f'Successfully deleted all {deleted_count} jobs.', 'success')
    else:
        flash('No jobs to delete.', 'info')
    return redirect(url_for('dashboard'))

@app.route('/update_settings', methods=['POST'])
@login_required
def update_settings():
    email_recipients = request.form.get('email_recipients', '').strip()
    email_frequency = request.form.get('email_frequency', 'daily').strip()
    send_excel_attachment = 'send_excel_attachment' in request.form

    db = JobDatabase()
    if db.update_user_settings(current_user.id, email_recipients, email_frequency, send_excel_attachment):
        flash('Email settings updated successfully!', 'success')
    else:
        flash('Failed to update email settings.', 'danger')
    return redirect(url_for('dashboard'))

@app.route('/update_job_status', methods=['POST'])
@app.route('/update_job_status/<int:job_id>', methods=['POST'])
@login_required
def update_job_status(job_id=None):
    # Handle both URL parameter and form data
    if job_id is None:
        job_id = request.form.get('job_id', type=int)
    
    status = request.form.get('status')
    notes = request.form.get('notes', '')
    sync_to_calendar = request.form.get('sync_to_calendar') == '1'  # Check if checkbox is checked

    if not job_id or not status:
        if request.is_json or 'application/json' in request.headers.get('Accept', ''):
            return jsonify({'error': 'Job ID and status are required'}), 400
        flash('Job ID and status are required', 'danger')
        return redirect(url_for('dashboard'))

    db = JobDatabase()
    
    if db.update_job_status_and_notes(job_id, current_user.id, status, notes):
        success_message = 'Job status updated successfully!'
        
        # Only sync to calendar if user requested it
        if sync_to_calendar:
            # Get job details for calendar integration
            jobs, _ = db.get_jobs_for_user(current_user.id, limit=1, offset=0, 
                                           search_query=f"id:{job_id}")
            
            if jobs:
                job_data = jobs[0]
                calendar_manager = GoogleCalendarManager()
                
                try:
                    calendar_synced = False
                    
                    if status == 'interview':
                        result = calendar_manager.create_interview_event(job_data)
                        if result:
                            success_message = 'Job status updated and interview event created in calendar!'
                            calendar_synced = True
                    elif status == 'applied':
                        result = calendar_manager.create_followup_reminder(job_data, status)
                        if result:
                            success_message = 'Job status updated and follow-up reminder created!'
                            calendar_synced = True
                    elif status in ['offered', 'rejected']:
                        result = calendar_manager.create_followup_reminder(job_data, status)
                        if result:
                            success_message = f'Job status updated and {status} follow-up reminder created!'
                            calendar_synced = True
                    elif job_data.get('deadline') and job_data['deadline'] != 'N/A':
                        # Create deadline reminder for any status if deadline exists
                        result = calendar_manager.create_deadline_reminder(job_data, job_data['deadline'])
                        if result:
                            success_message = 'Job status updated and deadline reminder created!'
                            calendar_synced = True
                    
                    if not calendar_synced and sync_to_calendar:
                        success_message += ' (No calendar event needed for this status)'
                        
                except Exception as e:
                    logger.error(f"Calendar integration failed: {e}")
                    if request.is_json or 'application/json' in request.headers.get('Accept', ''):
                        return jsonify({'error': 'Job status updated, but calendar sync failed. Check your Google Calendar connection.'}), 500
                    flash('Job status updated, but calendar sync failed. Check your Google Calendar connection.', 'warning')
                    return redirect(url_for('dashboard'))
        
        # Return JSON response for AJAX requests
        if request.is_json or 'application/json' in request.headers.get('Accept', ''):
            # Get updated job data
            jobs, _ = db.get_jobs_for_user(current_user.id, limit=1, offset=0, 
                                           search_query=f"id:{job_id}")
            if jobs:
                job_data = jobs[0]
                return jsonify({
                    'success': True,
                    'message': success_message,
                    'job': {
                        'id': job_data['id'],
                        'status': job_data['status'],
                        'title': job_data['title'],
                        'company': job_data['company']
                    }
                })
            else:
                return jsonify({'error': 'Job not found after update'}), 404
        
        flash(success_message, 'success')
    else:
        if request.is_json or 'application/json' in request.headers.get('Accept', ''):
            return jsonify({'error': 'Failed to update job status'}), 500
        flash('Failed to update job status.', 'danger')
    
    return redirect(url_for('dashboard'))

@app.route('/sync_job_to_calendar/<int:job_id>', methods=['POST'])
@login_required
def sync_job_to_calendar(job_id):
    """Sync a specific job to Google Calendar."""
    try:
        db = JobDatabase()
        calendar_manager = GoogleCalendarManager()
        
        if not calendar_manager.calendar_service:
            return jsonify({'error': 'Calendar not connected'}), 400
        
        # Get job details
        jobs, _ = db.get_jobs_for_user(current_user.id, limit=1, offset=0, 
                                       search_query=f"id:{job_id}")
        
        if not jobs:
            return jsonify({'error': 'Job not found'}), 404
        
        job_data = jobs[0]
        events_created = []
        
        # Create appropriate calendar events based on job status and data
        if job_data.get('status') == 'interview':
            result = calendar_manager.create_interview_event(job_data)
            if result:
                events_created.append('Interview event')
        
        if job_data.get('status') == 'applied':
            result = calendar_manager.create_followup_reminder(job_data, 'applied')
            if result:
                events_created.append('Follow-up reminder')
        
        if job_data.get('status') in ['offered', 'rejected']:
            result = calendar_manager.create_followup_reminder(job_data, job_data['status'])
            if result:
                events_created.append(f'{job_data["status"].title()} follow-up')
        
        if job_data.get('deadline') and job_data['deadline'] != 'N/A':
            result = calendar_manager.create_deadline_reminder(job_data, job_data['deadline'])
            if result:
                events_created.append('Deadline reminder')
        
        if events_created:
            message = f'Successfully created: {", ".join(events_created)}'
            return jsonify({'success': True, 'message': message, 'events_created': events_created})
        else:
            return jsonify({'success': True, 'message': 'No calendar events needed for this job', 'events_created': []})
        
    except Exception as e:
        logger.error(f"Failed to sync job {job_id} to calendar: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/feedback', methods=['POST'])
@login_required
def feedback():
    job_id = request.form.get('job_id', type=int)
    feedback_type = request.form.get('feedback_type') # 'like' or 'dislike'
    
    db = JobDatabase()
    if db.record_job_feedback(current_user.id, job_id, feedback_type):
        flash(f"Feedback recorded: {feedback_type}!", 'success')
        # Here, you might also trigger an update to custom scores based on feedback
        # For simplicity, let's assume feedback directly updates the job entry.
    else:
        flash('Failed to record feedback.', 'danger')
    return redirect(url_for('dashboard'))

@app.route('/assisted_apply/<int:job_id>', methods=['POST'])
@login_required
def assisted_apply(job_id):
    """Triggers the assisted apply Celery task."""
    try:
        # You could add a check here to see if the user has filled out their profile
        task = assisted_apply_task.delay(current_user.id, job_id)
        logger.info(f"Enqueued assisted_apply_task {task.id} for user {current_user.id}, job {job_id}.")
        return jsonify({'status': 'success', 'message': 'Task started! A browser window should open shortly.'})
    except Exception as e:
        logger.error(f"Failed to enqueue assisted_apply_task for user {current_user.id}, job {job_id}: {e}", exc_info=True)
        return jsonify({'status': 'error', 'message': 'Failed to start task. Is the Celery worker running?'}), 500

@app.route('/api/job_status_data')
@login_required
def job_status_data():
    """API endpoint to provide job status data for charts."""
    db = JobDatabase()
    status_counts = db.get_job_status_counts(current_user.id)
    return jsonify(status_counts)

@app.route('/sync_calendar', methods=['POST'])
@login_required
def sync_calendar():
    """Manually sync existing jobs with Google Calendar (with duplicate prevention)."""
    try:
        db = JobDatabase()
        calendar_manager = GoogleCalendarManager()
        
        if not calendar_manager.calendar_service or not calendar_manager.job_alerts_calendar_id:
            flash('Google Calendar not connected or Job Alerts calendar not created. Please check your connection.', 'danger')
            return redirect(url_for('dashboard'))
        
        # Get all jobs for the user
        jobs, _ = db.get_jobs_for_user(current_user.id, limit=1000)
        
        synced_count = 0
        skipped_count = 0
        
        flash(f'Starting sync of {len(jobs)} jobs to "{calendar_manager.user_name}\'s Job Alerts" calendar...', 'info')
        
        for job in jobs:
            try:
                events_created = 0
                
                # Create deadline reminders for jobs with deadlines
                if job.get('deadline') and job['deadline'] != 'N/A':
                    result = calendar_manager.create_deadline_reminder(job, job['deadline'])
                    if result:
                        events_created += 1
                
                # Create interview events for jobs in interview status
                if job.get('status') == 'interview':
                    result = calendar_manager.create_interview_event(job)
                    if result:
                        events_created += 1
                
                # Create follow-up reminders for applied/offered/rejected jobs
                if job.get('status') in ['applied', 'offered', 'rejected']:
                    result = calendar_manager.create_followup_reminder(job, job['status'])
                    if result:
                        events_created += 1
                
                if events_created > 0:
                    synced_count += events_created
                else:
                    skipped_count += 1
                    
            except Exception as e:
                logger.warning(f"Failed to sync job {job.get('id')}: {e}")
                skipped_count += 1
                continue
        
        if synced_count > 0:
            flash(f'✅ Successfully synced {synced_count} calendar events! {skipped_count} jobs skipped (no events needed or duplicates prevented).', 'success')
        else:
            flash(f'No new calendar events created. {skipped_count} jobs processed (may already have events or no events needed).', 'info')
        
    except Exception as e:
        logger.error(f"Calendar sync failed: {e}")
        flash('Calendar sync failed. Please check your Google Calendar connection.', 'danger')
    
    return redirect(url_for('dashboard'))

@app.route('/test_calendar', methods=['POST'])
@login_required
def test_calendar():
    """Test Google Calendar connection."""
    try:
        calendar_manager = GoogleCalendarManager()
        
        if not calendar_manager.calendar_service:
            flash('Google Calendar connection failed. Please check your credentials.json file.', 'danger')
            return redirect(url_for('dashboard'))
        
        # Try to list calendars to test connection
        calendars = calendar_manager.calendar_service.calendarList().list().execute()
        primary_calendar = next((cal for cal in calendars['items'] if cal.get('primary')), None)
        
        if primary_calendar:
            flash(f'✅ Google Calendar connected successfully! Primary calendar: {primary_calendar.get("summary", "Unknown")}', 'success')
        else:
            flash('Google Calendar connected but no primary calendar found.', 'warning')
            
    except Exception as e:
        logger.error(f"Calendar test failed: {e}")
        error_str = str(e).lower()
        if "insufficient authentication scopes" in error_str:
            flash('❌ Calendar permissions missing. Click "Re-authorize Google APIs" to fix this.', 'danger')
        elif "accessnotconfigured" in error_str or "has not been used" in error_str:
            flash('❌ Google Calendar API not enabled. Please enable it in Google Cloud Console for project: job-alert-automation-465708', 'danger')
        else:
            flash(f'Google Calendar connection test failed: {str(e)}', 'danger')
    
    return redirect(url_for('dashboard'))

@app.route('/reauth_google', methods=['POST'])
@login_required
def reauth_google():
    """Force re-authentication with Google APIs to get all required scopes."""
    try:
        # Delete existing token to force re-auth
        if os.path.exists('token.pickle'):
            os.remove('token.pickle')
            logger.info("Deleted existing token.pickle for re-authentication")
        
        # Force new authentication
        emailer = SmartEmailer()
        if emailer.gmail_service:
            flash('✅ Google APIs re-authorized successfully! You now have Gmail and Calendar access.', 'success')
        else:
            flash('❌ Re-authorization failed. Please check your credentials.json file.', 'danger')
            
    except Exception as e:
        logger.error(f"Re-authorization failed: {e}")
        flash(f'Re-authorization failed: {str(e)}', 'danger')
    
    return redirect(url_for('dashboard'))

@app.route('/calendar_events')
@login_required
def get_calendar_events():
    """Get all job-related calendar events."""
    try:
        calendar_manager = GoogleCalendarManager()
        
        if not calendar_manager.calendar_service:
            return jsonify({'error': 'Calendar not connected'}), 400
        
        # Get events from the last 30 days to next 90 days
        from datetime import datetime, timedelta
        import pytz
        
        now = datetime.now(pytz.UTC)
        time_min = (now - timedelta(days=30)).isoformat()
        time_max = (now + timedelta(days=90)).isoformat()
        
        # Search for events in our Job Alerts calendar
        calendar_id = calendar_manager.job_alerts_calendar_id or 'primary'
        
        events_result = calendar_manager.calendar_service.events().list(
            calendarId=calendar_id,
            timeMin=time_min,
            timeMax=time_max,
            maxResults=100,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        # Format events for display
        formatted_events = []
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            # Parse datetime for better display
            try:
                if 'T' in start:
                    dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                    display_date = dt.strftime('%Y-%m-%d %H:%M')
                else:
                    display_date = start
            except:
                display_date = start
                
            formatted_events.append({
                'id': event['id'],
                'summary': event.get('summary', 'No Title'),
                'description': event.get('description', ''),
                'start': display_date,
                'htmlLink': event.get('htmlLink', ''),
                'created': event.get('created', ''),
                'calendar_id': calendar_id
            })
        
        return jsonify({'events': formatted_events})
        
    except Exception as e:
        logger.error(f"Failed to get calendar events: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/delete_calendar_event/<event_id>', methods=['DELETE'])
@login_required
def delete_calendar_event(event_id):
    """Delete a specific calendar event."""
    try:
        calendar_manager = GoogleCalendarManager()
        
        if not calendar_manager.calendar_service:
            return jsonify({'error': 'Calendar not connected'}), 400
        
        # Use the Job Alerts calendar or primary calendar
        calendar_id = calendar_manager.job_alerts_calendar_id or 'primary'
        
        # Delete the event
        calendar_manager.calendar_service.events().delete(
            calendarId=calendar_id,
            eventId=event_id
        ).execute()
        
        return jsonify({'success': True, 'message': 'Event deleted successfully'})
        
    except Exception as e:
        logger.error(f"Failed to delete calendar event {event_id}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/calendar_sync_status')
@login_required
def calendar_sync_status():
    """Check if calendar is in sync and return last sync time."""
    try:
        calendar_manager = GoogleCalendarManager()
        
        if not calendar_manager.calendar_service:
            return jsonify({'error': 'Calendar not connected', 'synced': False}), 400
        
        # Get current event count
        from datetime import datetime, timedelta
        import pytz
        
        now = datetime.now(pytz.UTC)
        time_min = (now - timedelta(days=30)).isoformat()
        time_max = (now + timedelta(days=90)).isoformat()
        
        calendar_id = calendar_manager.job_alerts_calendar_id or 'primary'
        
        events_result = calendar_manager.calendar_service.events().list(
            calendarId=calendar_id,
            timeMin=time_min,
            timeMax=time_max,
            maxResults=100,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        return jsonify({
            'synced': True,
            'event_count': len(events),
            'last_sync': now.isoformat(),
            'calendar_id': calendar_id
        })
        
    except Exception as e:
        logger.error(f"Failed to check calendar sync status: {e}")
        return jsonify({'error': str(e), 'synced': False}), 500


# --- Missing Routes for Dashboard JavaScript ---

@app.route('/start_scrape', methods=['POST'])
@login_required
def start_scrape():
    """Start job scraping task and return task ID."""
    try:
        search_terms = request.form.get('search_terms', '')
        location = request.form.get('location', '')
        experience = request.form.get('experience', '')
        job_type = request.form.get('job_type', '')
        
        if not search_terms:
            return jsonify({'error': 'Search terms are required'}), 400
        
        # Convert search terms to list
        search_terms_list = [term.strip() for term in search_terms.split(',') if term.strip()]
        
        # Start the Celery task
        task = run_job_hunt_task.delay(
            current_user.id, search_terms_list, location, experience, job_type
        )
        
        return jsonify({
            'task_id': task.id,
            'status': 'started',
            'message': 'Job search started successfully'
        })
        
    except Exception as e:
        logger.error(f"Failed to start scraping task: {e}")
        return jsonify({'error': 'Failed to start search. Celery worker might be down.'}), 500


@app.route('/status/<task_id>')
@login_required
def status(task_id):
    """Get status of a Celery task."""
    try:
        task = run_job_hunt_task.AsyncResult(task_id)
        
        if task.state == 'PENDING':
            response = {
                'status': 'Pending...',
                'progress': 0,
                'details': 'Task is waiting to be processed...'
            }
        elif task.state == 'PROGRESS':
            response = {
                'status': task.info.get('status', 'In Progress...'),
                'progress': task.info.get('progress', 0),
                'details': task.info.get('status', 'Processing...')  # Use status as details for now
            }
        elif task.state == 'SUCCESS':
            response = {
                'status': 'SUCCESS',
                'progress': 100,
                'details': 'Job search completed successfully!',
                'message': task.info.get('message', 'Search completed')
            }
        else:  # FAILURE
            response = {
                'status': 'FAILURE',
                'progress': 100,
                'details': f'Task failed: {str(task.info)}',
                'message': 'Search failed'
            }
            
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Failed to get task status: {e}")
        return jsonify({
            'status': 'ERROR',
            'progress': 0,
            'details': f'Error checking task status: {str(e)}'
        }), 500


@app.route('/jobs')
@login_required
def jobs():
    """Get jobs for current user as JSON."""
    try:
        db = JobDatabase()
        jobs_data, total_count = db.get_jobs_for_user(current_user.id, limit=100)
        
        # Format jobs for frontend
        def get_status_colors(status):
            status_colors = {
                'new': {'bg': '#f3f4f6', 'text': '#374151'},
                'applied': {'bg': '#dcfce7', 'text': '#166534'},
                'interview': {'bg': '#e0e7ff', 'text': '#3730a3'},
                'offered': {'bg': '#fef3c7', 'text': '#92400e'},
                'rejected': {'bg': '#fee2e2', 'text': '#991b1b'},
                'withdrawn': {'bg': '#f3f4f6', 'text': '#6b7280'}
            }
            return status_colors.get(status, status_colors['new'])
        
        formatted_jobs = []
        for job in jobs_data:
            colors = get_status_colors(job.get('status', 'new'))
            formatted_job = {
                'id': job['id'],
                'title': job['title'],
                'company': job['company'],
                'location': job['location'],
                'salary': job['salary'] or 'Not specified',
                'link': job['link'],
                'post_date': job['posted_date'],
                'status': job['status'],
                'status_color': colors['bg'],
                'status_text_color': colors['text'],
                'description': job['description'][:200] + '...' if len(job.get('description', '')) > 200 else job.get('description', '')
            }
            formatted_jobs.append(formatted_job)
        
        return jsonify(formatted_jobs)
        
    except Exception as e:
        logger.error(f"Failed to fetch jobs: {e}")
        return jsonify({'error': 'Failed to fetch jobs'}), 500



# This part runs the Flask app if executed directly
if __name__ == "__main__":
    # Initialize database
    db_instance = JobDatabase()
    db_instance.init_db() # Ensure tables are created/migrated

    # Setup signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, lambda s, f: sys.exit(0))
    signal.signal(signal.SIGTERM, lambda s, f: sys.exit(0))
    
    logger.info("Starting Flask application...")
    app.run(debug=True, host='0.0.0.0', port=5000)
