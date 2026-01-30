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
        self.has_api_key = bool(os.environ.get("CEREBRAS_API_KEY"))
        
        # Fallback keywords if AI fails or is unavailable
        self.keyword_bank = {
            'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'html', 'css', 'sql', 'nosql',
            'react', 'angular', 'vue', 'node.js', 'django', 'flask', 'fastapi', 'aws', 'azure', 'gcp',
            'docker', 'kubernetes', 'git', 'ci/cd', 'agile', 'scrum', 'machine learning', 'ai',
            'communication', 'leadership', 'problem solving', 'teamwork'
        }

    def parse(self, file_path: str) -> Dict[str, Any]:
        """
        Main entry point to parse a resume file.
        Returns a dictionary with raw_text, skills, and work_experience.
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
        extracted_data = self._extract_structured_data(clean_text)

        return {
            'raw_text': raw_text,
            'skills': extracted_data.get('skills', []),
            'work_experience': extracted_data.get('work_experience', [])
        }

    def _extract_text(self, file_path: str) -> str:
        """Extracts text from PDF or DOCX files."""
        try:
            if file_path.lower().endswith('.pdf'):
                return extract_text(file_path)
            elif file_path.lower().endswith('.docx'):
                doc = docx.Document(file_path)
                return "\n".join([para.text for para in doc.paragraphs])
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

    def _extract_structured_data(self, text: str) -> Dict[str, Any]:
        """
        Uses OpenAI to extract skills and work experience. 
        Falls back to keyword matching for skills if AI fails.
        """
        # 1. Keyword Matching (Baseline)
        found_skills = [skill for skill in self.keyword_bank if skill in text]
        
        # 2. AI Extraction
        if self.has_api_key:
            try:
                system_prompt = "You are an expert resume parser. Extract skills and work experience from the resume text provided. Return ONLY valid JSON."
                user_prompt = f"Analyze the following resume text and extract:\n1. 'skills': A list of technical and soft skills.\n2. 'work_experience': A list of objects, each containing 'title', 'company', 'start_date', 'end_date', and 'description'.\n\nResume Text:\n{text[:4000]}"

                data = safe_ai_request(system_prompt, user_prompt, model="llama-3.3-70b")
                
                
                # Merge AI skills with keyword skills (deduplicate)
                ai_skills = [s.lower() for s in data.get('skills', [])]
                combined_skills = list(set(found_skills + ai_skills))
                
                return {
                    'skills': combined_skills,
                    'work_experience': data.get('work_experience', [])
                }

            except Exception as e:
                logger.error(f"AI parsing failed: {e}")
        
        # Fallback if AI fails
        return {
            'skills': found_skills,
            'work_experience': [] # Regex fallback could be added here if strictly necessary
        }