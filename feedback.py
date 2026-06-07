import json
from gemini_client import generate_text
from prompts import build_feedback_prompt, build_error_extraction_prompt, build_native_expression_extraction_prompt
from storage import save_session
from user_profile import update_profile_with_errors, update_profile_with_native_expressions


def clean_json_response(raw_text: str) -> str:
    return raw_text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()


def generate_feedback(history, scenario, character, level, tone, username: str | None = None):
    feedback_prompt = build_feedback_prompt(history, scenario, tone, level)
    feedback_text = generate_text(feedback_prompt, temperature=0.4)

    errors = []
    try:
        raw_json = generate_text(build_error_extraction_prompt(feedback_text), temperature=0.1)
        errors = json.loads(clean_json_response(raw_json)).get("errors", [])
    except Exception:
        errors = []

    native_expressions = []
    try:
        raw_json = generate_text(build_native_expression_extraction_prompt(feedback_text), temperature=0.1)
        native_expressions = json.loads(clean_json_response(raw_json)).get("expressions", [])
    except Exception:
        native_expressions = []

    profile = update_profile_with_errors(errors, username)
    profile = update_profile_with_native_expressions(native_expressions, username)
    save_session(scenario, character, level, tone, history, feedback_text, username)
    return feedback_text, profile
