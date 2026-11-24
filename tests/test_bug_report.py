"""Tests for Snapy quick beta bug reporting endpoint."""

import os
import sys
import unittest
from unittest.mock import patch

from flask import g
from werkzeug.security import generate_password_hash

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, JobDatabase


class BugReportTestDatabase(JobDatabase):
    def __init__(self, db_path="test_bug_reports.db"):
        super().__init__(db_path)


class SnapyBugReportTestCase(unittest.TestCase):
    def setUp(self):
        self.test_db_path = "test_bug_reports.db"
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
        self.db_patcher = patch("app.JobDatabase", side_effect=BugReportTestDatabase)
        self.db_patcher.start()

        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        app.config["SECRET_KEY"] = "test-bug-secret"
        app.config["DISABLE_RATE_LIMIT"] = True

        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()

        db = BugReportTestDatabase()
        db.init_db()
        db.add_user(
            "beta_tester",
            generate_password_hash("password123"),
            role="seeker",
            email="tester@example.com",
            account_status="active",
            onboarding_completed=True,
        )
        g.pop("_login_user", None)
        self.client.post("/login", data={"username": "beta_tester", "password": "password123"})
        g.pop("_login_user", None)

    def tearDown(self):
        self.db_patcher.stop()
        self.app_context.pop()
        if os.path.exists(self.test_db_path):
            try:
                os.remove(self.test_db_path)
            except OSError:
                pass

    def test_submit_and_store_bug_report(self):
        # Rejects empty description
        bad = self.client.post("/api/snapy/bug-report", json={"category": "Scraper", "description": "hi"})
        self.assertEqual(bad.status_code, 400)

        # Accepts valid report and stores it in DB
        resp = self.client.post(
            "/api/snapy/bug-report",
            json={
                "category": "Scraper",
                "description": "Play button on saved preset did not respond on Safari.",
                "steps": "Clicked Play twice",
                "page_url": "https://app.jobsnap.me/dashboard",
                "viewport": "390x844",
            },
        )
        self.assertEqual(resp.status_code, 201)
        data = resp.get_json()
        self.assertTrue(data["success"])
        self.assertGreater(data["report_id"], 0)

        rows = BugReportTestDatabase().list_bug_reports(limit=10)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["category"], "Scraper")
        self.assertEqual(rows[0]["username"], "beta_tester")
        self.assertIn("Play button", rows[0]["description"])


if __name__ == "__main__":
    unittest.main()
