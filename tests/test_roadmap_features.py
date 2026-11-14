import unittest
import os
import sys
import json
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, JobDatabase
from learning_models import LearningPath, LearningModule, UserLearningProgress
from extensions import db as extension_db

class TestRoadmapDatabase(JobDatabase):
    def __init__(self, db_path="test_roadmap_jobs.db"):
        super().__init__(db_path)

class RoadmapFeatureTestCase(unittest.TestCase):
    def setUp(self):
        self.test_db_path = 'test_roadmap_jobs.db'
        if os.path.exists(self.test_db_path):
            try:
                os.remove(self.test_db_path)
            except:
                pass

        self.db_patcher = patch('app.JobDatabase', side_effect=TestRoadmapDatabase)
        self.db_patcher.start()

        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SECRET_KEY'] = 'test-roadmap-secret'
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_roadmap_jobs.db'

        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()

        db = TestRoadmapDatabase()
        db.init_db()
        extension_db.create_all()

    def tearDown(self):
        self.db_patcher.stop()
        self.app_context.pop()
        if os.path.exists(self.test_db_path):
            try:
                os.remove(self.test_db_path)
            except:
                pass

    def _login_user(self, username="roadmap_user"):
        with patch('app._send_email_verification_email') as send_verification:
            self.client.post('/register', data={
                'username': username,
                'password': 'password123',
                'email': f'{username}@example.com',
                'role': 'seeker'
            }, follow_redirects=True)
            verification_token = send_verification.call_args.args[1]
        self.client.get(f'/confirm-email/{verification_token}')

        resp = self.client.post('/login', data={
            'username': username,
            'password': 'password123'
        }, follow_redirects=True)
        return resp

    def test_learning_path_unauthenticated_redirects(self):
        resp = self.client.get('/learning_path')
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/login', resp.headers.get('Location', ''))

    def test_learning_path_authenticated_renders(self):
        self._login_user("learner_1")
        resp = self.client.get('/learning_path')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Skill Gap & Roadmap Engine', resp.data)
        self.assertIn(b'Save this learning plan?', resp.data)

    def test_save_and_retrieve_roadmap(self):
        self._login_user("learner_2")

        sample_roadmap = {
            "total_weeks": 2,
            "weekly_breakdown": [
                {
                    "week_number": 1,
                    "focus_topics": [{"title": "Docker basics", "completed": True}],
                    "mini_project": {"title": "Containerize microservice", "completed": True}
                },
                {
                    "week_number": 2,
                    "focus_topics": [{"title": "Kubernetes pods", "completed": False}],
                    "mini_project": {"title": "Deploy to minikube", "completed": False}
                }
            ]
        }

        # 1. Save new roadmap
        save_resp = self.client.post('/learning-path/save', json={
            "target_role": "DevOps Engineer",
            "total_weeks": 2,
            "roadmap_data": sample_roadmap,
            "path_id": None,
            "progress": 50
        })
        self.assertEqual(save_resp.status_code, 200)
        save_data = save_resp.get_json()
        self.assertTrue(save_data.get('success'))
        path_id = save_data.get('path_id')
        self.assertIsNotNone(path_id)

        # 2. Retrieve user's saved paths
        list_resp = self.client.get('/learning-paths')
        self.assertEqual(list_resp.status_code, 200)
        paths_list = list_resp.get_json()
        self.assertTrue(len(paths_list) >= 1)
        self.assertEqual(paths_list[0]['target_role'], "DevOps Engineer")

        # 3. Retrieve single path details
        detail_resp = self.client.get(f'/learning-path/{path_id}')
        self.assertEqual(detail_resp.status_code, 200)
        detail_data = detail_resp.get_json()
        self.assertEqual(detail_data['target_role'], "DevOps Engineer")
        self.assertEqual(len(detail_data['modules']), 2)

if __name__ == '__main__':
    unittest.main()
