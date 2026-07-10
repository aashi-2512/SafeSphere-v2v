from datetime import datetime, timedelta
from jose import jwt, JWTError

from app.config import (
    JWT_SECRET,
    JWT_ALGORITHM,
    TOKEN_EXPIRY_MINUTES,
)


def create_token(session_id: str, role: str):
    """
    Creates a JWT token for a specific session and role.
    """

    expire = datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRY_MINUTES)

    payload = {
        "session_id": session_id,
        "role": role,
        "exp": expire
    }

    token = jwt.encode(
        payload,
        JWT_SECRET,
        algorithm=JWT_ALGORITHM
    )

    return token


def verify_token(token: str):
    """
    Verifies a JWT token and returns its payload.
    """

    try:
        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM]
        )

        return payload

    except JWTError:
        return None