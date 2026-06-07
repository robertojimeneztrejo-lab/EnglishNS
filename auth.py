import hashlib
import hmac
import json
import re
import secrets
from pathlib import Path

DATA_DIR = Path("data")
USERS_PATH = DATA_DIR / "users.json"

USERNAME_PATTERN = re.compile(r"^[a-zA-Z0-9_.-]{3,30}$")


def _ensure_data_dir():
    DATA_DIR.mkdir(exist_ok=True)


def _read_users():
    _ensure_data_dir()
    if not USERS_PATH.exists():
        return {}
    try:
        return json.loads(USERS_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def _write_users(users):
    _ensure_data_dir()
    USERS_PATH.write_text(json.dumps(users, ensure_ascii=False, indent=2), encoding="utf-8")


def normalize_username(username: str) -> str:
    return username.strip().lower()


def validate_username(username: str) -> tuple[bool, str]:
    username = normalize_username(username)
    if not USERNAME_PATTERN.match(username):
        return False, "El usuario debe tener de 3 a 30 caracteres. Usa solo letras, números, punto, guion o guion bajo."
    return True, ""


def hash_password(password: str, salt: str | None = None) -> tuple[str, str]:
    if salt is None:
        salt = secrets.token_hex(16)
    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        120_000,
    ).hex()
    return salt, password_hash


def create_user(username: str, password: str) -> tuple[bool, str]:
    username = normalize_username(username)
    valid, message = validate_username(username)
    if not valid:
        return False, message
    if len(password) < 6:
        return False, "La contraseña debe tener al menos 6 caracteres."

    users = _read_users()
    if username in users:
        return False, "Ese usuario ya existe. Intenta iniciar sesión."

    salt, password_hash = hash_password(password)
    users[username] = {
        "salt": salt,
        "password_hash": password_hash,
    }
    _write_users(users)
    return True, "Usuario creado correctamente."


def authenticate_user(username: str, password: str) -> bool:
    username = normalize_username(username)
    users = _read_users()
    user = users.get(username)
    if not user:
        return False

    _, attempted_hash = hash_password(password, user.get("salt", ""))
    return hmac.compare_digest(attempted_hash, user.get("password_hash", ""))
