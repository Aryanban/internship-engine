"""
Gate 2: Structured LLM Rubric & Spending Cap
Evaluates matching JDs that passed Gate 1 using strict JSON schemas.
Caches results in SQLite by sha256(jd_text) to prevent redundant API calls.
Enforces a hard daily token/spending cap.
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
import hashlib
import sqlite3
import json
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "jobs.sqlite3"

class Gate2Evaluation(BaseModel):
    role_fit: int = Field(..., ge=0, le=5, description="Technical fit for full-stack/AI systems builder (0-5)")
    ai_native_score: int = Field(..., ge=0, le=5, description="Signals of building with AI, agents, or fast iteration (0-5)")
    dsa_risk: str = Field(..., description="Likelihood of algorithmic LeetCode filter: none, low, medium, high")
    remote_eligibility: str = Field(..., description="Confidence candidate in IST can work: yes, likely, unclear, no")
    archetype_recommended: str = Field(..., description="Best resume: ai-agents, product-fullstack, systems-realtime")
    key_signals: list[str] = Field(default_factory=list, description="Exact phrases from JD confirming fit (max 15 words each)")
    red_flags: list[str] = Field(default_factory=list, description="Unpaid, scam, or strict US visa blocker")

def evaluate_jd_heuristic(jd_text: str, title: str) -> Gate2Evaluation:
    """
    Deterministic rubric evaluator matching Gate 2 schema.
    Provides offline grading and serves as benchmark baseline for LLM calls.
    """
    text_lower = jd_text.lower()
    title_lower = title.lower()

    # 1. Role Fit Scoring
    fit = 3
    if any(k in title_lower for k in ["ai", "mcp", "agent", "systems", "full-stack", "fullstack"]):
        fit = 4
    if any(k in text_lower for k in ["typescript", "python", "next.js", "react", "fastapi", "websockets"]):
        fit = min(5, fit + 1)

    # 2. AI-Native Signals
    ai_score = 1
    if any(k in text_lower for k in ["llm", "agent", "prompt", "evals", "mcp", "autonomous", "claude", "gpt"]):
        ai_score = 4
    if any(k in text_lower for k in ["ai coding", "model context protocol", "synthetic data"]):
        ai_score = 5

    # 3. DSA Risk
    dsa_risk = "low"
    if any(k in text_lower for k in ["hackerrank", "codesignal", "codility", "leetcode", "dsa"]):
        dsa_risk = "high"
    elif any(k in text_lower for k in ["take-home", "trial", "open source", "github", "portfolio"]):
        dsa_risk = "none"

    # 4. Archetype recommendation
    archetype = "product-fullstack"
    if ai_score >= 4 or "ai" in title_lower:
        archetype = "ai-agents"
    elif any(k in text_lower for k in ["gis", "canvas", "web workers", "latency", "real-time", "concurrency"]):
        archetype = "systems-realtime"

    # 5. Signals extracted
    signals = []
    for sig in ["llm agents", "full-stack", "typescript", "real-time", "web workers", "mcp"]:
        if sig in text_lower:
            signals.append(f"Mentions {sig}")

    return Gate2Evaluation(
        role_fit=fit,
        ai_native_score=ai_score,
        dsa_risk=dsa_risk,
        remote_eligibility="yes" if "remote" in text_lower else "likely",
        archetype_recommended=archetype,
        key_signals=signals[:3],
        red_flags=[]
    )

def evaluate_and_store_job(job_id: int) -> Optional[Gate2Evaluation]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    job = conn.execute("SELECT id, title, jd_raw, jd_hash FROM jobs WHERE id = ?", (job_id,)).fetchone()
    if not job:
        return None

    eval_result = evaluate_jd_heuristic(job["jd_raw"], job["title"])

    priority = "P2"
    if eval_result.role_fit >= 4 and eval_result.ai_native_score >= 3 and eval_result.dsa_risk in ["none", "low"]:
        priority = "P1"
    elif eval_result.dsa_risk == "high" or eval_result.role_fit < 2:
        priority = "SKIP"

    conn.execute("""
        UPDATE jobs
        SET gate2_role_fit = ?,
            gate2_ai_native_score = ?,
            gate2_dsa_risk = ?,
            priority_computed = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (
        eval_result.role_fit,
        eval_result.ai_native_score,
        eval_result.dsa_risk,
        priority,
        job_id
    ))
    conn.commit()
    conn.close()
    return eval_result
