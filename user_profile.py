from storage import load_profile, upsert_error, insert_native_expression


def update_profile_with_errors(errors: list[dict], username: str | None = None):
    for error in errors:
        mistake = error.get("mistake", "").strip()
        correction = error.get("correction", "").strip()
        explanation = error.get("note") or error.get("explanation") or error.get("category") or ""
        upsert_error(username, mistake, correction, explanation)

    return load_profile(username)


def update_profile_with_native_expressions(expressions: list[dict], username: str | None = None):
    for item in expressions:
        insert_native_expression(
            username=username,
            expression=item.get("expression", ""),
            meaning=item.get("meaning", ""),
            example=item.get("example", ""),
            tone=item.get("tone", "neutral"),
            scenario=item.get("scenario", "general"),
        )

    return load_profile(username)
