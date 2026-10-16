import os
from datetime import UTC, datetime, timedelta

import bcrypt
import jwt

SECRET_KEY = os.getenv("JWT_SECRET", "dev-only-secret-change-me-in-production")
ALGORITHM = "HS256"
TOKEN_LIFETIME = timedelta(hours=8)


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode(), password_hash.encode())


def create_token(username: str, role: str) -> str:
    payload = {"sub": username, "role": role, "exp": datetime.now(UTC) + TOKEN_LIFETIME}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    """Raises jwt.InvalidTokenError if the token is invalid or expired."""
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
