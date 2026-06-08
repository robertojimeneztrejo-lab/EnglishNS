from datetime import datetime
from typing import Any

from supabase_client import get_supabase_client


def default_profile() -> dict[str, Any]:
    return {
        "total_sessions": 0,
        "common_errors": [],
        "native_expressions": [],
        "strengths": [],
        "last_practice": None,
    }


def _safe_username(username: str | None) -> str:
    return (username or "default").strip().lower() or "default"


def save_session(scenario, character, level, tone, history, feedback, username: str | None = None):
    supabase = get_supabase_client()
    username = _safe_username(username)

    supabase.table("sessions").insert({
        "username": username,
        "scenario": scenario,
        "character_name": character,
        "conversation": history,
        "feedback": {
            "text": feedback,
            "level": level,
            "tone": tone,
        },
    }).execute()


def load_sessions(limit=10, username: str | None = None):
    supabase = get_supabase_client()
    username = _safe_username(username)

    result = (
        supabase.table("sessions")
        .select("created_at, scenario, character_name, conversation, feedback")
        .eq("username", username)
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )

    sessions = []
    for row in result.data or []:
        feedback = row.get("feedback") or {}
        if isinstance(feedback, str):
            feedback = {"text": feedback}
        sessions.append({
            "created_at": row.get("created_at", ""),
            "scenario": row.get("scenario", ""),
            "character": row.get("character_name", ""),
            "level": feedback.get("level", ""),
            "tone": feedback.get("tone", ""),
            "history": row.get("conversation", []),
            "feedback": feedback.get("text", ""),
        })
    return sessions


def load_profile(username: str | None = None):
    supabase = get_supabase_client()
    username = _safe_username(username)
    profile = default_profile()

    sessions = (
        supabase.table("sessions")
        .select("created_at")
        .eq("username", username)
        .order("created_at", desc=True)
        .limit(1000)
        .execute()
    )
    session_rows = sessions.data or []
    profile["total_sessions"] = len(session_rows)
    if session_rows:
        profile["last_practice"] = session_rows[0].get("created_at")

    errors = (
        supabase.table("error_profile")
        .select("error, correction, explanation, frequency, updated_at")
        .eq("username", username)
        .order("frequency", desc=True)
        .limit(25)
        .execute()
    )
    profile["common_errors"] = [
        {
            "mistake": row.get("error", ""),
            "correction": row.get("correction", ""),
            "note": row.get("explanation", ""),
            "count": row.get("frequency", 1),
            "updated_at": row.get("updated_at", ""),
        }
        for row in (errors.data or [])
    ]

    expressions = (
        supabase.table("native_expressions")
        .select("expression, meaning, example, tone, scenario, created_at")
        .eq("username", username)
        .order("created_at", desc=True)
        .limit(50)
        .execute()
    )
    # Agrupación simple por expresión para mostrar frecuencia aunque la tabla guarde eventos individuales.
    grouped = {}
    for row in expressions.data or []:
        key = (row.get("expression") or "").lower().strip()
        if not key:
            continue
        if key not in grouped:
            grouped[key] = {
                "expression": row.get("expression", ""),
                "meaning": row.get("meaning", ""),
                "scenario": row.get("scenario", "general"),
                "tone": row.get("tone", "neutral"),
                "example": row.get("example", ""),
                "count": 1,
                "last_seen": row.get("created_at", ""),
            }
        else:
            grouped[key]["count"] += 1
    profile["native_expressions"] = sorted(grouped.values(), key=lambda x: x.get("count", 1), reverse=True)

    return profile


def save_profile(profile, username: str | None = None):
    # La versión Supabase no guarda perfiles como archivo único.
    # El perfil se reconstruye desde sessions, error_profile y native_expressions.
    return None


def upsert_error(username: str | None, mistake: str, correction: str, explanation: str = ""):
    supabase = get_supabase_client()
    username = _safe_username(username)
    mistake = (mistake or "").strip()
    correction = (correction or "").strip()
    if not mistake or not correction:
        return

    existing = (
        supabase.table("error_profile")
        .select("id, frequency")
        .eq("username", username)
        .eq("error", mistake)
        .limit(1)
        .execute()
    )

    now = datetime.now().isoformat(timespec="seconds")
    if existing.data:
        row = existing.data[0]
        supabase.table("error_profile").update({
            "correction": correction,
            "explanation": explanation,
            "frequency": int(row.get("frequency") or 1) + 1,
            "updated_at": now,
        }).eq("id", row["id"]).execute()
    else:
        supabase.table("error_profile").insert({
            "username": username,
            "error": mistake,
            "correction": correction,
            "explanation": explanation,
            "frequency": 1,
            "updated_at": now,
        }).execute()


def insert_native_expression(username: str | None, expression: str, meaning: str = "", example: str = "", tone: str = "neutral", scenario: str = "general"):
    supabase = get_supabase_client()
    username = _safe_username(username)
    expression = (expression or "").strip()
    if not expression:
        return

    supabase.table("native_expressions").insert({
        "username": username,
        "expression": expression,
        "meaning": meaning or "",
        "example": example or "",
        "tone": tone or "neutral",
        "scenario": scenario or "general",
    }).execute()
