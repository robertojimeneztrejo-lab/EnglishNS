import json
from pathlib import Path
from datetime import datetime

DATA_DIR = Path("data")
PROFILE_PATH = DATA_DIR / "learning_profile.json"
SESSIONS_PATH = DATA_DIR / "sessions.json"


def ensure_data_dir():
    DATA_DIR.mkdir(exist_ok=True)


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
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def load_profile():
    return read_json(PROFILE_PATH, {
        "total_sessions": 0,
        "common_errors": [],
        "native_expressions": [],
        "strengths": [],
        "last_practice": None,
    })


def save_profile(profile):
    write_json(PROFILE_PATH, profile)


def save_session(scenario, character, level, tone, history, feedback):
    sessions = read_json(SESSIONS_PATH, [])
    sessions.append({
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "scenario": scenario,
        "character": character,
        "level": level,
        "tone": tone,
        "history": history,
        "feedback": feedback,
    })
    write_json(SESSIONS_PATH, sessions)


def load_sessions(limit=10):
    sessions = read_json(SESSIONS_PATH, [])
    return list(reversed(sessions[-limit:]))
