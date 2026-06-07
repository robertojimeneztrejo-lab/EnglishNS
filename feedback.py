import json
from gemini_client import generate_text
from prompts import build_feedback_prompt, build_error_extraction_prompt, build_native_expression_extraction_prompt
from storage import save_session
from user_profile import update_profile_with_errors, update_profile_with_native_expressions


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

    native_expressions = []
    try:
        raw_json = generate_text(build_native_expression_extraction_prompt(feedback_text), temperature=0.1)
        cleaned = raw_json.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        native_expressions = json.loads(cleaned).get("expressions", [])
    except Exception:
        native_expressions = []

    profile = update_profile_with_errors(errors)
    profile = update_profile_with_native_expressions(native_expressions)
    save_session(scenario, character, level, tone, history, feedback_text)
    return feedback_text, profile
