import os
import hashlib
import json
import time
from flask import Flask, request, jsonify, render_template
from ai_utils import safe_ai_request

# Set Cerebras API Key
os.environ['CEREBRAS_API_KEY'] = "csk-yjmhny5wcyh5dmt4wf9f5mp3k6w4cvkerw2vrh4ceyxh46vr"

app = Flask(__name__, template_folder='.')

# In-memory storage for demonstration. 
# In production, replace with database models (e.g., SQLAlchemy).
analysis_cache = {}

def get_user_resume():
    # Placeholder: Retrieve the current user's resume text from DB/Session
    # In a real app, this would query the database for the logged-in user's resume
    return """
    EXPERIENCED FULL STACK DEVELOPER
    Skills: Python, JavaScript, React, Flask, SQL, Git, Docker
    Experience: 5 years building scalable web applications.
    """

@app.route('/')
def index():
    return render_template('learning_path.html')

@app.route('/api/analyze_job_match', methods=['POST'])
def analyze_job_match():
    try:
        data = request.get_json()
        job_description = data.get('job_description')

        if not job_description:
            return jsonify({'error': 'Job description is required'}), 400

        # 1. Generate Hash for JD to prevent duplicate analysis
        # Normalize whitespace to ensure consistency
        jd_normalized = " ".join(job_description.split())
        jd_hash = hashlib.md5(jd_normalized.encode('utf-8')).hexdigest()

        # 2. Check if analysis already exists in cache/DB
        if jd_hash in analysis_cache:
            return jsonify(analysis_cache[jd_hash])

        # 3. Fetch user resume
        resume_text = get_user_resume()

        system_prompt = """
        You are an expert ATS (Applicant Tracking System) scanner. 
        Compare the Resume against the Job Description.
        Return a JSON object with exactly these keys:
        - match_score: (integer 0-100)
        - matched_skills: (list of strings)
        - missing_skills: (list of strings)
        - missing_keywords: (list of strings found in JD but missing in resume)
        - resume_improvement_suggestions: (list of actionable strings)
        """

        user_prompt = f"""
        RESUME:
        {resume_text}

        JOB DESCRIPTION:
        {job_description}
        """

        # 4. Call AI Utility
        result = safe_ai_request(system_prompt, user_prompt)

        # 5. Save to DB/Cache
        analysis_cache[jd_hash] = result

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze_skill_gap', methods=['POST'])
def analyze_skill_gap():
    try:
        data = request.get_json()
        target_role = data.get('target_role')
        
        if not target_role:
            return jsonify({'error': 'Target role is required'}), 400
            
        resume_text = get_user_resume()
        
        system_prompt = """
        You are an expert Career Coach. Analyze the gap between the candidate's resume and the target job role.
        Return a JSON object with exactly these keys:
        - readiness_score: (integer 0-100)
        - strong_skills: (list of matching skills)
        - missing_skills: (list of critical skills missing)
        """
        
        user_prompt = f"TARGET ROLE: {target_role}\nRESUME:\n{resume_text}"
        
        result = safe_ai_request(system_prompt, user_prompt)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate_roadmap', methods=['POST'])
def generate_roadmap():
    try:
        data = request.get_json()
        target_role = data.get('target_role')
        missing_skills = data.get('missing_skills')
        
        if not missing_skills:
            return jsonify({'error': 'Missing skills are required'}), 400
            
        system_prompt = """
        You are a Technical Curriculum Developer. Create a weekly learning path.
        Return JSON with:
        - total_weeks: (int)
        - weekly_breakdown: (list of objects with week_number, focus_topics (list), why_this_matters, mini_project (string title))
        """
        
        user_prompt = f"Role: {target_role}\nSkills: {missing_skills}"
        
        result = safe_ai_request(system_prompt, user_prompt)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/save_roadmap', methods=['POST'])
def save_roadmap():
    # Simulate database save
    time.sleep(0.5)
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    app.run(debug=True)