# ============================================================
#  CodeSense Backend — AI-Powered Code Review API
#  Stack: Python + FastAPI
#  Run:   uvicorn main:app --reload
# ============================================================

import os
import json
import random
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ── App setup ──────────────────────────────────────────────
app = FastAPI(
    title="CodeSense API",
    description="AI-powered code review backend",
    version="1.0.0",
)

# ── CORS — allows your frontend (any origin) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # In production, replace * with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Request / Response models ───────────────────────────────
class ReviewRequest(BaseModel):
    code: str
    language: str = "javascript"   # default language if not sent

class ReviewResponse(BaseModel):
    score: float
    bugs: list[str]
    improvements: list[str]
    best_practices: list[str]
    language: str
    mock: bool = False             # tells the frontend if this was a real AI response


# ── Mock response — used when no OpenAI key is set ──────────
def get_mock_response(language: str) -> dict:
    """
    Returns a realistic-looking fake review.
    This lets you demo the app without an API key.
    """
    score = round(random.uniform(6.0, 9.5), 1)

    bugs_pool = [
        "Potential null reference — variable may be undefined before use.",
        "Unhandled promise rejection — async function missing try/catch.",
        "Off-by-one error in loop boundary condition.",
        "Division by zero not guarded when denominator is user input.",
        "Memory leak — event listener added but never removed.",
    ]
    improvements_pool = [
        "Cache array length outside loop to avoid repeated property lookups.",
        "Replace manual loop with a built-in higher-order function (map/filter).",
        "Extract repeated logic into a reusable helper function.",
        "Use early returns to reduce nesting depth.",
        "Consider breaking this function into smaller, single-responsibility units.",
    ]
    best_practices_pool = [
        "Use const for variables that are never reassigned.",
        "Add JSDoc / docstring comments to all public functions.",
        "Validate function inputs at the entry point.",
        "Follow consistent naming conventions throughout the file.",
        "Add unit tests for the core logic.",
    ]

    return {
        "score": score,
        "bugs": random.sample(bugs_pool, k=2),
        "improvements": random.sample(improvements_pool, k=2),
        "best_practices": random.sample(best_practices_pool, k=3),
        "language": language,
        "mock": True,
    }


# ── Real OpenAI call ────────────────────────────────────────
def get_ai_response(code: str, language: str) -> dict:
    """
    Sends the code to OpenAI and parses the structured JSON reply.
    Only called when OPENAI_API_KEY is set in environment.
    """
    try:
        # Import here so the app still starts even if openai isn't installed
        from openai import OpenAI
    except ImportError:
        raise HTTPException(
            status_code=500,
            detail="openai package not installed. Run: pip install openai",
        )

    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    prompt = f"""You are a senior software engineer. Analyze the given {language} code and provide:
1. Bugs
2. Improvements
3. Best practices
4. Score out of 10

Return ONLY a JSON object — no extra text, no markdown fences — in this exact format:
{{
  "score": <number>,
  "bugs": ["..."],
  "improvements": ["..."],
  "best_practices": ["..."]
}}

Code:
{code}"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",          # cheap + fast; swap for gpt-4o if you want
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,              # low temperature → more consistent output
        max_tokens=800,
    )

    raw = response.choices[0].message.content.strip()

    # Strip markdown fences in case the model wraps the JSON
    raw = raw.replace("```json", "").replace("```", "").strip()

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500,
            detail=f"AI returned non-JSON response: {raw[:200]}",
        )

    return {
        "score": float(data.get("score", 5.0)),
        "bugs": data.get("bugs", []),
        "improvements": data.get("improvements", []),
        "best_practices": data.get("best_practices", []),
        "language": language,
        "mock": False,
    }


# ── Health check ────────────────────────────────────────────
@app.get("/")
def root():
    """Simple health check — visit http://localhost:8000 to confirm server is up."""
    has_key = bool(os.environ.get("OPENAI_API_KEY"))
    return {
        "status": "ok",
        "service": "CodeSense API",
        "version": "1.0.0",
        "ai_mode": "openai" if has_key else "mock",
    }


# ── Main endpoint ───────────────────────────────────────────
@app.post("/review-code", response_model=ReviewResponse)
def review_code(request: ReviewRequest):
    """
    Accepts code + language, returns structured AI feedback.

    - If OPENAI_API_KEY env var is set  → calls real OpenAI API
    - Otherwise                         → returns mock data (great for dev/demo)
    """
    # Basic validation
    if not request.code or not request.code.strip():
        raise HTTPException(status_code=400, detail="Code cannot be empty.")

    if len(request.code) > 10_000:
        raise HTTPException(status_code=400, detail="Code exceeds 10,000 character limit.")

    openai_key = os.environ.get("OPENAI_API_KEY")

    if openai_key:
        # Real AI mode
        result = get_ai_response(request.code, request.language)
    else:
        # Mock mode — works with zero API key
        result = get_mock_response(request.language)

    return result
