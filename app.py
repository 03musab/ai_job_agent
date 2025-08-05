import requests
from bs4 import BeautifulSoup
import datetime, schedule, time, os, pickle, base64, json, sys, signal
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import sqlite3
import hashlib
import re
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException as SeleniumWebDriverException
import pandas as pd
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import concurrent.futures
import random
import threading
import traceback
from collections import Counter
import gevent.monkey
gevent.monkey.patch_all(ssl=False) # FIX: Prevent recursion error by not patching SSL

# --- Flask & Celery Imports ---
from flask import Flask, request, render_template, redirect, url_for, flash, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from celery import Celery

# --- Logging Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Celery Configuration ---
def make_celery(app):
    """Create and configure Celery instance."""
    celery = Celery(
        app.import_name,
        backend=os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0'),
        broker=os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    )
    celery.conf.update(app.config)
    return celery

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['CELERY_BROKER_URL'] = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
app.config['CELERY_RESULT_BACKEND'] = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

# Initialize Celery
celery = make_celery(app)

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


# --- Google API Scopes for Gmail ---
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

# --- Admin Email for Critical Alerts ---
ADMIN_ALERT_EMAIL = os.environ.get('ADMIN_ALERT_EMAIL', 'musabimp.0@gmail.com')


# --- Add a list of common User-Agent strings to mimic different browsers ---
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:107.0) Gecko/20100101 Firefox/107.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36 Edg/108.0.1462.46',
]


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
            'relevance_score': self.relevance_score,
            'min_experience_years': self.min_experience_years,
            'max_experience_years': self.max_experience_years,
            'extracted_tools': ', '.join(self.extracted_tools),
            'extracted_soft_skills': ', '.join(self.extracted_soft_skills),
            'user_feedback': self.user_feedback
        }

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

    def add_job(self, job: Job, user_id: Optional[int] = None):
        """Adds a job to the database with deduplication and user association."""
        job_hash = hashlib.md5(f"{job.title}{job.company}{job.location}".encode()).hexdigest()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO jobs
                (job_hash, title, company, location, salary, link, description,
                 keywords, skills, experience, job_type, posted_date, source,
                 relevance_score, found_date, user_id, status, notes,
                 min_experience_years, max_experience_years, extracted_tools, extracted_soft_skills, user_feedback)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                job_hash, job.title, job.company, job.location, job.salary,
                job.link, job.description, ', '.join(job.keywords),
                ', '.join(job.skills), job.experience, job.job_type,
                job.posted_date, job.source, job.relevance_score,
                datetime.datetime.now().isoformat(), user_id,
                'new', '', # Default status and notes
                job.min_experience_years, job.max_experience_years,
                ', '.join(job.extracted_tools), ', '.join(job.extracted_soft_skills),
                job.user_feedback if job.user_feedback else ''
            ))
            conn.commit()
            if cursor.rowcount > 0:
                logger.debug(f"Added new job to DB: {job.title} at {job.company} for user {user_id}")
                return True
            else:
                logger.debug(f"Job already exists in DB (skipped): {job.title} at {job.company} for user {user_id}")
                return False
        except sqlite3.OperationalError as e:
            logger.error(f"SQLite Operational Error (likely schema mismatch during job insert): {e}.")
            logger.error("Attempting to insert values: %s", (job_hash, job.title, job.company, job.location, job.salary, job.link, job.description, ', '.join(job.keywords), ', '.join(job.skills), job.experience, job.job_type, job.posted_date, job.source, job.relevance_score, datetime.datetime.now().isoformat(), user_id, 'new', '', job.min_experience_years, job.max_experience_years, ', '.join(job.extracted_tools), ', '.join(job.extracted_soft_skills), job.user_feedback))
            return False
        except Exception as e:
            logger.error(f"Error adding job to database: {e}")
            return False
        finally:
            conn.close()

    def get_jobs_for_user(self, user_id: int, limit=100, offset=0,
                         sort_by='found_date', sort_order='DESC',
                         search_query: Optional[str] = None,
                         status_filter: Optional[str] = None) -> Tuple[List[Dict], int]:
        """Retrieves jobs for a specific user from the database, with filters and pagination."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query_columns = """
            id, job_hash, title, company, location, salary, link, description,
            keywords, skills, experience, job_type, posted_date, source,
            relevance_score, found_date, applied, status, user_id, notes,
            min_experience_years, max_experience_years, extracted_tools, extracted_soft_skills, user_feedback
        """
        query = f"SELECT {query_columns} FROM jobs WHERE user_id = ?"
        params = [user_id]

        if search_query:
            search_pattern = f"%{search_query}%"
            query += " AND (title LIKE ? OR company LIKE ? OR description LIKE ? OR location LIKE ? OR notes LIKE ? OR keywords LIKE ? OR skills LIKE ? OR extracted_tools LIKE ? OR extracted_soft_skills LIKE ?)"
            params.extend([search_pattern, search_pattern, search_pattern, search_pattern, search_pattern, search_pattern, search_pattern, search_pattern, search_pattern])

        if status_filter and status_filter != 'all':
            query += " AND status = ?"
            params.append(status_filter)

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
                            location: str, experience: str, job_type: str) -> bool:
        """Saves a search profile for a user."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO search_profiles
                (user_id, profile_name, search_terms, location, experience, job_type)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, profile_name, search_terms, location, experience, job_type))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            logger.warning(f"Attempted to save duplicate profile name '{profile_name}' for user {user_id}.")
            return False
        except Exception as e:
            logger.error(f"Error saving search profile: {e}")
            return False
        finally:
            conn.close()

    def get_search_profiles(self, user_id: int) -> List[Dict]:
        """Retrieves all saved search profiles for a user."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, profile_name, search_terms, location, experience, job_type FROM search_profiles WHERE user_id = ?", (user_id,))
        profiles_raw = cursor.fetchall()
        conn.close()

        column_names = [description[0] for description in cursor.description]
        profiles = [dict(zip(column_names, profile_tuple)) for profile_tuple in profiles_raw]
        return profiles

    def get_search_profile_by_id(self, profile_id: int, user_id: int) -> Optional[Dict]:
        """Retrieves a single search profile by ID and user ID."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, profile_name, search_terms, location, experience, job_type FROM search_profiles WHERE id = ? AND user_id = ?", (profile_id, user_id))
        profile_data = cursor.fetchone()
        conn.close()
        if profile_data:
            column_names = [description[0] for description in cursor.description]
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
            ''', (email_recipients, email_frequency, send_excel_attachment, user_id))
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


class EnhancedJobScraper:
    """Advanced job scraper with multiple sources and strategies."""
    
    def __init__(self, search_terms: List[str], location: Optional[str],
                 experience: Optional[str], job_type: Optional[str], user_id: int):
        self.search_terms = search_terms
        self.location = location
        self.experience = experience
        self.job_type = job_type
        self.user_id = user_id
        self.db = JobDatabase()
        self.custom_scores = self.db.get_custom_scores(self.user_id)
        self.session = requests.Session()
        
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
            options.add_argument('--headless')
            options.add_argument('--disable-gpu')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            random_user_agent = random.choice(USER_AGENTS)
            options.add_argument(f"user-agent={random_user_agent}")
            
            service = EdgeService(executable_path=DRIVER_PATHS['edge'])
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
        text_lower = text.lower()

        match_range = re.search(r'(\d+)\s*-\s*(\d+)\s*years?', text_lower)
        if match_range:
            min_exp = int(match_range.group(1))
            max_exp = int(match_range.group(2))
        else:
            match_plus = re.search(r'(\d+)\s*\+\s*years?', text_lower)
            if match_plus:
                min_exp = int(match_plus.group(1))
                max_exp = None
            else:
                match_single = re.search(r'(\d+)\s*year[s]?\s*experience', text_lower)
                if match_single:
                    min_exp = int(match_single.group(1))
                    max_exp = int(match_single.group(1))
                else:
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
                score += 30 * self.custom_scores.get((term.lower(), 'keywords'), 1.0)
            elif term.lower() in job_description_lower:
                score += 10 * self.custom_scores.get((term.lower(), 'keywords'), 1.0)

        for skill in job.skills:
            score += 5 * self.custom_scores.get((skill.lower(), 'skills'), 1.0)
        for tool in job.extracted_tools:
            score += 4 * self.custom_scores.get((tool.lower(), 'tools_platforms'), 1.0)
        for soft_skill in job.extracted_soft_skills:
            score += 3 * self.custom_scores.get((soft_skill.lower(), 'soft_skills'), 1.0)

        for word in re.findall(r'\b\w+\b', job_title_lower):
            score += 2 * self.custom_scores.get((word, 'title_word'), 1.0)

        if self.experience:
            user_min_exp, user_max_exp = self._extract_experience_years(self.experience)
            if user_min_exp is not None:
                if job.min_experience_years is not None and job.max_experience_years is not None:
                    if max(user_min_exp, job.min_experience_years) <= min(user_max_exp if user_max_exp is not None else float('inf'), job.max_experience_years if job.max_experience_years is not None else float('inf')):
                        score += 20
                elif job.min_experience_years is not None and job.max_experience_years is None:
                    if user_min_exp >= job.min_experience_years:
                        score += 20
                elif job.min_experience_years is not None and user_max_exp is None:
                    if job.min_experience_years >= user_min_exp:
                        score += 20
                elif job.min_experience_years is None:
                    exp_match_keywords = self._extract_keywords_from_description(job.experience, re.findall(r'\b\w+\b', self.experience.lower()))
                    if exp_match_keywords:
                        score += 10

        if self.location and self.location.lower() in job.location.lower():
            score += 15

        if self.job_type and self.job_type.lower() in job.job_type.lower():
            score += 10

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
            score *= 1.2
        elif days_ago <= 30:
            score *= 1.05

        return round(score, 2)


    def scrape_linkedin_jobs(self, term: str) -> List[Job]:
        """
        Enhanced LinkedIn scraper: robust, stealthy, paginated, and with anti-bot/anti-scraping security.
        """
        logger.info(f"[LinkedIn] Scraping for term '{term}' in {self.location or 'All Locations'}...")
        jobs = []
        seen_links = set()
        max_pages = 3  # LinkedIn throttles hard, so keep this low
        base_url = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
        proxies = None  # Optionally add proxy support here
        for page in range(0, max_pages):
            params = {
                'keywords': term,
                'location': self.location,
                'start': page * 25,
                'count': 25
            }
            headers = {'User-Agent': random.choice(USER_AGENTS)}
            try:
                time.sleep(random.uniform(2, 5))
                response = self.session.get(base_url, params=params, headers=headers, timeout=15, proxies=proxies)
                if response.status_code != 200:
                    logger.warning(f"[LinkedIn] Non-200 status {response.status_code} on page {page+1} for '{term}'.")
                    break
                # Anti-bot: check for login/captcha or suspicious content
                if b'captcha' in response.content.lower() or b'login' in response.content.lower():
                    logger.warning(f"[LinkedIn] Possible bot detection or login wall encountered on page {page+1} for '{term}'. Aborting.")
                    break
                try:
                    soup = BeautifulSoup(response.content, 'lxml')
                except Exception:
                    soup = BeautifulSoup(response.content, 'html.parser')
                job_cards = soup.find_all('div', class_='job-search-card')
                if not job_cards:
                    logger.info(f"[LinkedIn] No job cards found on page {page+1} for '{term}'. Stopping.")
                    break
                logger.info(f"[LinkedIn] Page {page+1}: Found {len(job_cards)} job cards.")
                for card in job_cards:
                    try:
                        # --- Robust title extraction ---
                        title_elem = card.find('h3', class_='base-search-card__title')
                        if not title_elem:
                            title_elem = card.find(lambda tag: tag.name in ['h3','span','a'] and 'title' in ''.join(tag.get('class', [])) and tag.text.strip())
                        title = title_elem.text.strip() if title_elem else 'N/A'
                        if title == 'N/A':
                            logger.warning(f"[LinkedIn] Could not extract title. Card HTML: {card.prettify()}")

                        # --- Robust company extraction ---
                        company_elem = card.find('h4', class_='base-search-card__subtitle')
                        if not company_elem:
                            company_elem = card.find(lambda tag: tag.name in ['h4','span','div'] and ('company' in ''.join(tag.get('class', [])) or 'subtitle' in ''.join(tag.get('class', []))) and tag.text.strip())
                        company = company_elem.text.strip() if company_elem else 'N/A'
                        if company == 'N/A':
                            logger.warning(f"[LinkedIn] Could not extract company. Card HTML: {card.prettify()}")

                        # --- Robust location extraction ---
                        location_elem = card.find('span', class_='job-search-card__location')
                        if not location_elem:
                            location_elem = card.find(lambda tag: tag.name in ['span','div'] and 'location' in ''.join(tag.get('class', [])) and tag.text.strip())
                        location = location_elem.text.strip() if location_elem else 'N/A'
                        if location == 'N/A':
                            logger.warning(f"[LinkedIn] Could not extract location. Card HTML: {card.prettify()}")

                        # --- Robust link extraction ---
                        link_elem = card.find('a', class_='base-card__full-link')
                        if not link_elem:
                            link_elem = card.find('a', href=True)
                        link = link_elem.get('href') if link_elem and link_elem.get('href') else 'N/A'
                        if link in seen_links or link == 'N/A':
                            continue
                        seen_links.add(link)

                        posted_date_elem = card.find('time', class_='job-search-card__listdate')
                        if not posted_date_elem:
                            posted_date_elem = card.find('time')
                        posted_date = posted_date_elem.get('datetime') if posted_date_elem and posted_date_elem.get('datetime') else (posted_date_elem.text.strip() if posted_date_elem else 'N/A')
                        description = card.text.strip() if card.text else 'N/A'
                        raw_data = {
                            'title': title,
                            'company': company,
                            'location': location,
                            'link': link,
                            'description': description,
                            'posted_date': posted_date,
                            'source': 'LinkedIn'
                        }
                        jobs.append(self._create_job_object_from_raw_data(raw_data))
                    except Exception as e:
                        logger.warning(f"[LinkedIn] Error extracting job card: {e}", exc_info=True)
                        continue
                # If less than 10 jobs, likely last page
                if len(job_cards) < 10:
                    break
            except requests.exceptions.RequestException as e:
                logger.error(f"[LinkedIn] Network error on page {page+1} for '{term}': {e}", exc_info=True)
                continue
            except Exception as e:
                logger.error(f"[LinkedIn] Unexpected error on page {page+1} for '{term}': {e}", exc_info=True)
                continue
        logger.info(f"[LinkedIn] ✅ Scraped {len(jobs)} jobs for '{term}'.")
        return jobs
    #22
 
# --- Rewritten scrape_internshala_jobs to use requests/BeautifulSoup ---
    def scrape_internshala_jobs(self, term: str) -> List[Job]:
        """
        Enhanced Internshala scraper: robust, paginated, stealthy, and extracts more job details.
        """
        logger.info(f"[Internshala] Scraping for term '{term}' in {self.location or 'All Locations'}...")
        jobs = []
        seen_links = set()
        max_pages = 5  # Scrape up to 5 pages for depth
        base_url = "https://internshala.com/jobs/keywords-{}".format(term.replace(' ', '-'))
        if self.location:
            base_url += f"-{self.location.replace(' ', '-')}"
        base_url += "/"

        for page in range(1, max_pages + 1):
            url = base_url + (f"page-{page}/" if page > 1 else "")
            headers = {'User-Agent': random.choice(USER_AGENTS)}
            proxies = None  # Optionally add proxy support here
            try:
                time.sleep(random.uniform(1.5, 3.5))
                response = self.session.get(url, headers=headers, timeout=15, proxies=proxies)
                if response.status_code != 200:
                    logger.warning(f"[Internshala] Non-200 status {response.status_code} on page {page} for '{term}'.")
                    break
                soup = BeautifulSoup(response.content, 'lxml')
                job_cards = soup.find_all('div', class_='individual_internship')
                if not job_cards:
                    logger.info(f"[Internshala] No job cards found on page {page} for '{term}'. Stopping.")
                    break
                logger.info(f"[Internshala] Page {page}: Found {len(job_cards)} job cards.")
                for card in job_cards:
                    # Skip generic/promo/placement guarantee cards
                    if 'pgc-card' in card.get('class', []) or card.find('div', class_='main-content generic'):
                        continue
                    link_elem = card.find('a', href=True)
                    if not link_elem or '/internship/detail/' not in link_elem.get('href', ''):
                        continue
                    try:
                        title_elem = card.find('h3', class_='job-internship-name')
                        # --- Robust company extraction ---
                        company_elem = card.find('p', class_='company_name')
                        if not company_elem:
                            company_elem = card.find('div', class_='company_name')
                        if not company_elem:
                            # Try to find by text pattern
                            company_elem = card.find(lambda tag: tag.name in ['p','div','span'] and 'company' in tag.get('class', []) and tag.text.strip())
                        company = company_elem.text.strip() if company_elem else 'N/A'
                        if company == 'N/A':
                            logger.warning(f"[Internshala] Could not extract company. Card HTML: {card.prettify()}")

                        # --- Robust location extraction ---
                        location_elem = card.find('p', class_='location_names')
                        if not location_elem:
                            location_elem = card.find('div', class_='location_names')
                        if not location_elem:
                            # Try to find by text pattern
                            location_elem = card.find(lambda tag: tag.name in ['p','div','span'] and 'location' in ''.join(tag.get('class', [])) and tag.text.strip())
                        location = location_elem.text.strip() if location_elem else 'N/A'
                        if location == 'N/A':
                            logger.warning(f"[Internshala] Could not extract location. Card HTML: {card.prettify()}")

                        link_elem = title_elem.find('a') if title_elem else None
                        posted_date_elem = None
                        detail_row_2 = card.find('div', class_='detail-row-2')
                        if detail_row_2:
                            posted_date_elem = detail_row_2.find('span', class_='status-success')
                        stipend_elem = card.find('span', class_='stipend')
                        duration_elem = card.find('span', class_='duration')
                        skills_elem = card.find('div', class_='container-fluid individual_internship_skills')
                        # Extract details
                        title = title_elem.text.strip() if title_elem else 'N/A'
                        link = f"https://internshala.com{link_elem.get('href')}" if link_elem and link_elem.get('href') else 'N/A'
                        posted_date = posted_date_elem.text.strip() if posted_date_elem else 'N/A'
                        stipend = stipend_elem.text.strip() if stipend_elem else 'N/A'
                        duration = duration_elem.text.strip() if duration_elem else 'N/A'
                        skills = [s.text.strip() for s in skills_elem.find_all('a')] if skills_elem else []
                        description_elem = card.find('div', class_='internship_other_details_container')
                        description = description_elem.text.strip() if description_elem else card.text.strip()
                        # Deduplication
                        if link in seen_links or link == 'N/A':
                            continue
                        seen_links.add(link)
                        # Compose raw_data
                        raw_data = {
                            'title': title,
                            'company': company,
                            'location': location,
                            'link': link,
                            'description': description,
                            'posted_date': posted_date,
                            'salary': stipend,
                            'job_type': duration,
                            'skills': skills,
                            'source': 'Internshala'
                        }
                        jobs.append(self._create_job_object_from_raw_data(raw_data))
                    except Exception as e:
                        logger.warning(f"[Internshala] Error extracting job card: {e}", exc_info=True)
                        continue
                # If less than 10 jobs, likely last page
                if len(job_cards) < 10:
                    break
            except requests.exceptions.RequestException as e:
                logger.error(f"[Internshala] Network error on page {page} for '{term}': {e}", exc_info=True)
                continue
            except Exception as e:
                logger.error(f"[Internshala] Unexpected error on page {page} for '{term}': {e}", exc_info=True)
                continue
        logger.info(f"[Internshala] ✅ Scraped {len(jobs)} jobs for '{term}'.")
        return jobs

    def _create_job_object_from_raw_data(self, raw_data: Dict) -> Job:
        """Helper to create a Job object and calculate its relevance score."""
        salary = raw_data.get('salary', '')
        experience = raw_data.get('experience', '')
        if 'description' in raw_data:
            salary = self._extract_salary(raw_data['description']) or salary
            experience = self._extract_experience(raw_data['description']) or experience

        job_obj = Job(
            title=raw_data.get('title', ''),
            company=raw_data.get('company', ''),
            location=raw_data.get('location', ''),
            salary=salary,
            link=raw_data.get('link', ''),
            description=raw_data.get('description', ''),
            keywords=self.search_terms,
            skills=self._extract_keywords_from_description(raw_data.get('description', ''), self.common_skills),
            experience=experience,
            job_type=raw_data.get('job_type', 'Full-time'),
            posted_date=raw_data.get('posted_date', ''),
            source=raw_data.get('source', '')
        )
        job_obj.min_experience_years, job_obj.max_experience_years = self._extract_experience_years(job_obj.description)
        job_obj.extracted_tools = self._extract_keywords_from_description(job_obj.description, self.tools_platforms)
        job_obj.extracted_soft_skills = self._extract_keywords_from_description(job_obj.description, self.soft_skills)
        job_obj.relevance_score = self._calculate_relevance_score(job_obj)
        return job_obj
        
    def _extract_salary(self, text: str) -> str:
        """Extracts salary information from text using regex patterns."""
        patterns = [
            r'₹?\s*([\d,]+\s*(?:-\s*[\d,]+)?\s*(?:lpa|lakhs?|ctc))',
            r'(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)\s*(?:lpa|lakhs?)',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        return "N/A"

    def _extract_experience(self, text: str) -> str:
        """Extracts experience requirements from text using regex patterns."""
        patterns = [
            r'(\d+)\s*-\s*(\d+)\s*years?',
            r'(\d+)\+?\s*years?',
            r'(fresher|entry\.level|junior|senior|lead|manager)',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        return "N/A"

    def scrape_all_sources(self) -> List[Job]:
        """Scrapes jobs from all configured sources concurrently."""
        all_jobs = []
        scraper_methods = {
            'LinkedIn': self.scrape_linkedin_jobs,
            'Internshala': self.scrape_internshala_jobs
        }

        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
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
                except Exception as exc:
                    logger.error(f'{source_info} generated an exception: {exc}', exc_info=True)
                    
        logger.info(f"Total jobs scraped across all sources before deduplication: {len(all_jobs)}.")
        
        unique_jobs = {}
        for job in all_jobs:
            key = hashlib.md5(f"{job.title.lower()}_{job.company.lower()}_{job.location.lower()}".encode()).hexdigest()
            if key not in unique_jobs or job.relevance_score > unique_jobs[key].relevance_score:
                unique_jobs[key] = job
        
        filtered_jobs = list(unique_jobs.values())
        filtered_jobs = [job for job in filtered_jobs if job.title and job.link]
        
        high_relevance_jobs = [job for job in filtered_jobs if job.relevance_score >= 10]
        high_relevance_jobs.sort(key=lambda x: x.relevance_score, reverse=True)
        
        logger.info(f"Jobs count after filtering by relevance_score >= 10: {len(high_relevance_jobs)}.")
        
        source_counts = Counter(job.source for job in high_relevance_jobs)
        for source, count in source_counts.items():
            logger.info(f"Final jobs from {source}: {count}.")
            
        return high_relevance_jobs[:50]

class SmartEmailer:
    """Enhanced email system with better formatting and attachments using Gmail API."""
    def __init__(self):
        self.gmail_service = self.authenticate_gmail()

    def authenticate_gmail(self):
        creds = None
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    # FIX: Use google.auth.transport.requests.Request() for token refresh
                    creds.refresh(Request())
                except Exception as e:
                    logger.critical(f"Failed to refresh Gmail API token: {e}")
                    return None
            else:
                try:
                    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                    creds = flow.run_local_server(port=0)
                except Exception as e:
                    logger.critical(f"Failed to authenticate with Gmail API: {e}")
                    return None
        
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        
        return build('gmail', 'v1', credentials=creds)

    def create_excel_report(self, jobs: List[Job]) -> str:
        from openpyxl.styles import Font, PatternFill, Alignment, Border, Side, GradientFill
        from openpyxl.utils import get_column_letter
        filename = f"jobs_report_{datetime.date.today().strftime('%Y%m%d')}.xlsx"
        job_data = [job.to_dict() for job in jobs]
        # Remove 'id' column if present and add row number
        df = pd.DataFrame(job_data)
        if 'id' in df.columns:
            df = df.drop(columns=['id'])
        df.insert(0, 'No.', range(1, len(df) + 1))
        try:
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Jobs', index=False)
                workbook = writer.book
                worksheet = writer.sheets['Jobs']
                # --- Add Title Row ---
                title = f"Job Report – {datetime.date.today().strftime('%B %d, %Y')} (Total: {len(jobs)} / 100)"
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
                    'source': 'Source',
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
                                <a href="{job.link}" target="_blank">{job.title}</a>
                            </div>
                            <div class="job-company">{job.company}</div>
                            <div class="job-meta">
                                <span class="job-meta-item">📍 {job.location}</span>
                                {f'<span class="job-meta-item">💰 {job.salary}</span>' if job.salary and job.salary != 'N/A' else ''}
                                {f'<span class="job-meta-item">👨‍💼 {job.experience}</span>' if job.experience and job.experience != 'N/A' else ''}
                                <span class="job-meta-item">🔗 {job.source}</span>
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

    def send_email(self, subject: str, html_content: str, attachment_path: Optional[str] = None):
        """Sends an email with HTML content and an optional attachment using Gmail API."""
        # FIX: Use the already authenticated self.gmail_service from __init__
        # instead of re-authenticating and misusing the returned service object.
        if not self.gmail_service:
            logger.critical("Email not sent: Gmail service not authenticated.")
            return

        message = MIMEMultipart()
        message['to'] = ', '.join(['musabimp.0@gmail.com'])
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
            # FIX: Use the existing service object directly.
            self.gmail_service.users().messages().send(userId='me', body={'raw': raw}).execute()
            logger.info("📧 Email sent successfully!")
        except Exception as e:
            logger.error(f"Error sending email: {e}")

class JobHunter:
    """Main class to run the job alert system."""
    def __init__(self, search_terms: List[str], location: str):
        self.search_terms = search_terms
        self.location = location
        self.db = JobDatabase()
        self.scraper = EnhancedJobScraper(search_terms=self.search_terms, location=self.location, experience="", job_type="", user_id=1)
        self.emailer = SmartEmailer()
        
    def run(self):
        """Orchestrates the entire job search and alert process."""
        logger.info(f"🔍 Starting job hunt for terms: {self.search_terms}, location: {self.location}")
        
        jobs = self.scraper.scrape_all_sources()
        
        if not jobs:
            logger.info("📊 Found 0 new jobs matching criteria today. No email will be sent.")
            
        html = self.emailer.build_smart_html_email(jobs)
        excel_file = self.emailer.create_excel_report(jobs)
        
        subject = f"🧠 {len(jobs)} New Job Matches – {datetime.date.today().strftime('%b %d, %Y')}"
        self.emailer.send_email(subject, html, attachment_path=excel_file)
        
        if os.path.exists(excel_file):
            os.remove(excel_file)
            logger.info(f"Cleaned up Excel report: {excel_file}.")

        logger.info("🤖 Super Job Agent finished its run.")

def main_job_alert_task():
    """Entry point for the scheduled job alert task."""
    hunter = JobHunter(search_terms=['marketing manager', 'digital marketing', 'brand manager', 'web developer'], location='India')
    hunter.run()

def shutdown_handler(signum, frame):
    """Gracefully handle shutdown signals."""
    logger.info(f"Shutdown signal {signum} received. Exiting scheduler loop.")
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)

    logger.info("🚀 Starting Super Job Agent scheduler...")
    main_job_alert_task()
    
    schedule.every().day.at("09:00").do(main_job_alert_task)
    schedule.every().day.at("18:00").do(main_job_alert_task)

    while True:
        schedule.run_pending()
        time.sleep(1)
