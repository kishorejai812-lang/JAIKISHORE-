"""Personalized learning path with Gemini."""
from gemini_client import generate


def get_learning_recommendations(topic: str) -> str:
    prompt = (f"Create a structured learning path for the topic: {topic}.\n"
              "Organize it into Beginner, Intermediate and Advanced levels. For each level give "
              "an estimated time, key topics, and resources (videos, articles, books, practice "
              "sites). End with a short list of adaptive learning tips. Use Markdown with "
              "**bold** headings and '*' bullet points.")
    return generate(prompt)
