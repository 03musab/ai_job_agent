import os
import json
import logging
import time
from cerebras.cloud.sdk import Cerebras

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
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
        logger.error("CEREBRAS_API_KEY not found.")
        raise Exception("Cerebras API key not configured.")

    client = Cerebras(api_key=api_key)
    attempt = 0
    
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
            
            # Validate JSON structure
            data = json.loads(content)
            return data

        except json.JSONDecodeError as e:
            logger.error(f"Malformed JSON received (Attempt {attempt+1}): {e}")
            logger.debug(f"Raw content: {content}")
        except Exception as e:
            logger.error(f"AI Service Error (Attempt {attempt+1}): {e}")
            
        attempt += 1
        if attempt <= retries:
            time.sleep(1)  # Brief backoff before retry
            
    raise Exception("AI Service failed to return valid JSON after retries.")