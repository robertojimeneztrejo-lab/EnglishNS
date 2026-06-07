import json
import re
from pathlib import Path
from datetime import datetime

DATA_DIR = Path("data")
USERS_DATA_DIR = DATA_DIR / "user_data"


def ensure_data_dir():
    DATA_DIR.mkdir(exist_ok=True)
    USERS_DATA_DIR.mkdir(exist_ok=True)


def safe_username(username: str | None) -> str:
    username = (username or "default").strip().lower()
    username = re.sub(r"[^a-zA-Z0-9_.-]", "_", username)
    return username or "default"


def get_user_dir(username: str | None):
    ensure_data_dir()
    user_dir = USERS_DATA_DIR / safe_username(username)
    user_dir.mkdir(exist_ok=True)
    return user_dir


def get_profile_path(username: str | None):
    return get_user_dir(username) / "learning_profile.json"


def get_sessions_path(username: str | None):
    return get_user_dir(username) / "sessions.json"


def read_json(path: Path, default):
    ensure_data_dir()
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return default


def write_json(path: Path, data):
    ensure_data_dir()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def default_profile():
    return {
        "total_sessions": 0,
        "common_errors": [],
        "native_expressions": [],
        "strengths": [],
        "last_practice": None,
    }


def load_profile(username: str | None = None):
    return read_json(get_profile_path(username), default_profile())


def save_profile(profile, username: str | None = None):
    write_json(get_profile_path(username), profile)


def save_session(scenario, character, level, tone, history, feedback, username: str | None = None):
    sessions = read_json(get_sessions_path(username), [])
    sessions.append({
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "scenario": scenario,
        "character": character,
        "level": level,
        "tone": tone,
        "history": history,
        "feedback": feedback,
    })
    write_json(get_sessions_path(username), sessions)


def load_sessions(limit=10, username: str | None = None):
    sessions = read_json(get_sessions_path(username), [])
    return list(reversed(sessions[-limit:]))
