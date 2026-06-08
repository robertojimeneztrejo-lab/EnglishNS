import hashlib
import hmac
import re
import secrets

from supabase_client import get_supabase_client

USERNAME_PATTERN = re.compile(r"^[a-zA-Z0-9_.-]{3,30}$")


def normalize_username(username: str) -> str:
    return (username or "").strip().lower()


def validate_username(username: str) -> tuple[bool, str]:
    username = normalize_username(username)
    if not USERNAME_PATTERN.match(username):
        return False, "El usuario debe tener de 3 a 30 caracteres. Usa solo letras, números, punto, guion o guion bajo."
    return True, ""


def _hash_password(password: str, salt: str | None = None) -> tuple[str, str]:
    if salt is None:
        salt = secrets.token_hex(16)
    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        120_000,
    ).hex()
    return salt, password_hash


def _pack_hash(salt: str, password_hash: str) -> str:
    return f"{salt}${password_hash}"


def _unpack_hash(stored_hash: str) -> tuple[str, str]:
    if "$" not in stored_hash:
        return "", stored_hash
    salt, password_hash = stored_hash.split("$", 1)
    return salt, password_hash


def create_user(username: str, password: str) -> tuple[bool, str]:
    username = normalize_username(username)
    valid, message = validate_username(username)
    if not valid:
        return False, message
    if len(password or "") < 6:
        return False, "La contraseña debe tener al menos 6 caracteres."

    supabase = get_supabase_client()

    existing = (
        supabase.table("users_profile")
        .select("username")
        .eq("username", username)
        .limit(1)
        .execute()
    )
    if existing.data:
        return False, "Ese usuario ya existe. Intenta iniciar sesión."

    salt, password_hash = _hash_password(password)
    supabase.table("users_profile").insert({
        "username": username,
        "password_hash": _pack_hash(salt, password_hash),
    }).execute()

    return True, "Usuario creado correctamente."


def authenticate_user(username: str, password: str) -> bool:
    username = normalize_username(username)
    if not username or not password:
        return False

    supabase = get_supabase_client()
    result = (
        supabase.table("users_profile")
        .select("password_hash")
        .eq("username", username)
        .limit(1)
        .execute()
    )
    if not result.data:
        return False

    stored = result.data[0].get("password_hash", "")
    salt, stored_hash = _unpack_hash(stored)
    if not salt or not stored_hash:
        return False

    _, attempted_hash = _hash_password(password, salt)
    return hmac.compare_digest(attempted_hash, stored_hash)
