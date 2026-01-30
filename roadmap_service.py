import json
import os
import logging
from typing import List, Dict, Any
from ai_utils import safe_ai_request
from skill_gap_service import SkillGapService

logger = logging.getLogger(__name__)

class RoadmapService:
    """
    Service to generate personalized learning roadmaps using OpenAI.
    """
    
    def __init__(self):
        pass

    def generate(self, target_role: str, current_skill_level: str, missing_skills: List[str], availability_hours: int, learning_style: str) -> Dict[str, Any]:
        """
        # Important: explicitly forbid markdown/code fences or extra commentary
        # so the response is raw JSON only (helps avoid intermittent parse failures).
        system_prompt += "\nIMPORTANT: Do NOT wrap the JSON in Markdown code fences or include any explanatory\ntext. Return raw JSON only."
        Generates a weekly learning roadmap based on missing skills and user preferences.
        """
        if not missing_skills:
             return {
                "total_weeks": 0,
                "weekly_breakdown": [],
                "message": "No missing skills to learn!"
            }

        system_prompt = """You are an expert Technical Career Coach and Curriculum Designer.
        Create a personalized, practical learning roadmap for a user to bridge their skill gaps.
        
        The roadmap must be beginner-friendly, actionable, and project-based.
        
        Output MUST be valid JSON with the following structure:
        {
            "total_weeks": integer,
            "weekly_breakdown": [
                {
                    "week_number": integer,
                    "focus_topics": ["string", "string"],
                    "why_this_matters": "string",
                    "practice_task": "string",
                    "mini_project": "string"
                }
            ]
        }
        """
        # Important: explicitly forbid markdown/code fences or extra commentary
        # so the response is raw JSON only (helps avoid intermittent parse failures).
        system_prompt += "\nIMPORTANT: Do NOT wrap the JSON in Markdown code fences or include any explanatory\ntext. Return raw JSON only."

        user_prompt = f"""
        Generate a learning roadmap based on the following profile:
        
        Target Role: {target_role}
        Current Skill Level: {current_skill_level}
        Missing Skills: {json.dumps(missing_skills)}
        Weekly Availability: {availability_hours} hours
        Learning Style: {learning_style}
        
        Constraints:
        1. Break down the missing skills into a logical sequence.
        2. Ensure the workload fits within {availability_hours} hours/week.
        3. Each week must have a concrete 'mini_project' or 'practice_task' to reinforce learning.
        4. Keep explanations concise and practical.
        5. If the list of missing skills is long, group related skills or prioritize the most critical ones for the first few weeks.
        """

        try:
            return safe_ai_request(system_prompt, user_prompt, model="llama-3.3-70b")

        except Exception as e:
            logger.error(f"Roadmap generation failed: {e}")
            return {
                "total_weeks": 0,
                "weekly_breakdown": [],
                "error": str(e),
                "message": "Roadmap generation failed. Please try again."
            }

    def generate_combined(self, target_role: str, user_skills: List[str], current_skill_level: str, availability_hours: int, learning_style: str) -> Dict[str, Any]:
        """
        Combines Skill Gap Analysis and Roadmap Generation into a single AI request.
        Returns a dictionary containing both 'analysis' and 'roadmap' keys.
        """
        # 1. Get Required Skills
        skill_service = SkillGapService()
        role_data = skill_service.get_role_def(target_role)
        
        if not role_data:
             return {"error": f"Role '{target_role}' not found in skill map."}

        required_core = role_data.get('core_skills', [])
        required_secondary = role_data.get('secondary_skills', [])
        required_tools = role_data.get('tools', [])

        # 2. Construct Combined Prompt
        system_prompt = """You are an expert Technical Career Coach and Skill Analyst.
        Perform two tasks in a single pass:
        
        TASK 1: SKILL GAP ANALYSIS
        Compare User Skills against Required Skills.
        - Identify 'strong_skills' (direct matches).
        - Identify 'improving_skills' (related matches).
        - Identify 'missing_skills' (critical gaps).
        - Calculate a 'readiness_score' (0-100).

        TASK 2: LEARNING ROADMAP
        Create a personalized weekly roadmap to bridge the 'missing_skills' identified in Task 1.
        - Fit within the user's weekly availability.
        - Include mini-projects.

        OUTPUT FORMAT:
        Return a single valid JSON object:
        {
            "analysis": { "strong_skills": [], "improving_skills": [], "missing_skills": [], "readiness_score": 0 },
            "roadmap": { "total_weeks": 0, "weekly_breakdown": [ { "week_number": 1, "focus_topics": [], "why_this_matters": "...", "practice_task": "...", "mini_project": "..." } ] }
        }
        """

        user_prompt = f"""
        Target Role: {target_role}
        Current Level: {current_skill_level}
        
        REQUIRED SKILLS:
        Core: {json.dumps(required_core)}
        Secondary: {json.dumps(required_secondary)}
        Tools: {json.dumps(required_tools)}
        
        USER PROFILE:
        Current Skills: {json.dumps(user_skills)}
        Availability: {availability_hours} hours/week
        Learning Style: {learning_style}
        """

        try:
            return safe_ai_request(system_prompt, user_prompt, model="llama-3.3-70b")
        except Exception as e:
            logger.error(f"Combined generation failed: {e}")
            return {"error": str(e)}