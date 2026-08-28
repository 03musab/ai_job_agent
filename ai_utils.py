import os
import re
import json
import logging
import time
import google.generativeai as genai
from cerebras.cloud.sdk import Cerebras

# Get logger (do not configure basicConfig here to avoid overriding app settings)
logger = logging.getLogger("AI_Utils")

def _extract_json_from_text(text: str):
    """
    Robustly extracts and parses JSON objects or arrays from LLM response text,
    stripping markdown backticks or commentary if present.
    """
    if not text:
        raise json.JSONDecodeError("Empty response text", text or "", 0)

    # 1. Direct JSON parse attempt
    try:
        return json.loads(text)
    except Exception:
        pass

    # 2. Strip code fences like ```json ... ``` or ``` ... ```
    cleaned = re.sub(r'```(?:json)?\s*(.*?)\s*```', r"\1", text, flags=re.S | re.I)
    cleaned = cleaned.replace('`', '')

    # 3. Search for outer JSON objects {} or arrays []
    pattern = re.compile(r'(\{(?:.|\s)*?\}|\[(?:.|\s)*?\])', re.S)
    candidates = pattern.findall(cleaned)
    for cand in candidates:
        cand = cand.strip()
        try:
            return json.loads(cand)
        except Exception:
            continue

    # 4. Fallback: locate first { and last }
    first_obj = cleaned.find('{')
    last_obj = cleaned.rfind('}')
    if first_obj != -1 and last_obj != -1 and last_obj > first_obj:
        sub = cleaned[first_obj:last_obj+1]
        try:
            return json.loads(sub)
        except Exception:
            pass

    # 5. Fallback: locate first [ and last ]
    first_arr = cleaned.find('[')
    last_arr = cleaned.rfind(']')
    if first_arr != -1 and last_arr != -1 and last_arr > first_arr:
        sub = cleaned[first_arr:last_arr+1]
        try:
            return json.loads(sub)
        except Exception:
            pass

    raise json.JSONDecodeError("No valid JSON object could be extracted", text, 0)


def safe_ai_request(system_prompt, user_prompt, model="gemini-3.6-flash", retries=2):
    """
    Executes an AI completion request prioritizing Google Gemini (with fallback to Cerebras):
    - Default model: gemini-3.6-flash
    - JSON enforcement
    - Automatic retries and model fallback
    """
    gemini_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
    cerebras_key = os.getenv('CEREBRAS_API_KEY')

    # Priority 1: Google Gemini API
    if gemini_key:
        genai.configure(api_key=gemini_key)
        
        # Candidate Gemini models in preference order (starting with gemini-3.6-flash)
        candidate_models = ["gemini-3.6-flash", "gemini-3.5-flash", "gemini-3.7-flash", "gemini-flash-latest"]
        if model and "gemini" in model.lower() and model not in candidate_models:
            candidate_models.insert(0, model)

        full_prompt = f"{system_prompt}\n\n{user_prompt}"

        for m_name in candidate_models:
            attempt = 0
            while attempt <= retries:
                try:
                    logger.info(f"Attempting Gemini request with model: {m_name}")
                    g_model = genai.GenerativeModel(
                        model_name=m_name,
                        generation_config={
                            "response_mime_type": "application/json",
                            "temperature": 0.2
                        }
                    )
                    response = g_model.generate_content(full_prompt)
                    content = response.text
                    if content:
                        data = _extract_json_from_text(content)
                        return data
                except Exception as e:
                    logger.warning(f"Gemini API ({m_name}) error (Attempt {attempt+1}): {e}")
                    attempt += 1
                    if attempt <= retries:
                        time.sleep(1)

    # Priority 2: Cerebras Fallback (if CEREBRAS_API_KEY is configured)
    if cerebras_key:
        client = Cerebras(api_key=cerebras_key)
        # Use valid Cerebras model identifier
        cerebras_model = "llama-3.3-70b" if ("qwen" in model.lower() or "gemini" in model.lower()) else model

        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        attempt = 0
        while attempt <= retries:
            try:
                logger.info(f"Attempting Cerebras request with model: {cerebras_model}")
                response = client.chat.completions.create(
                    model=cerebras_model,
                    messages=[{"role": "user", "content": full_prompt}],
                    response_format={"type": "json_object"},
                    temperature=0.2
                )
                content = response.choices[0].message.content
                if content:
                    return _extract_json_from_text(content)
            except Exception as e:
                logger.error(f"Cerebras Service Error (Attempt {attempt+1}): {e}")
                attempt += 1
                if attempt <= retries:
                    time.sleep(1)

    raise Exception("AI Service failed to return valid JSON after retries. Please check your GEMINI_API_KEY in .env.")