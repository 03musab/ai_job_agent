import hashlib
import html
import json
import os
import re
import sqlite3
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from werkzeug.security import check_password_hash, generate_password_hash

import app as app_module


class ProInviteTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.database_path = os.path.join(self.temp_dir.name, "test_jobs.db")
        # Keep the real class available while routes use the isolated test database.
        self.real_database_class = app_module.JobDatabase
        self.database_patcher = patch(
            "app.JobDatabase",
            side_effect=lambda: self.real_database_class(self.database_path),
        )
        self.database_patcher.start()

        app_module.app.config.update(
            TESTING=True,
            SECRET_KEY="pro-invite-test-secret",
            SESSION_COOKIE_SECURE=False,
        )
        self.client = app_module.app.test_client()
        self.environment = patch.dict(os.environ, {
            "ADMIN_USERNAMES": "admin",
            "PUBLIC_APP_URL": "https://jobsnap.example",
            "MAIL_SERVER": "smtp.example",
            "MAIL_PORT": "587",
            "MAIL_USERNAME": "mailer@example.com",
            "MAIL_PASSWORD": "test-only-password",
        })
        self.environment.start()
        self.real_database_class(self.database_path).add_user(
            "admin", generate_password_hash("admin-password")
        )

    def tearDown(self):
        self.environment.stop()
        self.database_patcher.stop()
        self.temp_dir.cleanup()

    def _login(self, username, password):
        return self.client.post("/login", data={"username": username, "password": password})

    def _csrf_token(self):
        response = self.client.get("/admin/pro-invites")
        self.assertEqual(response.status_code, 200)
        match = re.search(
            r'name="csrf_token" value="([^"]+)"',
            response.get_data(as_text=True),
        )
        self.assertIsNotNone(match)
        return match.group(1)

    def _database_row(self, query, parameters=()):
        connection = sqlite3.connect(self.database_path)
        try:
            return connection.execute(query, parameters).fetchone()
        finally:
            connection.close()

    def test_admin_login_page_routes_authorized_admin_to_invites(self):
        response = self.client.get("/admin/login")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login?admin=1", response.headers["Location"])

        page = self.client.get(response.headers["Location"])
        self.assertEqual(page.status_code, 200)
        self.assertIn(b"Administrator Sign In", page.data)
        self.assertIn(b'name="admin_login" value="1"', page.data)
        self.assertNotIn(b"CREATE ACCOUNT", page.data)

        login = self.client.post("/login?admin=1", data={
            "username": "admin",
            "password": "admin-password",
            "admin_login": "1",
        })
        self.assertEqual(login.status_code, 302)
        self.assertIn("/admin/pro-invites", login.headers["Location"])
        self.assertEqual(self.client.get("/admin/pro-invites").status_code, 200)

    def test_admin_login_rejects_regular_accounts(self):
        self.real_database_class(self.database_path).add_user(
            "ordinary", generate_password_hash("ordinary-password")
        )

        login = self.client.post("/login?admin=1", data={
            "username": "ordinary",
            "password": "ordinary-password",
            "admin_login": "1",
        })

        self.assertEqual(login.status_code, 302)
        self.assertIn("/login?admin=1", login.headers["Location"])
        self.assertIn(b"not authorized for administrator access", self.client.get(login.headers["Location"]).data)
        forbidden = self.client.get("/admin/pro-invites")
        self.assertEqual(forbidden.status_code, 302)
        self.assertIn("/login", forbidden.headers["Location"])

    def test_self_registration_is_free_and_cannot_create_admin_role(self):
        response = self.client.post("/register", data={
            "username": "ordinary",
            "password": "ordinary-password",
            "role": "seeker",
        })
        self.assertEqual(response.status_code, 302)
        user = self._database_row(
            "SELECT role, is_pro, account_status FROM users WHERE username = ?",
            ("ordinary",),
        )
        self.assertEqual(user, ("seeker", 0, "active"))
        self._login("ordinary", "ordinary-password")
        self.assertNotIn(b"Pro member", self.client.get("/profile").data)

        rejected = self.client.post("/register", data={
            "username": "intruder",
            "password": "ordinary-password",
            "role": "admin",
        })
        self.assertEqual(rejected.status_code, 302)
        self.assertIsNone(self._database_row(
            "SELECT id FROM users WHERE username = ?", ("intruder",)
        ))

    def test_admin_invite_sends_one_time_link_and_activates_password(self):
        self._login("admin", "admin-password")
        csrf_token = self._csrf_token()

        preview = self.client.post("/admin/pro-invites", data={
            "action": "preview",
            "csrf_token": csrf_token,
            "invitees": "invite@example.com,Invite Person",
        })
        self.assertEqual(preview.status_code, 200)
        page = preview.get_data(as_text=True)
        encoded_entries = re.search(
            r'name="entries_json" value="([^"]+)"', page
        ).group(1)
        entries = json.loads(html.unescape(encoded_entries))

        with patch("app.smtplib.SMTP") as smtp:
            smtp.return_value.__enter__.return_value = MagicMock()
            response = self.client.post("/admin/pro-invites", data={
                "action": "send",
                "csrf_token": csrf_token,
                "entries_json": json.dumps(entries),
            })
        self.assertEqual(response.status_code, 302)
        smtp.assert_called_once()
        sent_message = smtp.return_value.__enter__.return_value.send_message.call_args.args[0]
        plain_body = sent_message.get_payload()[0].get_payload(decode=True).decode()
        self.assertIn("invite.person", plain_body)
        raw_token = re.search(r"/set-password/([A-Za-z0-9_-]+)", plain_body).group(1)

        invited = self._database_row(
            "SELECT username, password_hash, is_pro, account_status FROM users WHERE email = ?",
            ("invite@example.com",),
        )
        self.assertEqual(invited[0], "invite.person")
        self.assertEqual(invited[2:], (1, "pending"))
        self.assertFalse(check_password_hash(invited[1], ""))
        self.assertNotEqual(
            self._database_row(
                "SELECT token_hash FROM password_setup_tokens WHERE user_id = "
                "(SELECT id FROM users WHERE email = ?)",
                ("invite@example.com",),
            )[0],
            raw_token,
        )

        setup = self.client.post(f"/set-password/{raw_token}", data={
            "password": "a-long-and-safe-password",
            "confirm_password": "a-long-and-safe-password",
        })
        self.assertEqual(setup.status_code, 302)
        activated = self._database_row(
            "SELECT password_hash, is_pro, account_status FROM users WHERE email = ?",
            ("invite@example.com",),
        )
        self.assertTrue(check_password_hash(activated[0], "a-long-and-safe-password"))
        self.assertEqual(activated[1:], (1, "active"))
        self.assertEqual(
            self.client.get(f"/set-password/{raw_token}").status_code,
            404,
        )
        self.client.get("/logout")
        self.client.post("/login", data={
            "username": "invite.person",
            "password": "a-long-and-safe-password",
        })
        self.assertIn(b"Pro member", self.client.get("/profile").data)

    def test_existing_account_is_upgraded_without_changing_password_or_sending_mail(self):
        existing_password_hash = generate_password_hash("existing-password")
        database = self.real_database_class(self.database_path)
        database.add_user("existing", existing_password_hash)
        database.save_user_details(2, {
            "full_name": "Existing Member",
            "email": "existing@example.com",
        })

        self._login("admin", "admin-password")
        csrf_token = self._csrf_token()
        preview = self.client.post("/admin/pro-invites", data={
            "action": "preview",
            "csrf_token": csrf_token,
            "invitees": "existing@example.com,Existing Member",
        })
        encoded_entries = re.search(
            r'name="entries_json" value="([^"]+)"',
            preview.get_data(as_text=True),
        ).group(1)
        entries = json.loads(html.unescape(encoded_entries))
        with patch("app.smtplib.SMTP") as smtp:
            response = self.client.post("/admin/pro-invites", data={
                "action": "send",
                "csrf_token": csrf_token,
                "entries_json": json.dumps(entries),
            })

        self.assertEqual(response.status_code, 302)
        smtp.assert_not_called()
        upgraded = self._database_row(
            "SELECT password_hash, is_pro, account_status FROM users WHERE username = ?",
            ("existing",),
        )
        self.assertEqual(upgraded[0], existing_password_hash)
        self.assertEqual(upgraded[1:], (1, "active"))

    def test_admin_page_is_not_available_to_regular_users(self):
        self.real_database_class(self.database_path).add_user(
            "ordinary", generate_password_hash("ordinary-password")
        )
        self._login("ordinary", "ordinary-password")
        self.assertEqual(self.client.get("/admin/pro-invites").status_code, 403)
        dashboard = self.client.get("/dashboard")
        self.assertEqual(dashboard.status_code, 200)
        self.assertNotIn(b'href="/admin/pro-invites"', dashboard.data)

    def test_admin_panel_navbar_link_visible_for_admin_on_dashboard(self):
        self._login("admin", "admin-password")
        dashboard = self.client.get("/dashboard")
        self.assertEqual(dashboard.status_code, 200)
        html_body = dashboard.get_data(as_text=True)
        self.assertIn("Job Matches", html_body)
        self.assertIn("Outreach Studio", html_body)
        self.assertIn("Skill Gap & Roadmap", html_body)
        self.assertIn("Admin Panel", html_body)
        self.assertIn('href="/admin/pro-invites"', html_body)

    def test_pro_invite_falls_back_to_gmail_token_when_smtp_unset(self):
        self._login("admin", "admin-password")
        csrf_token = self._csrf_token()
        entries = [{"email": "gmailfallback@example.com", "name": "Gmail Fallback"}]

        mock_service = MagicMock()
        fake_creds = MagicMock(valid=True, expired=False, scopes=["https://www.googleapis.com/auth/gmail.send"])

        with patch.dict(os.environ, {"MAIL_SERVER": "", "MAIL_USERNAME": "", "MAIL_PASSWORD": ""}), \
             patch("app.os.path.exists", return_value=True), \
             patch("app.open", unittest.mock.mock_open(read_data=b"token"), create=True), \
             patch("app.pickle.load", return_value=fake_creds), \
             patch("app.build", return_value=mock_service), \
             patch("app.smtplib.SMTP") as smtp:
            response = self.client.post("/admin/pro-invites", data={
                "action": "send",
                "csrf_token": csrf_token,
                "entries_json": json.dumps(entries),
            })

        self.assertEqual(response.status_code, 302)
        smtp.assert_not_called()
        mock_service.users().messages().send.assert_called_once()
        invited = self._database_row(
            "SELECT username, is_pro, account_status FROM users WHERE email = ?",
            ("gmailfallback@example.com",),
        )
        self.assertEqual(invited, ("gmail.fallback", 1, "pending"))

    def test_pro_invite_fails_cleanly_when_neither_smtp_nor_gmail_token_exists(self):
        self._login("admin", "admin-password")
        csrf_token = self._csrf_token()
        entries = [{"email": "nomail@example.com", "name": "No Mail"}]

        with patch.dict(os.environ, {"MAIL_SERVER": "", "MAIL_USERNAME": "", "MAIL_PASSWORD": ""}), \
             patch("app.os.path.exists", return_value=False):
            response = self.client.post("/admin/pro-invites", data={
                "action": "send",
                "csrf_token": csrf_token,
                "entries_json": json.dumps(entries),
            }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"could not be completed", response.data)
        self.assertIsNone(self._database_row(
            "SELECT id FROM users WHERE email = ?", ("nomail@example.com",)
        ))

    def test_pro_invite_email_builds_polished_html_and_escapes_name(self):
        plain_body, html_body = app_module._build_pro_invite_email_bodies(
            "<script>alert(1)</script>",
            "03.musab.1",
            "https://jobsnap.example/set-password/tok123",
        )
        self.assertIn("03.musab.1", plain_body)
        self.assertIn("https://jobsnap.example/set-password/tok123", plain_body)
        self.assertIn("AI JobSnap", html_body)
        self.assertIn("Pro Access", html_body)
        self.assertIn("Set Up Your Password", html_body)
        self.assertIn("03.musab.1", html_body)
        self.assertIn("https://jobsnap.example/set-password/tok123", html_body)
        self.assertNotIn("<script>", html_body)
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", html_body)

        plain_no_name, html_no_name = app_module._build_pro_invite_email_bodies(
            "",
            "03.musab.1",
            "https://jobsnap.example/set-password/tok123",
        )
        self.assertTrue(plain_no_name.startswith("Hello,"))
        self.assertIn("<p style=\"margin: 0 0 16px 0; font-size: 15px; color: #334155;\">\n                    Hello,\n                </p>", html_no_name)

    def test_pro_invite_defaults_link_to_app_jobsnap_domain_when_public_url_unset(self):
        self._login("admin", "admin-password")
        csrf_token = self._csrf_token()
        entries = [{"email": "domaincheck@example.com", "name": "Domain Check"}]

        with patch.dict(os.environ, {"PUBLIC_APP_URL": ""}), \
             patch("app.smtplib.SMTP") as smtp:
            smtp.return_value.__enter__.return_value = MagicMock()
            response = self.client.post("/admin/pro-invites", data={
                "action": "send",
                "csrf_token": csrf_token,
                "entries_json": json.dumps(entries),
            })

        self.assertEqual(response.status_code, 302)
        sent_message = smtp.return_value.__enter__.return_value.send_message.call_args.args[0]
        plain_body = sent_message.get_payload()[0].get_payload(decode=True).decode()
        html_body = sent_message.get_payload()[1].get_payload(decode=True).decode()
        self.assertIn("https://app.jobsnap.me/set-password/", plain_body)
        self.assertIn("https://app.jobsnap.me/set-password/", html_body)
        self.assertNotIn("127.0.0.1", plain_body)
        self.assertNotIn("127.0.0.1", html_body)


if __name__ == "__main__":
    unittest.main()
