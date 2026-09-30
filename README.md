# EduGenie – Google Gemini Powered Learning Assistant

Ask questions, get simple explanations, generate quizzes, summarize text and get
learning paths. Backend: **FastAPI** · Frontend: **HTML + CSS + JS** · AI: **Google Gemini**
(+ optional local **LaMini-Flan-T5-783M** for explanations).

## Setup (VS Code)
1. Install Python 3.10+ and VS Code (with the *Python* extension). `python --version` to verify.
2. **File → Open Folder…** → select the `EduGenie` folder. Open a terminal (**Ctrl+`**).
3. Create and activate a virtual environment:
   - Windows: `python -m venv venv` then `venv\Scripts\activate`
   - macOS/Linux: `python3 -m venv venv` then `source venv/bin/activate`
   - Ctrl+Shift+P → *Python: Select Interpreter* → pick the `venv` one.
4. Install dependencies: `pip install -r requirements.txt`
   (Want a fast, light install? Remove `torch`, `transformers`, `sentencepiece` from
   requirements.txt and set `EXPLAIN_BACKEND=gemini` in `.env`.)
5. Get a free API key at https://aistudio.google.com/app/apikey and paste it into `.env`:
   `GEMINI_API_KEY=your_key`

## Run
`uvicorn main:app --reload` → open http://127.0.0.1:8000

Note: the first local explanation downloads the ~3 GB LaMini model once. Until then
(or if it fails), `EXPLAIN_BACKEND=auto` falls back to Gemini.

## Test
- Automated (no API key needed): `pytest -v`
- Manual: use the dropdown to try Q&A ("Which is the largest ocean?"), Explain
  ("Binary Search Algorithm"), Quiz ("The Pythagoras Theorem"), Summarize (paste a
  paragraph), Recommend ("SQL"). API docs: http://127.0.0.1:8000/docs

## Endpoints
`POST /qa` · `POST /explain` · `POST /quiz` · `POST /summarize` · `GET /learn/recommendations?topic=`

## Troubleshooting
- *GEMINI_API_KEY is not set* → edit `.env`, restart uvicorn.
- *404 model not found* → set `GEMINI_MODEL` in `.env` to a current model (e.g. `gemini-2.5-flash`).
- `uvicorn` not found → activate the venv first.
