"""
JWT middleware — provides @jwt_required decorator.
"""
import os
import datetime
import jwt
from functools import wraps
from flask import request, jsonify


def _secret() -> str:
    """Read JWT_SECRET lazily so it works on both local (.env) and Vercel (env var)."""
    return os.environ.get("JWT_SECRET", "change-me-in-production")


def create_token(user_id: int, username: str) -> str:
    payload = {
        "sub":      user_id,
        "username": username,
        "exp":      datetime.datetime.utcnow() + datetime.timedelta(hours=12),
    }
    return jwt.encode(payload, _secret(), algorithm="HS256")


def decode_token(token: str) -> dict:
    return jwt.decode(token, _secret(), algorithms=["HS256"])


def jwt_required(f):
    """Decorator — rejects requests without a valid Bearer token."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or invalid Authorization header"}), 401
        token = auth_header.split(" ", 1)[1]
        try:
            payload = decode_token(token)
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired — please log in again"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
        request.current_user = payload
        return f(*args, **kwargs)
    return decorated
