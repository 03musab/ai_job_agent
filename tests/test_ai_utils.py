import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# Add project root to sys.path
sys.path.append(r'c:\Users\musab\Desktop\ai_job_agent')

from ai_utils import _extract_json_from_text, safe_ai_request, reset_model_cooldowns

class TestAIUtils(unittest.TestCase):
    def setUp(self):
        reset_model_cooldowns()

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
    @patch.dict(os.environ, {'GEMINI_API_KEY': 'mock-gemini-key', 'CEREBRAS_API_KEY': ''})
    def test_safe_ai_request_gemini(self, mock_gen_model):
        mock_response = MagicMock()
        mock_response.text = '{"content": "AI generated skill gap response"}'
        
        mock_instance = MagicMock()
        mock_instance.generate_content.return_value = mock_response
        mock_gen_model.return_value = mock_instance

        res = safe_ai_request("System Prompt", "User Prompt")
        self.assertEqual(res["content"], "AI generated skill gap response")

    @patch('ai_utils.Cerebras')
    @patch.dict(os.environ, {'CEREBRAS_API_KEY': 'mock-cerebras-key', 'GEMINI_API_KEY': ''})
    def test_safe_ai_request_cerebras_fastest(self, mock_cerebras_cls):
        mock_msg = MagicMock()
        mock_msg.content = '{"readiness_score": 88, "strong_skills": ["Python"], "missing_skills": ["Kubernetes"]}'
        mock_choice = MagicMock()
        mock_choice.message = mock_msg
        mock_resp = MagicMock()
        mock_resp.choices = [mock_choice]

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_resp
        mock_cerebras_cls.return_value = mock_client

        res = safe_ai_request("System Prompt", "User Prompt")
        self.assertEqual(res["readiness_score"], 88)
        called_model = mock_client.chat.completions.create.call_args.kwargs["model"]
        self.assertEqual(called_model, "gpt-oss-120b")

    @patch('google.generativeai.GenerativeModel')
    @patch.dict(os.environ, {'GEMINI_API_KEY': 'mock-gemini-key', 'CEREBRAS_API_KEY': ''})
    def test_gemini_rotates_on_429_to_next_high_quota_model_and_gemma(self, mock_gen_model):
        called_models = []

        def side_effect(model_name, **kwargs):
            called_models.append((model_name, kwargs))
            inst = MagicMock()
            if model_name in ("gemini-3.5-flash-lite", "gemini-3.1-flash-lite"):
                inst.generate_content.side_effect = Exception("429 Resource exhausted quota exceeded")
            else:
                resp = MagicMock()
                resp.text = '```json\n{"ok": true, "provider": "gemma4"}\n```'
                inst.generate_content.return_value = resp
            return inst

        mock_gen_model.side_effect = side_effect

        res = safe_ai_request("System Prompt", "User Prompt")
        self.assertEqual(res["provider"], "gemma4")
        self.assertEqual([m for m, _ in called_models], [
            "gemini-3.5-flash-lite",
            "gemini-3.1-flash-lite",
            "gemma-4-26b-a4b-it",
        ])
        # Verify Gemma 4 was invoked without unsupported system_instruction / JSON mime mode
        gemma_kwargs = called_models[-1][1]
        self.assertNotIn("system_instruction", gemma_kwargs)
        self.assertNotIn("response_mime_type", gemma_kwargs.get("generation_config", {}))

        # Second call immediately skips the 429-cooled models and hits gemma-4-26b-a4b-it directly
        called_models.clear()
        res2 = safe_ai_request("System Prompt", "User Prompt")
        self.assertEqual(res2["provider"], "gemma4")
        self.assertEqual([m for m, _ in called_models], ["gemma-4-26b-a4b-it"])

if __name__ == '__main__':
    unittest.main()
