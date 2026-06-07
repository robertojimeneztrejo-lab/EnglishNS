import json
from gemini_client import generate_text
from prompts import build_feedback_prompt, build_error_extraction_prompt
from storage import save_session
from user_profile import update_profile_with_errors


def generate_feedback(history, scenario, character, level, tone):
    feedback_prompt = build_feedback_prompt(history, scenario, tone, level)
    feedback_text = generate_text(feedback_prompt, temperature=0.4)

    errors = []
    try:
        raw_json = generate_text(build_error_extraction_prompt(feedback_text), temperature=0.1)
        cleaned = raw_json.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        errors = json.loads(cleaned).get("errors", [])
    except Exception:
        errors = []

    profile = update_profile_with_errors(errors)
    save_session(scenario, character, level, tone, history, feedback_text)
    return feedback_text, profile
