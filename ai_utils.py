import os
import re
import json
import logging
import time
import warnings
with warnings.catch_warnings():
    warnings.simplefilter("ignore", FutureWarning)
    import google.generativeai as genai
from cerebras.cloud.sdk import Cerebras

# Get logger (do not configure basicConfig here to avoid overriding app settings)
logger = logging.getLogger("AI_Utils")

_LEGACY_MODEL_ALIASES = {
    "gemini-3.6-flash": "gemini-2.5-flash",
    "gemini-3.5-flash": "gemini-2.5-flash",
    "gemini-3.7-flash": "gemini-2.5-flash",
}

_DEFAULT_GEMINI_MODELS = [
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-flash-latest",
]


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


def _is_non_retryable_error(err: Exception) -> bool:
    msg = str(err).lower()
    return any(tok in msg for tok in (
        "404", "not found", "api key", "invalid_argument", "permission",
        "401", "403", "unauthorized", "forbidden", "quota", "429", "resource_exhausted",
    ))


def _is_provider_fatal_error(err: Exception) -> bool:
    msg = str(err).lower()
    return any(tok in msg for tok in (
        "api key", "401", "403", "unauthorized", "forbidden", "quota", "429", "resource_exhausted",
    ))


def safe_ai_request(system_prompt, user_prompt, model="gemini-2.5-flash", retries=1, timeout=15):
    """
    Executes an AI completion request prioritizing Google Gemini (with fallback to Cerebras):
    - Uses valid, fast Gemini Flash models with strict request timeouts
    - Skips pointless retries on 404/auth/quota errors so fallback happens immediately
    - JSON enforcement
    """
    gemini_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
    cerebras_key = os.getenv('CEREBRAS_API_KEY')

    normalized_model = _LEGACY_MODEL_ALIASES.get((model or "").strip().lower(), model or "gemini-2.5-flash")

    # Priority 1: Google Gemini API
    if gemini_key:
        genai.configure(api_key=gemini_key)

        candidate_models = list(_DEFAULT_GEMINI_MODELS)
        if normalized_model and "gemini" in normalized_model.lower() and normalized_model not in candidate_models:
            candidate_models.insert(0, normalized_model)

        full_prompt = f"{system_prompt}\n\n{user_prompt}"

        for m_name in candidate_models:
            attempt = 0
            provider_failed = False
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
                    response = g_model.generate_content(
                        full_prompt,
                        request_options={"timeout": timeout}
                    )
                    content = getattr(response, "text", None)
                    if content:
                        return _extract_json_from_text(content)
                    break
                except Exception as e:
                    logger.warning(f"Gemini API ({m_name}) error (Attempt {attempt+1}): {e}")
                    if _is_provider_fatal_error(e):
                        provider_failed = True
                        break
                    if _is_non_retryable_error(e):
                        break
                    attempt += 1
                    if attempt <= retries:
                        time.sleep(0.5)
            if provider_failed:
                break

    # Priority 2: Cerebras Fallback (if CEREBRAS_API_KEY is configured)
    if cerebras_key:
        client = Cerebras(api_key=cerebras_key, timeout=timeout)
        cerebras_model = (
            "llama-3.3-70b"
            if ("qwen" in normalized_model.lower() or "gemini" in normalized_model.lower())
            else normalized_model
        )

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
                break
            except Exception as e:
                logger.error(f"Cerebras Service Error (Attempt {attempt+1}): {e}")
                if _is_non_retryable_error(e):
                    break
                attempt += 1
                if attempt <= retries:
                    time.sleep(0.5)

    raise Exception("AI Service failed to return valid JSON after retries. Please check your GEMINI_API_KEY or CEREBRAS_API_KEY in .env.")
