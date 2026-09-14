"""
JWT middleware — @jwt_required and @role_required decorators.
"""
import os
import datetime
import jwt
from functools import wraps
from flask import request, jsonify

VALID_ROLES = {"owner", "incident_manager", "viewer"}


def _secret() -> str:
    return os.environ.get("JWT_SECRET", "change-me-in-production")


def create_token(user_id: int, username: str, role: str) -> str:
    payload = {
        "sub":      user_id,
        "username": username,
        "role":     role,
        "exp":      datetime.datetime.utcnow() + datetime.timedelta(hours=12),
    }
    return jwt.encode(payload, _secret(), algorithm="HS256")


def decode_token(token: str) -> dict:
    return jwt.decode(token, _secret(), algorithms=["HS256"])


def jwt_required(f):
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


def role_required(*allowed_roles):
    """Decorator — only allows users with one of the specified roles."""
    def decorator(f):
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
            if payload.get("role") not in allowed_roles:
                return jsonify({"error": "Access denied — insufficient permissions"}), 403
            request.current_user = payload
            return f(*args, **kwargs)
        return decorated
    return decorator
