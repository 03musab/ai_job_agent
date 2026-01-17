import json
import os
import logging
from typing import List, Dict, Any
from ai_utils import safe_ai_request

logger = logging.getLogger(__name__)

class SkillGapService:
    """
    Service to analyze skill gaps between a user's profile and a target role
    using a predefined skill map and OpenAI for semantic classification.
    """
    
    def __init__(self, role_map_path: str = 'role_skill_map.json'):
        self.role_map_path = role_map_path
        self.role_map = self._load_role_map()

    def _load_role_map(self) -> Dict:
        """Loads the static role-skill mapping JSON."""
        if not os.path.exists(self.role_map_path):
            logger.error(f"Role map file not found at {self.role_map_path}")
            return {}
        try:
            with open(self.role_map_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading role map: {e}")
            return {}

    def analyze(self, target_role: str, resume_skills: List[str], user_selected_skills: List[str]) -> Dict[str, Any]:
        """
        Performs the gap analysis.
        Returns a dictionary with strong, improving, and missing skills, plus a readiness score.
        """

        # 1. Retrieve Required Skills from Map
        # Case-insensitive lookup for the role
        role_data = next((self.role_map[r] for r in self.role_map if r.lower() == target_role.lower()), None)
        
        if not role_data:
            return {"error": f"Role '{target_role}' not found in skill map."}

        required_core = role_data.get('core_skills', [])
        required_secondary = role_data.get('secondary_skills', [])
        required_tools = role_data.get('tools', [])
        
        # Combine user skills (deduplicated)
        user_skills = list(set(resume_skills + user_selected_skills))

        # 2. Construct Deterministic Prompt
        system_prompt = """You are an expert AI Skill Analyst. Perform a Skill Gap Analysis.
        Compare the User's Skills against the Required Skills.
        
        Classify the User's status for the Required Skills into:
        1. strong_skills: User has this skill or a semantic equivalent (e.g., 'React.js' matches 'React').
        2. improving_skills: User has a related/foundational skill but not the exact requirement.
        3. missing_skills: No evidence of this skill.

        Calculate 'readiness_score' (0-100) weighting Core skills higher than Secondary/Tools.
        Output MUST be valid JSON."""

        user_prompt = f"""
        Target Role: {target_role}
        Required Core: {json.dumps(required_core)}
        Required Secondary: {json.dumps(required_secondary)}
        Required Tools: {json.dumps(required_tools)}
        User Skills: {json.dumps(user_skills)}
        
        Return JSON: {{ "strong_skills": [], "improving_skills": [], "missing_skills": [], "readiness_score": int }}
        """

        # 3. Call OpenAI
        try:
            return safe_ai_request(system_prompt, user_prompt, model="llama-3.3-70b")

        except Exception as e:
            logger.error(f"Skill gap analysis failed: {e}")
            return {"error": str(e)}