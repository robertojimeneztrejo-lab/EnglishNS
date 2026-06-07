from datetime import datetime
from storage import load_profile, save_profile


def update_profile_with_errors(errors: list[dict]):
    profile = load_profile()
    profile["total_sessions"] = profile.get("total_sessions", 0) + 1
    profile["last_practice"] = datetime.now().isoformat(timespec="seconds")

    existing = profile.get("common_errors", [])
    for error in errors:
        mistake = error.get("mistake", "").strip()
        correction = error.get("correction", "").strip()
        if not mistake or not correction:
            continue

        found = False
        for item in existing:
            if item.get("mistake", "").lower() == mistake.lower():
                item["count"] = item.get("count", 1) + 1
                item["correction"] = correction
                item["category"] = error.get("category", item.get("category", "naturalness"))
                item["note"] = error.get("note", item.get("note", ""))
                found = True
                break
        if not found:
            existing.append({
                "mistake": mistake,
                "correction": correction,
                "category": error.get("category", "naturalness"),
                "note": error.get("note", ""),
                "count": 1,
            })

    existing = sorted(existing, key=lambda x: x.get("count", 1), reverse=True)[:25]
    profile["common_errors"] = existing
    save_profile(profile)
    return profile
