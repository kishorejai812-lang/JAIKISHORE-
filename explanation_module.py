"""Concept explanation using the local LaMini-Flan-T5-783M model (Gemini fallback)."""
import os
from gemini_client import generate

_pipe = None


def _local_explain(topic: str) -> str:
    global _pipe
    if _pipe is None:
        from transformers import pipeline  # imported lazily: heavy dependency
        _pipe = pipeline("text2text-generation",
                         model=os.getenv("LOCAL_MODEL", "MBZUAI/LaMini-Flan-T5-783M"))
    out = _pipe(f"Explain the following concept in simple words for a beginner: {topic}",
                max_new_tokens=220, do_sample=False, no_repeat_ngram_size=3)
    text = out[0]["generated_text"].strip()
    if not text:
        raise RuntimeError("Local model produced no output.")
    return text


def _gemini_explain(topic: str) -> str:
    return generate("Explain this concept simply, in under 150 words, with one everyday "
                    f"analogy, for a beginner: {topic}")


def explain_concept(topic: str) -> str:
    backend = os.getenv("EXPLAIN_BACKEND", "auto").lower()
    if backend == "gemini":
        return _gemini_explain(topic)
    if backend == "local":
        return _local_explain(topic)
    try:
        return _local_explain(topic)
    except Exception as e:  # torch/transformers missing, download failed, etc.
        print(f"[EduGenie] Local model unavailable ({e}); using Gemini.")
        return _gemini_explain(topic)
