import unittest
import os
import sys
import shutil
from unittest.mock import MagicMock, patch
from datetime import datetime

# Add parent directory to path at the beginning to verify local imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import app standardly - assume dependencies are present in venv
from app import app, JobDatabase, Job, User
from extensions import db as extension_db

class TestJobDatabase(JobDatabase):
    """Subclass to force using test DB."""
    def __init__(self, db_path="test_jobs.db"):
        super().__init__(db_path)

class AIJobAgentTestCase(unittest.TestCase):
    def setUp(self):
        """Set up test environment."""
        self.test_db_path = 'test_jobs.db'
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
            
        # Patch JobDatabase in app to use our TestJobDatabase (fixed db path)
        self.db_patcher = patch('app.JobDatabase', side_effect=TestJobDatabase)
        self.db_patcher.start()
        
        # Configure App
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SECRET_KEY'] = 'test-secret-key'
        
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        
        # Initialize Test DB (schema)
        # Verify we are using the test db
        db = TestJobDatabase()
        db.init_db()

    def tearDown(self):
        """Clean up."""
        self.db_patcher.stop()
        self.app_context.pop()
        if os.path.exists(self.test_db_path):
            try:
                os.remove(self.test_db_path)
            except:
                pass

    def test_register_and_login_flow(self):
        """Test full register -> login -> dashboard flow."""
        # 1. Register
        with patch('app._send_email_verification_email') as send_verification:
            resp = self.client.post('/register', data={
                'username': 'tester',
                'password': 'password123',
                'email': 'tester@example.com',
                'confirm_password': 'password123'
            })
            self.assertEqual(resp.status_code, 200)
            self.assertIn(b'Check your email', resp.data)

            pending_user = User.get_by_username('tester')
            self.assertEqual(pending_user.account_status, 'pending')
            first_token = send_verification.call_args.args[1]
            pending_login = self.client.post('/login', data={
                'username': 'tester',
                'password': 'password123',
            })
            self.assertEqual(pending_login.status_code, 200)
            self.assertIn(b'Check your email', pending_login.data)
            verification_token = send_verification.call_args.args[1]
            self.assertNotEqual(first_token, verification_token)
            self.assertIn(
                b'already used',
                self.client.get(f'/confirm-email/{first_token}').data,
            )
            verified = self.client.get(f'/confirm-email/{verification_token}')
            self.assertEqual(verified.status_code, 200)
            self.assertIn(b'Your account is ready', verified.data)
            self.assertEqual(User.get_by_username('tester').account_status, 'active')

        # 2. First login after confirming the email directs to the 4-step onboarding wizard.
        resp_login = self.client.post('/login', data={
            'username': 'tester',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Step 1 of 4', resp_login.data)
        self.assertIn(b'How will you use AI JobSnap?', resp_login.data)

        # 3. Complete the 4-step onboarding as a Job Seeker and land on the dashboard.
        complete = self.client.post('/api/onboarding/complete', json={
            'role': 'seeker',
            'full_name': 'Tester Candidate',
            'target_role': 'Full Stack Engineer',
        })
        self.assertEqual(complete.status_code, 200)
        self.assertEqual(complete.get_json()['redirect_url'], '/dashboard?tour=1')
        dash = self.client.get('/dashboard?tour=1')
        self.assertEqual(dash.status_code, 200)
        self.assertTrue(b'Dashboard' in dash.data or b'Job Application Dashboard' in dash.data or b'Job Matches' in dash.data)
        self.assertIn(b'spotlightTourOverlay', dash.data)
        self.assertIn(b'data-auto-start="true"', dash.data)
        dismiss = self.client.post('/api/onboarding/tour-dismiss')
        self.assertEqual(dismiss.status_code, 200)

    def test_first_email_login_creates_account_and_requires_confirmation(self):
        with patch('app._send_email_verification_email') as send_verification:
            response = self.client.post('/login', data={
                'username': 'first.timer@example.com',
                'password': 'password123',
            })
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Check your email', response.data)

            user = User.get_by_email('first.timer@example.com')
            self.assertIsNotNone(user)
            self.assertEqual(user.role, 'seeker')
            self.assertEqual(user.account_status, 'pending')
            self.assertFalse(user.onboarding_completed)

            confirmation_token = send_verification.call_args.args[1]
            verified = self.client.get(f'/confirm-email/{confirmation_token}')
            self.assertEqual(verified.status_code, 200)
            self.assertEqual(User.get_by_email('first.timer@example.com').account_status, 'active')

        signed_in = self.client.post('/login', data={
            'username': 'first.timer@example.com',
            'password': 'password123',
        }, follow_redirects=True)
        self.assertIn(b'Step 1 of 4', signed_in.data)

    def test_google_auth_creates_verified_user_and_signs_in(self):
        flow = MagicMock()
        flow.credentials.id_token = 'verified-id-token'
        with patch.dict(os.environ, {
            'GOOGLE_CLIENT_ID': 'test-client-id',
            'GOOGLE_CLIENT_SECRET': 'test-client-secret',
        }), patch('app._google_oauth_flow', return_value=flow), patch(
            'app.id_token.verify_oauth2_token',
            return_value={'email': 'new.user@example.com', 'email_verified': True},
        ):
            with self.client.session_transaction() as browser_session:
                browser_session['google_oauth_state'] = 'expected-state'
                browser_session['google_oauth_mode'] = 'register'
                browser_session['google_oauth_role'] = 'recruiter'

            response = self.client.get(
                '/auth/google/callback?state=expected-state&code=test-code'
            )

        self.assertEqual(response.status_code, 302)
        self.assertIn('/recruiter', response.headers['Location'])
        created_user = User.get_by_email('new.user@example.com')
        self.assertIsNotNone(created_user)
        self.assertEqual(created_user.role, 'recruiter')
        self.assertEqual(created_user.account_status, 'active')

    def test_google_signin_activates_pending_beta_user_after_password_setup(self):
        database = TestJobDatabase()
        database.add_user(
            'beta_user',
            'temporary-password-hash',
            email='beta@example.com',
            is_pro=True,
            account_status='pending',
        )
        flow = MagicMock()
        flow.credentials.id_token = 'verified-id-token'

        with patch.dict(os.environ, {'GOOGLE_CLIENT_ID': 'test-client-id'}), patch(
            'app._google_oauth_flow', return_value=flow
        ), patch(
            'app.id_token.verify_oauth2_token',
            return_value={'email': 'beta@example.com', 'email_verified': True},
        ):
            with self.client.session_transaction() as browser_session:
                browser_session['google_oauth_state'] = 'first-google-state'
                browser_session['google_oauth_mode'] = 'login'

            first_signin = self.client.get(
                '/auth/google/callback?state=first-google-state&code=test-code'
            )
            self.assertEqual(first_signin.status_code, 302)
            self.assertIn('/set-password/', first_signin.headers['Location'])

            password_setup = self.client.post(first_signin.headers['Location'], data={
                'password': 'a-long-and-safe-password',
                'confirm_password': 'a-long-and-safe-password',
            })
            self.assertEqual(password_setup.status_code, 302)
            activated_user = User.get_by_email('beta@example.com')
            self.assertEqual(activated_user.account_status, 'active')
            self.assertTrue(activated_user.is_pro)
            self.assertNotEqual(activated_user.password_hash, 'temporary-password-hash')

            with self.client.session_transaction() as browser_session:
                browser_session['google_oauth_state'] = 'second-google-state'
                browser_session['google_oauth_mode'] = 'login'

            later_signin = self.client.get(
                '/auth/google/callback?state=second-google-state&code=test-code'
            )

        self.assertEqual(later_signin.status_code, 302)
        self.assertIn('/dashboard', later_signin.headers['Location'])

    def test_google_signup_starts_oauth_with_selected_role(self):
        with patch.dict(os.environ, {
            'GOOGLE_CLIENT_ID': 'test-client-id',
            'GOOGLE_CLIENT_SECRET': 'test-client-secret',
            'GOOGLE_OAUTH_REDIRECT_URI': 'https://jobsnap.test/auth/google/callback',
        }):
            response = self.client.get('/auth/google?mode=register&role=recruiter')

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.headers['Location'].startswith('https://accounts.google.com/'))
        self.assertIn('userinfo.email', response.headers['Location'])
        with self.client.session_transaction() as browser_session:
            self.assertEqual(browser_session['google_oauth_mode'], 'register')
            self.assertEqual(browser_session['google_oauth_role'], 'recruiter')
            self.assertTrue(browser_session['google_oauth_state'])

    def test_google_oauth_scope_warning_does_not_return_500(self):
        flow = MagicMock()
        flow.fetch_token.side_effect = Warning('OAuth scope changed')
        with patch('app._google_oauth_flow', return_value=flow):
            with self.client.session_transaction() as browser_session:
                browser_session['google_oauth_state'] = 'expected-state'
                browser_session['google_oauth_mode'] = 'register'

            response = self.client.get(
                '/auth/google/callback?state=expected-state&code=test-code'
            )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.headers['Location'].endswith('/login#register'))

    def test_google_auth_rejects_mismatched_state(self):
        with self.client.session_transaction() as browser_session:
            browser_session['google_oauth_state'] = 'expected-state'

        response = self.client.get('/auth/google/callback?state=wrong-state&code=test-code')

        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.headers['Location'])
        self.assertIsNone(User.get_by_email('new.user@example.com'))

    def test_google_signin_creates_unknown_account(self):
        flow = MagicMock()
        flow.credentials.id_token = 'verified-id-token'
        with patch.dict(os.environ, {'GOOGLE_CLIENT_ID': 'test-client-id'}), patch(
            'app._google_oauth_flow', return_value=flow
        ), patch(
            'app.id_token.verify_oauth2_token',
            return_value={'email': 'unknown@example.com', 'email_verified': True},
        ):
            with self.client.session_transaction() as browser_session:
                browser_session['google_oauth_state'] = 'expected-state'
                browser_session['google_oauth_mode'] = 'login'
                browser_session['google_oauth_role'] = 'recruiter'

            response = self.client.get(
                '/auth/google/callback?state=expected-state&code=test-code'
            )

        self.assertEqual(response.status_code, 302)
        self.assertIn('/recruiter', response.headers['Location'])
        created_user = User.get_by_email('unknown@example.com')
        self.assertIsNotNone(created_user)
        self.assertEqual(created_user.role, 'recruiter')
        self.assertEqual(created_user.account_status, 'active')

    def test_google_signin_starts_oauth_with_selected_role(self):
        with patch.dict(os.environ, {
            'GOOGLE_CLIENT_ID': 'test-client-id',
            'GOOGLE_CLIENT_SECRET': 'test-client-secret',
            'GOOGLE_OAUTH_REDIRECT_URI': 'https://jobsnap.test/auth/google/callback',
        }):
            page = self.client.get('/login')
            self.assertNotIn(b'id="googleLoginRole"', page.data)
            self.assertNotIn(b'id="googleRoleMenu"', page.data)
            self.assertNotIn(b'id="signupRoleMenu"', page.data)
            self.assertIn(b'id="googleLoginLink"', page.data)
            self.assertIn(b'id="googleSignupLink"', page.data)
            self.assertNotIn(b'Administrator sign in', page.data)
            response = self.client.get('/auth/google?mode=login')

        self.assertEqual(response.status_code, 302)
        with self.client.session_transaction() as browser_session:
            self.assertEqual(browser_session['google_oauth_mode'], 'login')
            self.assertIsNone(browser_session['google_oauth_role'])

    def test_first_time_google_user_completes_four_step_onboarding_as_recruiter(self):
        flow = MagicMock()
        flow.credentials.id_token = 'verified-id-token'
        with patch.dict(os.environ, {'GOOGLE_CLIENT_ID': 'test-client-id'}), patch(
            'app._google_oauth_flow', return_value=flow
        ), patch(
            'app.id_token.verify_oauth2_token',
            return_value={'email': 'new.recruiter@example.com', 'email_verified': True},
        ):
            with self.client.session_transaction() as browser_session:
                browser_session['google_oauth_state'] = 'expected-state'
                browser_session['google_oauth_mode'] = 'login'
                browser_session['google_oauth_role'] = None

            response = self.client.get(
                '/auth/google/callback?state=expected-state&code=test-code'
            )

        self.assertEqual(response.status_code, 302)
        self.assertIn('/onboarding', response.headers['Location'])
        created_user = User.get_by_email('new.recruiter@example.com')
        self.assertIsNotNone(created_user)
        self.assertFalse(created_user.onboarding_completed)

        complete = self.client.post('/api/onboarding/complete', json={
            'role': 'recruiter',
            'company_name': 'Apex Hiring AI',
            'industry': 'Artificial Intelligence',
        })
        self.assertEqual(complete.status_code, 200)
        self.assertEqual(complete.get_json()['redirect_url'], '/recruiter/dashboard?tour=1')

        rec_dash = self.client.get('/recruiter/dashboard?tour=1')
        self.assertEqual(rec_dash.status_code, 200)
        self.assertIn(b'spotlightTourOverlay', rec_dash.data)
        self.assertIn(b'data-auto-start="true"', rec_dash.data)

        updated_user = User.get_by_email('new.recruiter@example.com')
        self.assertEqual(updated_user.role, 'recruiter')
        self.assertTrue(updated_user.onboarding_completed)

    def test_google_signin_updates_existing_seeker_to_recruiter_when_recruiter_selected(self):
        database = TestJobDatabase()
        database.add_user(
            'existing_candidate',
            'temporary-hash',
            role='seeker',
            email='existing.candidate@example.com',
            account_status='active',
        )
        existing_user = User.get_by_email('existing.candidate@example.com')
        self.assertIsNotNone(existing_user)
        self.assertEqual(existing_user.role, 'seeker')

        flow = MagicMock()
        flow.credentials.id_token = 'verified-id-token'
        with patch.dict(os.environ, {'GOOGLE_CLIENT_ID': 'test-client-id'}), patch(
            'app._google_oauth_flow', return_value=flow
        ), patch(
            'app.id_token.verify_oauth2_token',
            return_value={'email': 'existing.candidate@example.com', 'email_verified': True},
        ):
            with self.client.session_transaction() as browser_session:
                browser_session['google_oauth_state'] = 'expected-state'
                browser_session['google_oauth_mode'] = 'login'
                browser_session['google_oauth_role'] = 'recruiter'

            response = self.client.get(
                '/auth/google/callback?state=expected-state&code=test-code'
            )

        self.assertEqual(response.status_code, 302)
        self.assertIn('/recruiter', response.headers['Location'])
        refreshed_user = User.get_by_email('existing.candidate@example.com')
        self.assertIsNotNone(refreshed_user)
        self.assertEqual(refreshed_user.role, 'recruiter')

    def test_google_signin_preserves_existing_user_role_when_role_not_selected(self):
        database = TestJobDatabase()
        database.add_user(
            'existing_recruiter',
            'temporary-hash',
            role='recruiter',
            email='existing.recruiter@example.com',
            account_status='active',
        )
        flow = MagicMock()
        flow.credentials.id_token = 'verified-id-token'
        with patch.dict(os.environ, {'GOOGLE_CLIENT_ID': 'test-client-id'}), patch(
            'app._google_oauth_flow', return_value=flow
        ), patch(
            'app.id_token.verify_oauth2_token',
            return_value={'email': 'existing.recruiter@example.com', 'email_verified': True},
        ):
            with self.client.session_transaction() as browser_session:
                browser_session['google_oauth_state'] = 'expected-state'
                browser_session['google_oauth_mode'] = 'login'
                browser_session['google_oauth_role'] = None

            response = self.client.get(
                '/auth/google/callback?state=expected-state&code=test-code'
            )

        self.assertEqual(response.status_code, 302)
        self.assertIn('/recruiter', response.headers['Location'])
        refreshed_user = User.get_by_email('existing.recruiter@example.com')
        self.assertIsNotNone(refreshed_user)
        self.assertEqual(refreshed_user.role, 'recruiter')

    def test_job_persistence(self):
        """Test adding a job via code and retrieving it."""
        db = TestJobDatabase()
        # Create user manually since we mocked the app flow
        db.add_user('tester2', 'hashed_pw')
        
        # Providing ALL required positional args for the Job dataclass
        job = Job(
            title="Test Role",
            company="Test Co", 
            location="Remote",
            salary="100k",
            link="http://test.com",
            description="Test desc",
            keywords=["python", "flask"],
            skills=["Python", "Flask"],
            experience="3 years",
            job_type="Contract",
            posted_date=datetime.now().strftime('%Y-%m-%d'),
            source="Manual",
            deadline=""
        )
        # Using ID 1 because add_user likely creates ID 1 in empty DB
        db.add_job(job, user_id=1)
        
        jobs, _ = db.get_jobs_for_user(1)
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0]['title'], "Test Role")

    def test_job_deletion(self):
        """Test deleting a job."""
        db = TestJobDatabase()
        db.add_user('tester3', 'hashed_pw')
        
        # User ID here is 1 because new DB instance/file for each test?
        # Wait, setUp removes db file. Yes.
        
        job = Job(
            title="Delete Me",
            company="Test Co", 
            location="Remote",
            salary="100k",
            link="http://test.com",
            description="Test desc",
            keywords=[],
            skills=[],
            experience="1",
            job_type="Contract",
            posted_date=datetime.now().strftime('%Y-%m-%d'),
            source="Manual",
            deadline=""
        )
        db.add_job(job, user_id=1)
        
        # Get the job ID
        jobs, _ = db.get_jobs_for_user(1)
        self.assertEqual(len(jobs), 1)
        job_id = jobs[0]['id']
        
        # Delete
        success = db.delete_job(job_id, user_id=1)
        self.assertTrue(success)
        
        # Verify gone
        jobs_after, _ = db.get_jobs_for_user(1)
        self.assertEqual(len(jobs_after), 0)

    def test_user_job_isolation_and_demo_fallback(self):
        """Users with own scraped jobs do not see user 15 demo jobs; brand-new users get demo fallback."""
        db = TestJobDatabase()
        demo_id = db.add_user('demo_owner', 'hashed_pw', email='demo@example.com')
        # Force a row with user_id = 15 to simulate production demo seed jobs
        from database import connect_database
        conn = connect_database(self.test_db_path)
        conn.execute(
            """INSERT INTO jobs (job_hash, title, company, location, link, source, user_id, status)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            ('demo-hash-15', 'Demo Shared Role', 'DemoCo', 'Remote', 'https://example.com/demo15', 'Demo', 15, 'new'),
        )
        conn.commit()
        conn.close()
        self.assertIsNotNone(demo_id)

        user_a = db.add_user('seeker_a', 'hashed_pw', email='seekera@example.com')
        user_b = db.add_user('seeker_b', 'hashed_pw', email='seekerb@example.com')

        # Brand-new user with 0 own jobs receives demo seed fallback
        fallback_jobs, fallback_total = db.get_jobs_for_user(user_a)
        self.assertEqual(fallback_total, 1)
        self.assertEqual(fallback_jobs[0]['title'], 'Demo Shared Role')

        # Once user_a scrapes their own job, user_id=15 demo jobs are excluded
        job_a = Job(
            title='Flutter Mobile Engineer',
            company='AppLabs',
            location='Remote',
            salary='120k',
            link='https://example.com/flutter',
            description='Dart & Flutter role',
            keywords=['flutter'],
            skills=['Flutter', 'Dart'],
            experience='2 years',
            job_type='Full-time',
            posted_date=datetime.now().strftime('%Y-%m-%d'),
            source='Indeed',
            deadline='',
        )
        db.add_job(job_a, user_id=user_a)

        jobs_a, total_a = db.get_jobs_for_user(user_a)
        self.assertEqual(total_a, 1)
        self.assertEqual([j['title'] for j in jobs_a], ['Flutter Mobile Engineer'])
        counts_a = db.get_job_status_counts(user_a)
        self.assertEqual(counts_a['new'], 1)

        # User B gets their own scraped jobs independently without seeing User A or User 15
        job_b = Job(
            title='Rust Systems Developer',
            company='CoreSystems',
            location='Berlin',
            salary='140k',
            link='https://example.com/rust',
            description='Low-level Rust services',
            keywords=['rust'],
            skills=['Rust'],
            experience='4 years',
            job_type='Full-time',
            posted_date=datetime.now().strftime('%Y-%m-%d'),
            source='Indeed',
            deadline='',
        )
        db.add_job(job_b, user_id=user_b)

        jobs_b, total_b = db.get_jobs_for_user(user_b)
        self.assertEqual(total_b, 1)
        self.assertEqual([j['title'] for j in jobs_b], ['Rust Systems Developer'])

    def test_background_thread_fallback_tracks_progress_without_redis(self):
        """run_job_hunt_task and scrape_contacts_task succeed via local thread proxy even when Redis is unreachable."""
        import time
        from app import _dispatch_background_task, run_job_hunt_task, scrape_contacts_task, _get_local_task_result

        class _FakeHunter:
            def __init__(self, user_id, search_terms, location, experience, job_type, task=None, scan_mode='fast'):
                self.task = task

            def run(self):
                # Simulates real JobHunter calling update_state immediately at 5% and 90%
                self.task.update_state(state='PROGRESS', meta={'status': 'Initializing job hunt...', 'progress': 5, 'milestone': 'Initializing'})
                self.task.update_state(state='PROGRESS', meta={'status': 'Saved 2 new jobs', 'progress': 92, 'milestone': 'Saving'})

        with patch.object(run_job_hunt_task, 'delay', side_effect=ConnectionError('Redis down')), \
             patch('app.JobHunter', _FakeHunter):
            handle = _dispatch_background_task(run_job_hunt_task, 1, ['flutter'], 'Remote', '', '', 'fast')
            for _ in range(50):
                snap = _get_local_task_result(handle.id)
                if snap and snap['state'] in ('SUCCESS', 'FAILURE'):
                    break
                time.sleep(0.02)

            final_snap = _get_local_task_result(handle.id)
            self.assertIsNotNone(final_snap)
            self.assertEqual(final_snap['state'], 'SUCCESS')
            self.assertEqual(final_snap['info']['progress'], 100)

        with patch.object(scrape_contacts_task, 'delay', side_effect=ConnectionError('Redis down')), \
             patch('app.search_csv_repository_for_contacts', return_value=3):
            contact_handle = _dispatch_background_task(scrape_contacts_task, 1, ['Recruiter'])
            for _ in range(50):
                snap = _get_local_task_result(contact_handle.id)
                if snap and snap['state'] in ('SUCCESS', 'FAILURE'):
                    break
                time.sleep(0.02)

            contact_snap = _get_local_task_result(contact_handle.id)
            self.assertIsNotNone(contact_snap)
            self.assertEqual(contact_snap['state'], 'SUCCESS')
            self.assertEqual(contact_snap['info']['added_count'], 3)

    def test_postgres_statement_translates_like_to_ilike(self):
        """database._translate_statement converts SQLite LIKE to PostgreSQL case-insensitive ILIKE outside quotes."""
        from database import _translate_statement

        sql = "SELECT * FROM jobs WHERE title LIKE ? AND notes NOT LIKE ? AND tag = 'like_this'"
        translated = _translate_statement(sql)
        self.assertIn("title ILIKE %s", translated)
        self.assertIn("notes NOT ILIKE %s", translated)
        self.assertIn("'like_this'", translated)

if __name__ == '__main__':
    unittest.main()
