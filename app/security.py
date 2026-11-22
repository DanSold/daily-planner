import hashlib
import secrets

from pwdlib import PasswordHash

password_hasher = PasswordHash.recommended()

# Used to keep login timing similar for unknown emails.
DUMMY_PASSWORD_HASH = password_hasher.hash("dummy-password-for-timing-only")


def hash_password(password: str) -> str:
    return password_hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return password_hasher.verify(password, password_hash)


def generate_session_token() -> str:
    return secrets.token_urlsafe(32)


def hash_session_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()