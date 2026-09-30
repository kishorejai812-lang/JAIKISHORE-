"""Summarization with Gemini."""
from gemini_client import generate


def summarize_text(text: str) -> str:
    prompt = ("Summarize the following text in simple language for a student. Keep the key "
              f"points, remove redundancy, and use short bullet points if helpful:\n\n{text}")
    return generate(prompt)
