import os
import re
import json
import logging
from typing import List, Dict, Any, Union
import docx
from pdfminer.high_level import extract_text
from ai_utils import safe_ai_request

logger = logging.getLogger(__name__)

class ResumeParsingService:
    """
    Service to parse resumes (PDF/DOCX), extract text, and analyze content 
    using keyword matching and AI.
    """
    
    def __init__(self):
        self.has_api_key = bool(
            os.environ.get("CEREBRAS_API_KEY")
            or os.environ.get("GEMINI_API_KEY")
            or os.environ.get("GOOGLE_API_KEY")
        )
        
        # Fallback keywords if AI fails or is unavailable
        self.keyword_bank = {
            'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'go', 'rust', 'html', 'css',
            'sql', 'nosql', 'postgresql', 'mongodb', 'redis', 'react', 'next.js', 'angular', 'vue',
            'node.js', 'django', 'flask', 'fastapi', 'spring boot', 'aws', 'azure', 'gcp', 'linux',
            'docker', 'kubernetes', 'terraform', 'git', 'ci/cd', 'graphql', 'rest api', 'agile', 'scrum',
            'machine learning', 'deep learning', 'nlp', 'llm', 'pytorch', 'tensorflow', 'pandas', 'ai',
            'figma', 'ui/ux', 'communication', 'leadership', 'problem solving', 'teamwork'
        }

    def parse(self, file_path: str, fast_mode: bool = False) -> Dict[str, Any]:
        """
        Main entry point to parse a resume file.
        Returns a dictionary with raw_text, skills, and work_experience.
        When fast_mode=True (onboarding), uses ultra-fast lightweight models with strict timeout.
        """
        if not os.path.exists(file_path):
            logger.error(f"Resume file not found: {file_path}")
            return {}

        # 1. Extract Text
        raw_text = self._extract_text(file_path)
        if not raw_text:
            return {}

        # 2. Normalize Text
        clean_text = self._normalize_text(raw_text)

        # 3. Extract Data (Skills + Experience)
        extracted_data = self._extract_structured_data(clean_text, fast_mode=fast_mode)

        return {
            'raw_text': raw_text,
            'skills': extracted_data.get('skills', []),
            'work_experience': extracted_data.get('work_experience', [])
        }

    def _extract_text(self, file_path: str) -> str:
        """Extracts text from PDF, DOCX, or TXT files."""
        try:
            low = file_path.lower()
            if low.endswith('.pdf'):
                return extract_text(file_path)
            elif low.endswith('.docx'):
                doc = docx.Document(file_path)
                return "\n".join([para.text for para in doc.paragraphs])
            elif low.endswith('.txt'):
                with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                    return f.read()
            else:
                logger.warning(f"Unsupported file format: {file_path}")
                return ""
        except Exception as e:
            logger.error(f"Error extracting text from {file_path}: {e}")
            return ""

    def _normalize_text(self, text: str) -> str:
        """Normalizes text: lowercase, removes excessive whitespace and non-standard symbols."""
        # Convert to lowercase
        text = text.lower()
        # Remove non-ascii characters (optional, but helps with clean AI input)
        text = re.sub(r'[^\x00-\x7F]+', ' ', text)
        # Collapse whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def _extract_structured_data(self, text: str, fast_mode: bool = False) -> Dict[str, Any]:
        """
        Uses AI to extract skills and work experience.
        When fast_mode=True (onboarding), uses the fastest lightweight model (Cerebras llama3.1-8b
        or Gemini Flash-Lite) with zero retries and a tight timeout so onboarding feels instant.
        Falls back to keyword matching for skills if AI fails.
        """
        # 1. Keyword Matching (Baseline)
        found_skills = [skill for skill in self.keyword_bank if skill in text]
        
        # 2. AI Extraction
        if self.has_api_key:
            try:
                system_prompt = "Extract skills and work experience from the resume. Return ONLY valid JSON."
                excerpt_len = 2800 if fast_mode else 4000
                user_prompt = (
                    "Extract JSON with keys:\n"
                    '1. "skills": list of technical and soft skill strings\n'
                    '2. "work_experience": list of objects {"title","company","start_date","end_date","description"}\n\n'
                    f"Resume:\n{text[:excerpt_len]}"
                )

                if fast_mode:
                    data = safe_ai_request(
                        system_prompt,
                        user_prompt,
                        model="gemini-2.0-flash-lite",
                        retries=0,
                        timeout=6,
                        prefer_fast=True,
                    )
                else:
                    data = safe_ai_request(system_prompt, user_prompt, model="gemini-2.5-flash")
                
                if isinstance(data, dict):
                    ai_skills = [str(s).lower().strip() for s in (data.get('skills') or []) if str(s).strip()]
                    combined_skills = list(set(found_skills + ai_skills))
                    return {
                        'skills': combined_skills,
                        'work_experience': data.get('work_experience', []) if isinstance(data.get('work_experience'), list) else []
                    }

            except Exception as e:
                logger.error(f"AI parsing failed: {e}")
        
        # Fallback if AI fails
        return {
            'skills': found_skills,
            'work_experience': []
        }