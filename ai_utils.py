import os
import re
import json
import logging
import time
from cerebras.cloud.sdk import Cerebras

# Get logger (do not configure basicConfig here to avoid overriding app settings)
logger = logging.getLogger("AI_Utils")

def safe_ai_request(system_prompt, user_prompt, model="llama-3.3-70b", retries=1):
    """
    Executes an OpenAI call with:
    - JSON validation
    - Automatic retry on failure
    - Error logging
    - Enforced temperature=0.2 for stability
    """
    api_key = os.getenv('CEREBRAS_API_KEY')
    if not api_key:
        logger.error("CEREBRAS_API_KEY not found in environment variables.")
        raise Exception("Cerebras API key not configured.")

    client = Cerebras(api_key=api_key)
    attempt = 0
    
    # Cerebras works best with a single prompt string (no roles)
    full_prompt = f"{system_prompt}\n\n{user_prompt}"
    
    while attempt <= retries:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": full_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.2  # Enforced constraint
            )
            
            content = response.choices[0].message.content

            if not content:
                raise ValueError("Received empty response from Cerebras.")

            # Try to robustly extract JSON from the model's string (strip markdown/code fences
            # and handle surrounding conversational text). This helps avoid intermittent failures
            # when the model wraps JSON in triple-backticks or adds commentary.
            def _extract_json_from_text(text: str):
                if not text:
                    raise json.JSONDecodeError("Empty response", text or "", 0)

                # First, try direct parse
                try:
                    return json.loads(text)
                except Exception:
                    pass

                # Remove fenced code blocks (```json ... ``` or ``` ... ```)
                cleaned = re.sub(r'```(?:json)?\s*(.*?)\s*```', r"\1", text, flags=re.S | re.I)
                # Remove inline code ticks
                cleaned = cleaned.replace('`', '')

                # Try to find JSON-like substrings (objects or arrays)
                pattern = re.compile(r'(\{(?:.|\s)*?\}|\[(?:.|\s)*?\])', re.S)
                candidates = pattern.findall(cleaned)
                for cand in candidates:
                    cand = cand.strip()
                    try:
                        return json.loads(cand)
                    except Exception:
                        continue

                # Fallback: try to extract from first { to last }
                first_obj = cleaned.find('{')
                last_obj = cleaned.rfind('}')
                if first_obj != -1 and last_obj != -1 and last_obj > first_obj:
                    sub = cleaned[first_obj:last_obj+1]
                    try:
                        return json.loads(sub)
                    except Exception:
                        pass

                # Fallback: try from first [ to last ]
                first_arr = cleaned.find('[')
                last_arr = cleaned.rfind(']')
                if first_arr != -1 and last_arr != -1 and last_arr > first_arr:
                    sub = cleaned[first_arr:last_arr+1]
                    try:
                        return json.loads(sub)
                    except Exception:
                        pass

                raise json.JSONDecodeError("No JSON object found in text", text, 0)

            try:
                data = _extract_json_from_text(content)
                return data
            except json.JSONDecodeError as e:
                logger.error(f"Malformed JSON received (Attempt {attempt+1}): {e}")
                logger.debug(f"Raw content: {content}")

        except Exception as e:
            logger.error(f"AI Service Error (Attempt {attempt+1}): {e}")
            
        attempt += 1
        if attempt <= retries:
            time.sleep(2 ** attempt)  # Exponential backoff
            
    raise Exception("AI Service failed to return valid JSON after retries.")