"""
Auth blueprint — /auth/register and /auth/login
"""
from flask import Blueprint, request, jsonify, render_template
from .models import create_user, get_user_by_username, verify_password
from .auth_middleware import create_token

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/register-page")
def register_page():
    return render_template("register.html")


@auth_bp.route("/login-page")
def login_page():
    return render_template("login.html")


@auth_bp.route("/register", methods=["POST"])
def register():
    data     = request.get_json() or {}
    username = data.get("username", "").strip()
    email    = data.get("email", "").strip()
    password = data.get("password", "")

    if not username or not email or not password:
        return jsonify({"error": "username, email and password are required"}), 400
    if len(username) < 3:
        return jsonify({"error": "Username must be at least 3 characters"}), 400
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400
    if "@" not in email:
        return jsonify({"error": "Invalid email address"}), 400

    try:
        user = create_user(username, email, password)
        if user is None:
            return jsonify({"error": "Username or email already taken"}), 409
        token = create_token(user["id"], user["username"])
        return jsonify({"token": token, "username": user["username"]}), 201
    except Exception as e:
        print(f"[register] ERROR: {e}")
        return jsonify({"error": str(e)}), 500


@auth_bp.route("/login", methods=["POST"])
def login():
    data     = request.get_json() or {}
    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not username or not password:
        return jsonify({"error": "username and password are required"}), 400

    try:
        user = get_user_by_username(username)
        if not user or not verify_password(password, user["password"]):
            return jsonify({"error": "Invalid username or password"}), 401
        token = create_token(user["id"], user["username"])
        return jsonify({"token": token, "username": user["username"]}), 200
    except Exception as e:
        print(f"[login] ERROR: {e}")
        return jsonify({"error": str(e)}), 500
