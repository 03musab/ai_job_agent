"""
Automated tests for progressive per-user scraper cooldown (15s -> 30s -> 30s -> 30s...),
search scan reliability, and Saved Preset Play enforcement during cooldown.
"""

import os
import sys
import time
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from flask import g
from werkzeug.security import generate_password_hash

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import app as app_module
from app import app, JobDatabase, _run_job_hunt_impl, _LocalTaskContext


class CooldownTestDatabase(JobDatabase):
    def __init__(self, db_path="test_scraper_cooldown.db"):
        super().__init__(db_path)


class ScraperCooldownTestCase(unittest.TestCase):
    def setUp(self):
        self.test_db_path = "test_scraper_cooldown.db"
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)

        self.db_patcher = patch("app.JobDatabase", side_effect=CooldownTestDatabase)
        self.db_patcher.start()

        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        app.config["SECRET_KEY"] = "test-cooldown-secret-key"
        app.config["DISABLE_RATE_LIMIT"] = True

        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()

        db = CooldownTestDatabase()
        db.init_db()

    def tearDown(self):
        self.db_patcher.stop()
        self.app_context.pop()
        if os.path.exists(self.test_db_path):
            try:
                os.remove(self.test_db_path)
            except OSError:
                pass

    def _create_and_login(self, username, email, password="password123"):
        db = CooldownTestDatabase()
        uid = db.add_user(
            username,
            generate_password_hash(password),
            role="seeker",
            email=email,
            account_status="active",
            onboarding_completed=True,
        )
        g.pop("_login_user", None)
        self.client.get("/logout")
        g.pop("_login_user", None)
        resp = self.client.post("/login", data={"username": username, "password": password})
        self.assertIn(resp.status_code, (200, 302))
        g.pop("_login_user", None)
        return uid

    def test_01_progressive_cooldown_schedule_15_30_30_30(self):
        """1st scrape completion triggers 15s cooldown; 2nd, 3rd, 4th each trigger 30s."""
        uid = self._create_and_login("cd_user_1", "cd1@example.com")
        db = CooldownTestDatabase()

        # Before any scrape: ready, next cooldown will be 15s
        initial = db.get_scrape_cooldown_status(uid, now=1000.0)
        self.assertTrue(initial["can_scrape"])
        self.assertEqual(initial["cooldown_remaining"], 0)
        self.assertEqual(initial["completed_count"], 0)
        self.assertEqual(initial["next_cooldown_seconds"], 15)

        # 1st completion -> 15s
        c1 = db.record_scrape_completion(uid, now=1000.0)
        self.assertEqual(c1["completed_count"], 1)
        self.assertEqual(c1["cooldown_seconds"], 15)
        self.assertEqual(c1["cooldown_remaining"], 15)
        self.assertEqual(c1["next_cooldown_seconds"], 30)

        # At t=1010s -> still 5s remaining
        mid1 = db.get_scrape_cooldown_status(uid, now=1010.0)
        self.assertFalse(mid1["can_scrape"])
        self.assertEqual(mid1["cooldown_remaining"], 5)

        # At t=1016s -> unlocked
        after1 = db.get_scrape_cooldown_status(uid, now=1016.0)
        self.assertTrue(after1["can_scrape"])
        self.assertEqual(after1["cooldown_remaining"], 0)

        # 2nd, 3rd, 4th completions -> 30s each
        for expected_count, base_t in ((2, 1020.0), (3, 1060.0), (4, 1100.0)):
            c = db.record_scrape_completion(uid, now=base_t)
            self.assertEqual(c["completed_count"], expected_count)
            self.assertEqual(c["cooldown_seconds"], 30)
            self.assertEqual(c["cooldown_remaining"], 30)
            self.assertEqual(c["next_cooldown_seconds"], 30)

            blocked = db.get_scrape_cooldown_status(uid, now=base_t + 20.0)
            self.assertFalse(blocked["can_scrape"])
            self.assertEqual(blocked["cooldown_remaining"], 10)

            unlocked = db.get_scrape_cooldown_status(uid, now=base_t + 31.0)
            self.assertTrue(unlocked["can_scrape"])
            self.assertEqual(unlocked["cooldown_remaining"], 0)

    def test_02_start_scrape_search_jobs_and_saved_preset_blocked_during_cooldown(self):
        """/start_scrape, /search_jobs, and /apply_profile/<id> all return 429 during cooldown."""
        uid = self._create_and_login("cd_user_2", "cd2@example.com")
        db = CooldownTestDatabase()
        profile_id = db.save_search_profile(uid, "Python Remote", "Python, Flask", "Remote", "2-5 yrs", "Full-time")
        self.assertIsNotNone(profile_id)

        # Before cooldown: saved preset play works (200) and returns profile
        preset_ok = self.client.post(f"/apply_profile/{profile_id}", headers={"Accept": "application/json"})
        self.assertEqual(preset_ok.status_code, 200)
        preset_data = preset_ok.get_json()
        self.assertTrue(preset_data["success"])
        self.assertEqual(preset_data["profile"]["search_terms"], "Python, Flask")

        # Simulate completing 1st scrape via _run_job_hunt_impl (mocking JobHunter.run)
        with patch("app.JobHunter.run", return_value={"new_jobs_count": 3, "total_found": 5}):
            res = _run_job_hunt_impl(
                _LocalTaskContext("task-1"),
                uid,
                ["Python"],
                "Remote",
                "",
                "",
                "fast",
            )
        self.assertEqual(res["cooldown_seconds"], 15)
        self.assertEqual(res["completed_count"], 1)

        # /api/scrape_cooldown reports active 15s cooldown
        cd_api = self.client.get("/api/scrape_cooldown")
        self.assertEqual(cd_api.status_code, 200)
        cd_json = cd_api.get_json()
        self.assertFalse(cd_json["can_scrape"])
        self.assertGreater(cd_json["cooldown_remaining"], 0)
        self.assertLessEqual(cd_json["cooldown_remaining"], 15)

        # /start_scrape blocked with 429
        r_start = self.client.post("/start_scrape", data={"search_terms": "Python", "scan_mode": "fast"})
        self.assertEqual(r_start.status_code, 429)
        self.assertGreater(r_start.get_json()["cooldown_remaining"], 0)

        # /search_jobs blocked with 429
        r_legacy = self.client.post("/search_jobs", data={"search_terms": "Python"})
        self.assertEqual(r_legacy.status_code, 429)
        self.assertGreater(r_legacy.get_json()["cooldown_remaining"], 0)

        # Saved preset Play (/apply_profile/<id>) blocked with 429 during cooldown!
        r_preset = self.client.post(f"/apply_profile/{profile_id}", headers={"Accept": "application/json"})
        self.assertEqual(r_preset.status_code, 429)
        self.assertFalse(r_preset.get_json()["success"])
        self.assertGreater(r_preset.get_json()["cooldown_remaining"], 0)

        # Fast-forward expiry in DB so cooldown is over
        db.record_scrape_completion(uid, now=time.time() - 40.0)
        # Preset Play unlocks again (200) and /start_scrape works cleanly
        r_preset_after = self.client.post(f"/apply_profile/{profile_id}", headers={"Accept": "application/json"})
        self.assertEqual(r_preset_after.status_code, 200)

        with patch("app._dispatch_background_task", return_value=SimpleNamespace(id="mock-task-2")):
            r_start_after = self.client.post(
                "/start_scrape",
                data={"search_terms": "Python, Flask", "location": "Remote", "scan_mode": "deep"},
            )
        self.assertEqual(r_start_after.status_code, 200)
        self.assertEqual(r_start_after.get_json()["task_id"], "mock-task-2")
        self.assertEqual(r_start_after.get_json()["scan_mode"], "deep")

    def test_03_active_scan_blocks_concurrent_start_and_releases_on_error(self):
        """Concurrent scrape/preset blocked while scan is active; crash releases lock cleanly."""
        uid = self._create_and_login("cd_user_3", "cd3@example.com")
        db = CooldownTestDatabase()
        profile_id = db.save_search_profile(uid, "React Jobs", "React", "Remote", "", "")

        # Acquire active slot via /start_scrape
        with patch("app._dispatch_background_task", return_value=SimpleNamespace(id="live-task-1")):
            r1 = self.client.post("/start_scrape", data={"search_terms": "React", "scan_mode": "fast"})
        self.assertEqual(r1.status_code, 200)

        # Second concurrent /start_scrape and preset Play must both be blocked with 429
        r2 = self.client.post("/start_scrape", data={"search_terms": "Node", "scan_mode": "fast"})
        self.assertEqual(r2.status_code, 429)
        self.assertTrue(r2.get_json()["active"])

        r_preset = self.client.post(f"/apply_profile/{profile_id}")
        self.assertEqual(r_preset.status_code, 429)
        self.assertTrue(r_preset.get_json()["active"])

        # Simulated unexpected crash in _run_job_hunt_impl releases the active lock
        with patch("app.JobHunter.run", side_effect=RuntimeError("network blip")):
            with self.assertRaises(RuntimeError):
                _run_job_hunt_impl(_LocalTaskContext("live-task-1"), uid, ["React"], "Remote", "", "", "fast")

        # User is NOT permanently stuck
        status_after_err = db.get_scrape_cooldown_status(uid)
        self.assertTrue(status_after_err["can_scrape"])
        self.assertFalse(status_after_err["active"])

    def test_04_per_user_cooldown_isolation(self):
        """User A's cooldown never blocks User B from scraping or playing saved presets."""
        uid_a = self._create_and_login("cd_user_a", "cda@example.com")
        db = CooldownTestDatabase()
        db.record_scrape_completion(uid_a)  # User A now on 15s cooldown

        # Login as User B
        uid_b = self._create_and_login("cd_user_b", "cdb@example.com")
        prof_b = db.save_search_profile(uid_b, "Go Backend", "Golang", "Remote", "", "")

        self.assertFalse(db.get_scrape_cooldown_status(uid_a)["can_scrape"])
        self.assertTrue(db.get_scrape_cooldown_status(uid_b)["can_scrape"])

        r_preset_b = self.client.post(f"/apply_profile/{prof_b}")
        self.assertEqual(r_preset_b.status_code, 200)

        with patch("app._dispatch_background_task", return_value=SimpleNamespace(id="user-b-task")):
            r_start_b = self.client.post("/start_scrape", data={"search_terms": "Golang", "scan_mode": "fast"})
        self.assertEqual(r_start_b.status_code, 200)


if __name__ == "__main__":
    unittest.main()
