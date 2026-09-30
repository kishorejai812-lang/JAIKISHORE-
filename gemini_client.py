"""Shared Google Gemini helper used by every cloud-powered module.

Handles temporary Google outages (503 UNAVAILABLE / 429 rate limits) by retrying
with exponential backoff, then falling back to other models if needed.
"""
import os
import time
from dotenv import load_dotenv

load_dotenv()
_client = None

TRANSIENT = ("503", "UNAVAILABLE", "429", "RESOURCE_EXHAUSTED", "500", "504",
             "overloaded", "high demand", "DEADLINE", "timed out", "timeout")


def model_name() -> str:
    return os.getenv("GEMINI_MODEL", "gemini-3.8-flash")


def _models_to_try() -> list:
    fallbacks = os.getenv("GEMINI_FALLBACK_MODELS", "gemini-3.7-flash,gemini-3.5-flash-lite")
    names = [model_name()] + [m.strip() for m in fallbacks.split(",") if m.strip()]
    return list(dict.fromkeys(names))  # de-duplicate, keep order


def _get_client():
    global _client
    if _client is None:
        key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not key or key == "your_api_key_here":
            raise RuntimeError("GEMINI_API_KEY is not set. Add your key to the .env file.")
        from google import genai
        _client = genai.Client(api_key=key)
    return _client


def _is_transient(err: Exception) -> bool:
    text = str(err)
    return any(t.lower() in text.lower() for t in TRANSIENT)


def generate(prompt: str, json_mode: bool = False) -> str:
    """Send a prompt to Gemini and return the stripped text response."""
    config = {"response_mime_type": "application/json"} if json_mode else None
    retries = int(os.getenv("GEMINI_RETRIES", "3"))
    last_err = None
    for model in _models_to_try():
        for attempt in range(retries + 1):
            try:
                resp = _get_client().models.generate_content(
                    model=model, contents=prompt, config=config)
                text = (resp.text or "").strip()
                if not text:
                    raise RuntimeError("Gemini returned an empty response.")
                return text
            except RuntimeError as e:
                if "GEMINI_API_KEY" in str(e):
                    raise                      # config problem: retrying won't help
                last_err = e
                break
            except Exception as e:
                last_err = e
                if _is_transient(e) and attempt < retries:
                    time.sleep(2 ** attempt)   # 1s, 2s, 4s
                    continue
                break                          # 404 / overloaded for good -> next model
        print(f"[EduGenie] Model {model} failed ({str(last_err)[:80]}); trying next...")
    raise RuntimeError(f"All Gemini models failed. Last error: {last_err}")