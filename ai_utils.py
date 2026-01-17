import os
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

            # Validate JSON structure
            data = json.loads(content)
            return data

        except json.JSONDecodeError as e:
            logger.error(f"Malformed JSON received (Attempt {attempt+1}): {e}")
        except Exception as e:
            logger.error(f"AI Service Error (Attempt {attempt+1}): {e}")
            
        attempt += 1
        if attempt <= retries:
            time.sleep(2 ** attempt)  # Exponential backoff
            
    raise Exception("AI Service failed to return valid JSON after retries.")