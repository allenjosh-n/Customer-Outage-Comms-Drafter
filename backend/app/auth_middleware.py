"""
JWT middleware — provides @jwt_required decorator.
"""
import os
import jwt
from functools import wraps
from flask import request, jsonify

SECRET_KEY = os.environ.get("JWT_SECRET", "change-me-in-production")


def create_token(user_id: int, username: str) -> str:
    import datetime
    payload = {
        "sub":      user_id,
        "username": username,
        "exp":      datetime.datetime.utcnow() + datetime.timedelta(hours=12),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def decode_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])


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
        # Attach decoded payload to request context
        request.current_user = payload
        return f(*args, **kwargs)
    return decorated
