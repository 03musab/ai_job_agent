import unittest
import os
import sys
import shutil
from unittest.mock import MagicMock, patch
from datetime import datetime

# Add parent directory to path at the beginning to verify local imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import app standardly - assume dependencies are present in venv
from app import app, JobDatabase, Job
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
        resp = self.client.post('/register', data={
            'username': 'tester',
            'password': 'password123',
            'confirm_password': 'password123'
        }, follow_redirects=True)
        
        # Should redirect to Login
        self.assertTrue(b'Login' in resp.data or b'Sign In' in resp.data, "Registration did not redirect to login.")
        
        # 2. Login
        resp_login = self.client.post('/login', data={
            'username': 'tester',
            'password': 'password123'
        }, follow_redirects=True)
        
        self.assertTrue(b'Dashboard' in resp_login.data or b'Job Application Dashboard' in resp_login.data, 
                        "Login failed.")

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

if __name__ == '__main__':
    unittest.main()
