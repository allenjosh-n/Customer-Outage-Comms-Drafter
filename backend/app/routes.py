from flask import Blueprint, render_template, request, jsonify
from groq import Groq
import os

from .prompts import phase_detection_prompt, communication_prompt
from .auth_middleware import jwt_required, role_required
from .models import save_incident, get_recent_incidents, get_all_users, update_user_role

bp = Blueprint("main", __name__)

VALID_PHASES = {"initial", "progress", "resolved"}
VALID_ROLES  = {"owner", "incident_manager", "viewer"}


def get_client():
    api_key = os.environ.get("GROQ_API_KEY", "")
    if not api_key:
        raise ValueError("GROQ_API_KEY is not set in environment")
    return Groq(api_key=api_key)


@bp.route("/")
def home():
    return render_template("index.html")


@bp.route("/debug")
def debug():
    key = os.environ.get("GROQ_API_KEY", "")
    return jsonify({
        "GROQ_API_KEY_set": bool(key),
        "GROQ_API_KEY_prefix": key[:8] + "..." if key else "NOT SET",
    })


# ── AI routes (owner + incident_manager only) ─────────────────────────────────

@bp.route("/detect-phase", methods=["POST"])
@role_required("owner", "incident_manager")
def detect_phase():
    data     = request.get_json()
    timeline = (data or {}).get("timeline", "").strip()

    if not timeline:
        return jsonify({"phase": "initial"})

    try:
        client = get_client()
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[{"role": "user", "content": phase_detection_prompt(timeline)}],
            max_tokens=100,
            temperature=0,
        )
        phase = response.choices[0].message.content.strip().lower().strip('"\'. \n')
        if phase not in VALID_PHASES:
            phase = "initial"
        return jsonify({"phase": phase})
    except Exception as e:
        print(f"[detect-phase] ERROR: {e}")
        return jsonify({"phase": "initial"}), 500


@bp.route("/generate", methods=["POST"])
@role_required("owner", "incident_manager")
def generate():
    data     = request.get_json()
    timeline = (data or {}).get("timeline", "")
    severity = (data or {}).get("severity", "Low")
    tone     = (data or {}).get("tone", "Calm")
    phase    = (data or {}).get("phase", "initial")

    if phase not in VALID_PHASES:
        phase = "initial"

    try:
        client = get_client()
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[{"role": "user", "content": communication_prompt(timeline, severity, tone, phase)}],
            max_tokens=1024,
        )
        result = response.choices[0].message.content
        customer_message = ""
        summary_entry    = ""

        if "CUSTOMER_MESSAGE:" in result:
            after_cm = result.split("CUSTOMER_MESSAGE:")[1]
            if "SUMMARY_ENTRY:" in after_cm:
                customer_message = after_cm.split("SUMMARY_ENTRY:")[0].strip()
                summary_entry    = after_cm.split("SUMMARY_ENTRY:")[1].strip()
            else:
                customer_message = after_cm.strip()

        return jsonify({"phase": phase, "text": customer_message, "summary_entry": summary_entry})
    except Exception as e:
        print(f"[generate] ERROR: {e}")
        return jsonify({"phase": phase, "text": f"Error: {e}", "summary_entry": f"Error: {e}"}), 500


# ── Incident history (all authenticated users can read) ────────────────────────

@bp.route("/incidents/save", methods=["POST"])
@role_required("owner", "incident_manager")
def save_incident_route():
    data       = request.get_json() or {}
    severity   = data.get("severity", "Low")
    entries    = data.get("entries", [])
    drafted_by = request.current_user.get("username", "unknown")

    if not entries:
        return jsonify({"error": "No entries provided"}), 400

    ok = save_incident(drafted_by, severity, entries)
    return jsonify({"saved": ok}), 201 if ok else 500


@bp.route("/incidents", methods=["GET"])
@jwt_required
def get_incidents_route():
    """All authenticated roles can view shared incident history."""
    try:
        incidents = get_recent_incidents(limit=5)
        return jsonify({"incidents": incidents}), 200
    except Exception as e:
        print(f"[incidents] ERROR: {e}")
        return jsonify({"error": str(e), "incidents": []}), 500


# ── Admin routes (owner only) ──────────────────────────────────────────────────

@bp.route("/admin/users", methods=["GET"])
@role_required("owner")
def admin_list_users():
    """Return all users with their roles."""
    users = get_all_users()
    return jsonify({"users": users}), 200


@bp.route("/admin/users/<int:user_id>/role", methods=["PATCH"])
@role_required("owner")
def admin_update_role(user_id):
    """Owner changes a user's role. Cannot change another owner's role."""
    data     = request.get_json() or {}
    new_role = data.get("role", "").strip()

    if new_role not in VALID_ROLES:
        return jsonify({"error": f"Invalid role. Must be one of: {', '.join(VALID_ROLES)}"}), 400
    if new_role == "owner":
        return jsonify({"error": "Cannot promote to owner — there can only be one owner"}), 400

    # Get current role to prevent demoting another owner
    all_users = get_all_users()
    target = next((u for u in all_users if u["id"] == user_id), None)
    if not target:
        return jsonify({"error": "User not found"}), 404
    if target["role"] == "owner":
        return jsonify({"error": "Cannot change the owner's role"}), 403
    # Prevent owner from changing their own role
    if user_id == request.current_user.get("sub"):
        return jsonify({"error": "You cannot change your own role"}), 403

    ok = update_user_role(user_id, new_role)
    return jsonify({"updated": ok}), 200 if ok else 500
