import json
import os
import logging
from typing import List, Dict, Any
from ai_utils import safe_ai_request

logger = logging.getLogger(__name__)

class RoadmapService:
    """
    Service to generate personalized learning roadmaps using OpenAI.
    """
    
    def __init__(self):
        pass

    def generate(self, target_role: str, current_skill_level: str, missing_skills: List[str], availability_hours: int, learning_style: str) -> Dict[str, Any]:
        """
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