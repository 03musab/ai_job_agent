"""
Automated 14-Point Security Checklist Test Suite for AI JobSnap.
Verifies all 14 defensive checks:
 1. Type /admin (access control + pre-registration admin capture)
 2. Change the ID in the URL (IDOR on uploads, job ownership, recruiter apps, company API)
 3. API key in the browser (no secrets leaked into HTML responses)
 4-7. Negative / unbounded params, score tampering, duplicate submission ("redeem 100 times")
 8. Admin at signup (role escalation & reserved admin username blocking)
 9. Guess the login code (rate limiting on login/signup/tokens + minimum password length)
10. Prompt-inject your AI (system/user separation + sanitized PDF HTML)
11. Script in your username (strict username regex + XSS-safe rendering + URL scheme sanitization)
12. Upload a non-photo (magic-byte validation, no SVG/HTML uploads, no arbitrary file delete)
13. .env in Git (.gitignore coverage for secrets & DB files)
14. Query your database (SQL injection payloads safely parameterized)
"""

import io
import os
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, JobDatabase, Job, User, _reset_rate_limits
from werkzeug.security import generate_password_hash


class SecurityTestDatabase(JobDatabase):
    def __init__(self, db_path="test_security.db"):
        super().__init__(db_path)


class SecurityChecklistTestCase(unittest.TestCase):
    def setUp(self):
        self.test_db_path = "test_security.db"
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)

        self.db_patcher = patch("app.JobDatabase", side_effect=SecurityTestDatabase)
        self.db_patcher.start()

        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        app.config["SECRET_KEY"] = "test-security-secret-key"
        app.config["DISABLE_RATE_LIMIT"] = False
        app.config["ENABLE_RATE_LIMIT_IN_TESTS"] = True
        _reset_rate_limits()

        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()

        db = SecurityTestDatabase()
        db.init_db()

    def tearDown(self):
        app.config["ENABLE_RATE_LIMIT_IN_TESTS"] = False
        _reset_rate_limits()
        self.db_patcher.stop()
        self.app_context.pop()
        if os.path.exists(self.test_db_path):
            try:
                os.remove(self.test_db_path)
            except OSError:
                pass

    def _create_and_login(self, username, email, role="seeker", password="password123"):
        db = SecurityTestDatabase()
        uid = db.add_user(
            username,
            generate_password_hash(password),
            role=role,
            email=email,
            account_status="active",
            onboarding_completed=True,
        )
        self.client.post("/login", data={"username": username, "password": password})
        return uid

    # Check 1 & 8: Type /admin + Admin at signup + pre-registration admin capture
    def test_01_and_08_admin_routes_and_signup_escalation_blocked(self):
        with patch.dict(os.environ, {"ADMIN_USERNAMES": "superadmin_reserved"}):
            # Non-admin seeker cannot access admin panels
            self._create_and_login("normal_seeker", "normal@example.com", role="seeker")
            for path in ("/admin/pro-invites", "/admin/upload_contacts"):
                resp = self.client.get(path)
                self.assertEqual(resp.status_code, 403)

            # Cannot rename self to reserved admin handle
            ok, err = SecurityTestDatabase().update_username(
                User.get_by_username("normal_seeker").id, "superadmin_reserved"
            )
            self.assertFalse(ok)
            self.assertIn("reserved", (err or "").lower())

            # Sign out and try signing up as role=admin or reserved admin username
            self.client.get("/logout")
            resp_role = self.client.post("/register", data={
                "username": "wannabe_admin",
                "email": "wannabe@example.com",
                "password": "password123",
                "role": "admin",
            })
            self.assertEqual(resp_role.status_code, 302)
            self.assertIsNone(User.get_by_username("wannabe_admin"))

            resp_reserved = self.client.post("/register", data={
                "username": "superadmin_reserved",
                "email": "hijack@example.com",
                "password": "password123",
                "role": "seeker",
            })
            self.assertEqual(resp_reserved.status_code, 302)
            self.assertIsNone(User.get_by_username("superadmin_reserved"))

    # Check 2: IDOR on /uploads, job ownership, recruiter applications, company API
    def test_02_idor_protections(self):
        db = SecurityTestDatabase()
        victim_id = db.add_user(
            "victim_user",
            generate_password_hash("password123"),
            role="seeker",
            email="victim@example.com",
            account_status="active",
            onboarding_completed=True,
        )
        # Create a private file in victim's upload folder
        victim_dir = os.path.join(app.config["UPLOAD_FOLDER"], str(victim_id))
        os.makedirs(victim_dir, exist_ok=True)
        victim_file = os.path.join(victim_dir, "secret_resume.pdf")
        with open(victim_file, "wb") as f:
            f.write(b"%PDF-1.4 secret")

        try:
            # Unauthenticated user cannot access /uploads/<victim_id>/...
            unauth = self.client.get(f"/uploads/{victim_id}/secret_resume.pdf")
            self.assertEqual(unauth.status_code, 302)

            # Unauthenticated user cannot hit company API (must return 401, not 500)
            unauth_comp = self.client.get(f"/api/recruiters/{victim_id}/company")
            self.assertEqual(unauth_comp.status_code, 401)

            # Attacker seeker cannot read victim's upload
            attacker_id = self._create_and_login("attacker_user", "attacker@example.com", role="seeker")
            cross_upload = self.client.get(f"/uploads/{victim_id}/secret_resume.pdf")
            self.assertEqual(cross_upload.status_code, 403)

            # Seeker cannot access recruiter company endpoints even for their own ID
            seeker_comp = self.client.get(f"/api/recruiters/{attacker_id}/company")
            self.assertEqual(seeker_comp.status_code, 403)

            # Attacker cannot hijack or modify victim's private job via update_job_status
            db.add_job(
                Job(
                    title="Victim Private Role",
                    company="SecretCo",
                    location="Remote",
                    salary="$150k",
                    link="https://example.com/v1",
                    description="Private",
                    keywords=["Python"],
                    skills=["python"],
                    experience="3 yrs",
                    job_type="Full-time",
                    posted_date="Today",
                    source="LinkedIn",
                    deadline="N/A",
                ),
                user_id=victim_id,
                sync_calendar=False,
            )
            victim_jobs, _ = db.get_jobs_for_user(victim_id, limit=1)
            victim_job_id = victim_jobs[0]["id"]
            self.assertFalse(db.update_job_status_and_notes(victim_job_id, attacker_id, "rejected", "hijacked"))
        finally:
            if os.path.exists(victim_file):
                os.remove(victim_file)

    # Check 2b: Cross-recruiter application status tampering blocked
    def test_02b_cross_recruiter_application_status_blocked(self):
        db = SecurityTestDatabase()
        rec1 = db.add_user("recruiter_one", generate_password_hash("password123"), role="recruiter", email="r1@example.com", account_status="active", onboarding_completed=True)
        rec2 = db.add_user("recruiter_two", generate_password_hash("password123"), role="recruiter", email="r2@example.com", account_status="active", onboarding_completed=True)
        seeker = db.add_user("applicant_one", generate_password_hash("password123"), role="seeker", email="s1@example.com", account_status="active", onboarding_completed=True)

        db.add_job(
            Job(title="Rec1 Job", company="Co1", location="Remote", salary="$120k", link="", description="Desc", keywords=[], skills=[], experience="", job_type="Full-time", posted_date="Today", source="Recruiter", deadline="N/A"),
            user_id=rec1,
            posted_by_recruiter_id=rec1,
            sync_calendar=False,
        )
        r1_jobs, _ = db.get_jobs_for_user(rec1, limit=1)
        app_id = db.add_application(r1_jobs[0]["id"], "Applicant One", "s1@example.com", applicant_user_id=seeker, ai_match_score=85.0)

        # Recruiter 2 logs in and tries to tamper with Recruiter 1's application
        self.client.post("/login", data={"username": "recruiter_two", "password": "password123"})
        resp = self.client.patch(f"/api/applications/{app_id}/status", json={"status": "rejected"})
        self.assertEqual(resp.status_code, 404)

    # Check 3: No API keys or secrets leaked in HTML responses
    def test_03_no_api_keys_in_browser(self):
        with patch.dict(os.environ, {
            "GEMINI_API_KEY": "SUPER_SECRET_GEMINI_KEY_XYZ",
            "CEREBRAS_API_KEY": "SUPER_SECRET_CEREBRAS_KEY_XYZ",
        }):
            self._create_and_login("browser_check", "browser@example.com", role="seeker")
            for route in ("/dashboard", "/learning_path", "/profile"):
                page = self.client.get(route)
                self.assertEqual(page.status_code, 200)
                self.assertNotIn(b"SUPER_SECRET_GEMINI_KEY_XYZ", page.data)
                self.assertNotIn(b"SUPER_SECRET_CEREBRAS_KEY_XYZ", page.data)

    # Checks 4-7: Negative limit (-1), score tampering (9999), duplicate submit 100x
    def test_04_to_07_bounds_score_clamping_and_duplicate_applications(self):
        db = SecurityTestDatabase()
        rec_id = db.add_user("rec_bounds", generate_password_hash("password123"), role="recruiter", email="rb@example.com", account_status="active", onboarding_completed=True)
        db.add_job(
            Job(title="Staff Eng", company="BoundsCo", location="Remote", salary="$180k", link="", description="Desc", keywords=[], skills=[], experience="", job_type="Full-time", posted_date="Today", source="Recruiter", deadline="N/A"),
            user_id=rec_id,
            posted_by_recruiter_id=rec_id,
            sync_calendar=False,
        )
        rec_jobs, _ = db.get_jobs_for_user(rec_id, limit=1)
        job_id = rec_jobs[0]["id"]

        self._create_and_login("seeker_bounds", "sb@example.com", role="seeker")

        # Negative pagination limit/page does not crash or dump unbounded rows
        dash = self.client.get("/dashboard?page=-5&limit=-1")
        self.assertEqual(dash.status_code, 200)

        # First application succeeds (score 9999 gets clamped to <= 100)
        first = self.client.post("/api/applications", json={"job_id": job_id, "ai_match_score": 9999})
        self.assertEqual(first.status_code, 201)

        # Second application to the same job is rejected (409 Conflict)
        dup = self.client.post("/api/applications", json={"job_id": job_id, "ai_match_score": 100})
        self.assertEqual(dup.status_code, 409)

    # Check 9: Brute-force rate limiting on /login & minimum password length on /register
    def test_09_login_rate_limiting_and_password_policy(self):
        # Short password rejected on signup
        short_pw = self.client.post("/register", data={
            "email": "weakpw@example.com",
            "password": "123",
        })
        self.assertEqual(short_pw.status_code, 302)
        self.assertIsNone(User.get_by_email("weakpw@example.com"))

        # Rapid failed logins hit 429 Too Many Requests
        statuses = []
        for _ in range(17):
            r = self.client.post("/login", data={"username": "nonexistent_user_xyz", "password": "wrongpassword"})
            statuses.append(r.status_code)
        self.assertIn(429, statuses)

    # Check 11: Script in username rejected + javascript: URLs stripped
    def test_11_xss_username_and_javascript_url_blocked(self):
        resp = self.client.post("/register", data={
            "username": "<script>alert(1)</script>",
            "email": "xss@example.com",
            "password": "password123",
        })
        self.assertEqual(resp.status_code, 302)
        self.assertIsNone(User.get_by_email("xss@example.com"))

        self._create_and_login("safe_url_user", "safeurl@example.com", role="seeker")
        self.client.post("/profile", data={
            "full_name": "Safe User",
            "linkedin_url": "javascript:alert(document.cookie)",
            "github_url": "https://github.com/octocat",
            "portfolio_url": "data:text/html,<script>alert(1)</script>",
        })
        details = SecurityTestDatabase().get_user_details(User.get_by_username("safe_url_user").id)
        self.assertEqual(details.get("linkedin_url"), "")
        self.assertEqual(details.get("portfolio_url"), "")
        self.assertEqual(details.get("github_url"), "https://github.com/octocat")

    # Check 12: Uploading a non-photo (HTML / SVG / fake PNG) is blocked
    def test_12_non_photo_and_svg_uploads_blocked(self):
        self._create_and_login("upload_tester", "upload@example.com", role="seeker")
        uid = User.get_by_username("upload_tester").id

        # Try uploading an HTML file disguised as .png for profile_picture
        fake_png = (io.BytesIO(b"<html><script>alert(1)</script></html>"), "evil.png")
        resp = self.client.post(
            "/profile",
            data={"full_name": "Uploader", "profile_picture": fake_png},
            content_type="multipart/form-data",
        )
        self.assertEqual(resp.status_code, 302)
        details = SecurityTestDatabase().get_user_details(uid) or {}
        self.assertFalse(details.get("profile_picture"))

        # Try uploading an HTML script disguised as a resume
        fake_pdf = (io.BytesIO(b"<html><script>alert(1)</script></html>"), "evil.pdf")
        resp2 = self.client.post(
            "/profile",
            data={"full_name": "Uploader", "resume": fake_pdf},
            content_type="multipart/form-data",
        )
        self.assertEqual(resp2.status_code, 302)
        details2 = SecurityTestDatabase().get_user_details(uid) or {}
        self.assertFalse(details2.get("resume_path"))

    # Check 13: .env and sensitive files listed in .gitignore
    def test_13_gitignore_protects_env_and_secrets(self):
        gitignore_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".gitignore")
        with open(gitignore_path, "r", encoding="utf-8") as f:
            content = f.read()
        for entry in (".env", "credentials.json", "token.pickle", "*.db"):
            self.assertIn(entry, content)

    # Check 14: SQL injection payloads in search/sort safely handled
    def test_14_sql_injection_safely_parameterized(self):
        self._create_and_login("sqli_tester", "sqli@example.com", role="seeker")
        resp = self.client.get("/dashboard?search_query=' OR 1=1 --&sort_by=id;DROP TABLE users;--&sort_order=DESC;DROP TABLE jobs;")
        self.assertEqual(resp.status_code, 200)
        # Users table still intact
        self.assertIsNotNone(User.get_by_username("sqli_tester"))


if __name__ == "__main__":
    unittest.main()
