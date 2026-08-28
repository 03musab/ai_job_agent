import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# Add project root to sys.path
sys.path.append(r'c:\Users\musab\Desktop\ai_job_agent')

from ai_utils import _extract_json_from_text, safe_ai_request

class TestAIUtils(unittest.TestCase):
    def test_extract_json_direct(self):
        text = '{"status": "success", "readiness_score": 85}'
        result = _extract_json_from_text(text)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["readiness_score"], 85)

    def test_extract_json_markdown_fences(self):
        text = '''Here is your analysis:
```json
{
    "strong_skills": ["Python", "Flask"],
    "missing_skills": ["Docker"]
}
```
Hope this helps!'''
        result = _extract_json_from_text(text)
        self.assertIn("Python", result["strong_skills"])
        self.assertIn("Docker", result["missing_skills"])

    @patch('google.generativeai.GenerativeModel')
    @patch.dict(os.environ, {'GEMINI_API_KEY': 'mock-gemini-key'})
    def test_safe_ai_request_gemini(self, mock_gen_model):
        mock_response = MagicMock()
        mock_response.text = '{"content": "AI generated skill gap response"}'
        
        mock_instance = MagicMock()
        mock_instance.generate_content.return_value = mock_response
        mock_gen_model.return_value = mock_instance

        res = safe_ai_request("System Prompt", "User Prompt")
        self.assertEqual(res["content"], "AI generated skill gap response")

if __name__ == '__main__':
    unittest.main()
