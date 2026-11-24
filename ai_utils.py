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

# Map retired/legacy model names directly to active fastest high-quota equivalents
_LEGACY_MODEL_ALIASES = {
    "gemini-1.5-flash": "gemini-3.5-flash-lite",
    "gemini-1.5-pro": "gemini-3.8-flash",
    "gemini-2.0-flash": "gemini-3.5-flash-lite",
    "gemini-2.0-flash-lite": "gemini-3.5-flash-lite",
    "gemini-2.5-flash": "gemini-3.5-flash-lite",
    "gemini-3.5-flash": "gemini-3.5-flash-lite",
    "gemini-3.7-flash": "gemini-3.8-flash",
    "llama-3.3-70b": "gpt-oss-120b",
    "llama3.1-8b": "gpt-oss-120b",
    "qwen-3-32b": "qwen-3.8-27b",
}

# Tier 1: Active fastest Cerebras Shared Inference models (~3,000 tok/s and ~1,850 tok/s)
_CEREBRAS_FAST_MODELS = [
    "gpt-oss-120b",
    "qwen-3.8-27b",
]

# Tier 2-4: Active Google AI Studio text-out / general models ordered by speed & daily quota:
#   - Flash-Lite pool: 15 RPM, 250K TPM, 500 RPD each (1,000 RPD combined)
#   - Gemma 4 pool:    30 RPM, 16K TPM, 14,400 RPD each (28,800 RPD combined!)
#   - Flash reserve:   5-10 RPM, 250K TPM, 20 RPD each (+80-100 RPD reserve)
_FAST_GEMINI_MODELS = [
    "gemini-3.5-flash-lite",   # 15 RPM | 250K TPM | 500 RPD
    "gemini-3.1-flash-lite",   # 15 RPM | 250K TPM | 500 RPD
    "gemma-4-26b-a4b-it",      # 30 RPM | 16K TPM  | 14,400 RPD (MoE, ultra-fast)
    "gemma-4-31b-it",          # 30 RPM | 16K TPM  | 14,400 RPD (Dense 31B)
    "gemini-flash-lite-latest",
    "gemini-3.8-flash",        # 5 RPM  | 250K TPM | 20 RPD
    "gemini-3.6-flash",        # 5 RPM  | 250K TPM | 20 RPD
    "gemini-3-flash",          # 5 RPM  | 250K TPM | 20 RPD
    "gemini-2.5-flash-lite",   # 10 RPM | 250K TPM | 20 RPD
    "gemini-flash-latest",
]

_DEFAULT_GEMINI_MODELS = list(_FAST_GEMINI_MODELS)

_CEREBRAS_MODEL_CACHE = {"models": [], "ts": 0.0}
_CEREBRAS_CACHE_TTL = 600.0  # 10 minutes

# In-memory per-model cooldown tracker: { "provider:model_id": unix_timestamp_until }
# Prevents wasting latency on models that recently returned 429 (quota/RPM) or 404 (not found).
_MODEL_COOLDOWN_UNTIL = {}


def reset_model_cooldowns():
    """Clears all cached per-model rate-limit/404 cooldowns."""
    _MODEL_COOLDOWN_UNTIL.clear()


def _is_model_on_cooldown(provider: str, model_id: str) -> bool:
    key = f"{provider}:{model_id}"
    until = _MODEL_COOLDOWN_UNTIL.get(key, 0.0)
    if until <= 0.0:
        return False
    if time.time() >= until:
        _MODEL_COOLDOWN_UNTIL.pop(key, None)
        return False
    return True


def _mark_model_cooldown(provider: str, model_id: str, err: Exception):
    """Records a smart cooldown window for a model based on the error type."""
    msg = str(err).lower()
    key = f"{provider}:{model_id}"
    now = time.time()

    if any(tok in msg for tok in ("404", "not found", "model_not_found", "no longer available")):
        _MODEL_COOLDOWN_UNTIL[key] = now + 86400.0  # 24h for retired/missing models
        return

    if any(tok in msg for tok in ("429", "quota", "resource_exhausted", "rate limit", "too many requests")):
        # Try parsing retry_delay seconds from Gemini error payload if present
        sec_match = re.search(r'seconds:\s*(\d+)', str(err))
        if sec_match:
            delay = min(max(int(sec_match.group(1)), 60), 14400)
            _MODEL_COOLDOWN_UNTIL[key] = now + delay
            return
        if "per day" in msg or "perday" in msg or "rpd" in msg:
            _MODEL_COOLDOWN_UNTIL[key] = now + 3600.0  # 1h cooldown for daily quota
        else:
            _MODEL_COOLDOWN_UNTIL[key] = now + 65.0    # 65s cooldown for RPM/TPM burst


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
        "404", "not found", "model_not_found", "no longer available",
        "api key", "invalid_argument", "permission",
        "401", "403", "unauthorized", "forbidden",
        "quota", "429", "resource_exhausted", "rate limit", "too many requests",
    ))


def _is_provider_fatal_error(err: Exception) -> bool:
    # Only auth/key failures kill the entire provider; 429/quota & 404 are per-model so we seamlessly rotate models
    msg = str(err).lower()
    return any(tok in msg for tok in (
        "api key", "invalid_api_key", "401", "403", "unauthorized", "forbidden",
    ))


def _is_gemma_model(model_name: str) -> bool:
    return (model_name or "").strip().lower().startswith("gemma")


def _discover_cerebras_models(client: Cerebras):
    """Dynamically fetches active Cerebras model IDs (cached) as a future-proof fallback."""
    now = time.time()
    if _CEREBRAS_MODEL_CACHE["models"] and (now - _CEREBRAS_MODEL_CACHE["ts"]) < _CEREBRAS_CACHE_TTL:
        return list(_CEREBRAS_MODEL_CACHE["models"])
    try:
        resp = client.models.list()
        items = getattr(resp, "data", None) or []
        ids = [getattr(m, "id", None) for m in items if getattr(m, "id", None)]
        if ids:
            _CEREBRAS_MODEL_CACHE["models"] = ids
            _CEREBRAS_MODEL_CACHE["ts"] = now
            return list(ids)
    except Exception as e:
        logger.debug(f"Could not list Cerebras models dynamically: {e}")
    return []


def safe_ai_request(system_prompt, user_prompt, model="gemini-3.5-flash-lite", retries=1, timeout=15, prefer_fast=True):
    """
    Executes an AI JSON completion request with multi-provider, multi-model failover
    and per-model rate-limit cooldowns to virtually eliminate 429 rate-limit failures:

    1. Cerebras Cloud Inference first (gpt-oss-120b @ ~3,000 tok/s, qwen-3.8-27b @ ~1,850 tok/s,
       plus automatic live model-list discovery).
    2. Google AI Studio high-quota pool:
       - Flash-Lite: gemini-3.5-flash-lite (500 RPD), gemini-3.1-flash-lite (500 RPD)
       - Gemma 4:    gemma-4-26b-a4b-it (14,400 RPD), gemma-4-31b-it (14,400 RPD)
       - Flash burst reserve: gemini-3.8-flash, gemini-3.6-flash, gemini-3-flash, gemini-2.5-flash-lite
    """
    cerebras_key = os.getenv('CEREBRAS_API_KEY')
    gemini_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
    env_cerebras_model = (os.getenv('CEREBRAS_MODEL') or '').strip()
    env_gemini_model = (os.getenv('GEMINI_MODEL') or '').strip()

    raw_model = (model or "").strip().lower()
    normalized_model = _LEGACY_MODEL_ALIASES.get(raw_model, (model or "gemini-3.5-flash-lite").strip())

    def _run_cerebras_candidates():
        if not cerebras_key:
            return None
        client = Cerebras(api_key=cerebras_key, timeout=timeout)

        candidates = []
        if env_cerebras_model:
            candidates.append(env_cerebras_model)
        if (
            normalized_model
            and "gemini" not in normalized_model.lower()
            and not _is_gemma_model(normalized_model)
            and normalized_model not in candidates
        ):
            candidates.append(normalized_model)
        for m in _CEREBRAS_FAST_MODELS:
            if m not in candidates:
                candidates.append(m)

        tried = set()
        provider_fatal = False

        def _try_model(selected_model: str):
            nonlocal provider_fatal
            if not selected_model or selected_model in tried:
                return None
            if _is_model_on_cooldown("cerebras", selected_model):
                return None
            tried.add(selected_model)
            attempt = 0
            use_json_format = True
            while attempt <= retries:
                try:
                    logger.info(f"Attempting Cerebras request with model: {selected_model}")
                    kwargs = {
                        "model": selected_model,
                        "messages": [
                            {"role": "system", "content": str(system_prompt or "")},
                            {"role": "user", "content": str(user_prompt or "")},
                        ],
                        "temperature": 0.2,
                    }
                    if use_json_format:
                        kwargs["response_format"] = {"type": "json_object"}
                    response = client.chat.completions.create(**kwargs)
                    msg = response.choices[0].message
                    content = getattr(msg, "content", None) or getattr(msg, "reasoning", None)
                    if content:
                        return _extract_json_from_text(content)
                    break
                except Exception as e:
                    err_str = str(e).lower()
                    logger.warning(f"Cerebras Service Error ({selected_model}, Attempt {attempt+1}): {e}")
                    if use_json_format and ("response_format" in err_str or "json_object" in err_str):
                        use_json_format = False
                        continue
                    _mark_model_cooldown("cerebras", selected_model, e)
                    if _is_provider_fatal_error(e):
                        provider_fatal = True
                        break
                    if _is_non_retryable_error(e):
                        break
                    attempt += 1
                    if attempt <= retries:
                        time.sleep(0.4)
            return None

        for cb_model in candidates:
            res = _try_model(cb_model)
            if res is not None:
                return res
            if provider_fatal:
                return None

        # Dynamic fallback: query active Cerebras models once if all hardcoded IDs failed/404'd
        for discovered in _discover_cerebras_models(client):
            res = _try_model(discovered)
            if res is not None:
                return res
            if provider_fatal:
                return None

        return None

    def _run_gemini_candidates():
        if not gemini_key:
            return None
        genai.configure(api_key=gemini_key)

        base_list = list(_FAST_GEMINI_MODELS if prefer_fast else _DEFAULT_GEMINI_MODELS)
        candidate_models = []
        if env_gemini_model:
            candidate_models.append(env_gemini_model)
        if (
            normalized_model
            and ("gemini" in normalized_model.lower() or _is_gemma_model(normalized_model))
            and normalized_model not in candidate_models
        ):
            candidate_models.append(normalized_model)
        for m in base_list:
            if m not in candidate_models:
                candidate_models.append(m)

        for m_name in candidate_models:
            if _is_model_on_cooldown("gemini", m_name):
                continue

            attempt = 0
            provider_failed = False
            gemma_mode = _is_gemma_model(m_name)

            while attempt <= retries:
                try:
                    logger.info(f"Attempting Gemini/Gemma request with model: {m_name}")
                    if gemma_mode:
                        # Gemma models on Gemini API do not always support system_instruction or JSON mime mode
                        g_model = genai.GenerativeModel(
                            model_name=m_name,
                            generation_config={"temperature": 0.2}
                        )
                        combined_prompt = (
                            f"{str(system_prompt or '').strip()}\n\n"
                            f"{str(user_prompt or '').strip()}\n\n"
                            "IMPORTANT: Return ONLY a valid raw JSON object without markdown commentary."
                        )
                        response = g_model.generate_content(
                            combined_prompt,
                            request_options={"timeout": timeout}
                        )
                    else:
                        g_model = genai.GenerativeModel(
                            model_name=m_name,
                            system_instruction=str(system_prompt or ""),
                            generation_config={
                                "response_mime_type": "application/json",
                                "temperature": 0.2
                            }
                        )
                        response = g_model.generate_content(
                            str(user_prompt or ""),
                            request_options={"timeout": timeout}
                        )

                    content = getattr(response, "text", None)
                    if content:
                        return _extract_json_from_text(content)
                    break
                except Exception as e:
                    err_str = str(e).lower()
                    logger.warning(f"Gemini/Gemma API ({m_name}) error (Attempt {attempt+1}): {e}")
                    # If a model rejects system_instruction or JSON mode, retry once in plain prompt mode
                    if not gemma_mode and any(tok in err_str for tok in ("developer instruction", "system_instruction", "json mode", "response_mime_type")):
                        gemma_mode = True
                        continue
                    _mark_model_cooldown("gemini", m_name, e)
                    if _is_provider_fatal_error(e):
                        provider_failed = True
                        break
                    if _is_non_retryable_error(e):
                        break
                    attempt += 1
                    if attempt <= retries:
                        time.sleep(0.4)
            if provider_failed:
                break
        return None

    # Priority 1: Cerebras (fastest inference: ~3,000 tok/s)
    if cerebras_key:
        res = _run_cerebras_candidates()
        if res is not None:
            return res

    # Priority 2: Google Gemini Flash-Lite -> Gemma 4 (28.8K RPD!) -> Gemini Flash reserve
    if gemini_key:
        res = _run_gemini_candidates()
        if res is not None:
            return res

    raise Exception("AI Service failed to return valid JSON across all configured models. Please check your CEREBRAS_API_KEY or GEMINI_API_KEY in .env.")
