"""Quiz generation: 3 MCQs (4 options each) returned as a Python list."""
import json
import re
from gemini_client import generate


def clean_json_block(raw: str) -> str:
    """Strip Markdown code fences (```json ... ```) around a JSON response."""
    raw = raw.strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw, flags=re.IGNORECASE)
    raw = re.sub(r"\s*```$", "", raw)
    return raw.strip()


def _parse_json(raw: str):
    """Parse JSON, repairing stray backslashes (e.g. LaTeX like \\sqrt or \\( ) first."""
    raw = clean_json_block(raw)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Double any backslash that is not part of a valid JSON escape sequence.
        fixed = re.sub(r'\\(?!["\\/bfnrtu]|u[0-9a-fA-F]{4})', r"\\\\", raw)
        return json.loads(fixed, strict=False)


def _plain(s) -> str:
    """Tidy math/LaTeX leftovers so text reads cleanly in the browser."""
    s = str(s).strip()
    s = re.sub(r"\\[()\[\]]", "", s)            # \( \) \[ \]
    s = s.replace("$", "").replace("\\sqrt", "√").replace("\\times", "×")
    s = s.replace("\\cdot", "·").replace("\\^", "^")
    return re.sub(r"\s+", " ", s).strip()


def _normalize(items) -> list:
    if isinstance(items, dict):
        items = items.get("quiz") or items.get("questions") or []
    quiz = []
    for it in items:
        opts = [_plain(o) for o in it.get("options", [])][:4]
        ans = _plain(it.get("answer", ""))
        if len(opts) != 4 or not it.get("question"):
            raise ValueError("Model returned a malformed question.")
        if ans.upper() in ("A", "B", "C", "D"):          # letter -> option text
            ans = opts["ABCD".index(ans.upper())]
        if ans not in opts:                              # tolerate case/whitespace drift
            match = [o for o in opts if o.lower() == ans.lower()]
            if not match:
                raise ValueError("Correct answer is not among the options.")
            ans = match[0]
        quiz.append({"question": _plain(it["question"]), "options": opts, "answer": ans})
    if not quiz:
        raise ValueError("No questions were generated.")
    return quiz[:3]


def generate_quiz(text: str) -> list:
    prompt = ("Create exactly 3 multiple-choice questions from the passage or topic below. "
              "Each question needs exactly 4 plausible options and one correct answer. "
              "Use plain text only: no LaTeX, no backslashes, no $ signs. Write math like "
              "a^2 + b^2 = c^2. "
              'Respond ONLY with JSON: [{"question": "...", "options": ["...","...","...","..."], '
              '"answer": "<exact text of the correct option>"}]\n\n'
              f"Passage/Topic:\n{text}")
    last_err = None
    for _ in range(2):                                   # one automatic retry on bad output
        raw = generate(prompt, json_mode=True)
        try:
            return _normalize(_parse_json(raw))
        except (json.JSONDecodeError, ValueError, AttributeError, TypeError) as e:
            last_err = e
    raise ValueError(f"Could not parse quiz from model output: {last_err}") from last_err