"""EduGenie - FastAPI application. Run: uvicorn main:app --reload"""
from pathlib import Path
from fastapi import FastAPI, Request, Query
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from qna import answer_question
from explanation_module import explain_concept
from quiz_module import generate_quiz
from summary_module import summarize_text
from learning_path import get_learning_recommendations

BASE_DIR = Path(__file__).resolve().parent
app = FastAPI(title="EduGenie", description="Google Gemini powered learning assistant")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


class QARequest(BaseModel):
    question: str = ""


class ExplainRequest(BaseModel):
    topic: str = ""


class TextRequest(BaseModel):
    text: str = ""


def _err(msg: str, code: int):
    return JSONResponse(content={"error": msg}, status_code=code)


def _run(fn, arg: str, empty_msg: str):
    """Validate input, run a module function, and map failures to JSON errors."""
    arg = (arg or "").strip()
    if not arg:
        return None, _err(empty_msg, 400)
    try:
        return fn(arg), None
    except ValueError as e:
        return None, _err(str(e), 502)
    except Exception as e:
        return None, _err(f"AI service error: {e}", 503)


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(request, "index.html")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/qa")
def qa_api(req: QARequest):
    res, err = _run(answer_question, req.question, "Please provide a question.")
    return err or {"answer": res}


@app.post("/explain")
def explain_api(req: ExplainRequest):
    res, err = _run(explain_concept, req.topic, "Please provide a topic to explain.")
    return err or {"explanation": res}


@app.post("/quiz")
def quiz_api(req: TextRequest):
    res, err = _run(generate_quiz, req.text, "Please provide text or a topic for the quiz.")
    return err or {"quiz": res}


@app.post("/summarize")
def summarize_api(req: TextRequest):
    res, err = _run(summarize_text, req.text, "Please provide text to summarize.")
    return err or {"summary": res}


@app.get("/learn/recommendations")
def learning_recommendation_api(topic: str = Query(..., min_length=1)):
    res, err = _run(get_learning_recommendations, topic, "Please provide a topic.")
    return err or {"topic": topic, "recommendation": res}
