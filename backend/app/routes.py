from flask import Blueprint, render_template, request, jsonify
from groq import Groq
import os

from .prompts import phase_detection_prompt, communication_prompt
from .auth_middleware import jwt_required
from .models import save_incident, get_recent_incidents

bp = Blueprint("main", __name__)


def get_client():
    """Create Groq client lazily so it always picks up the live env var."""
    api_key = os.environ.get("GROQ_API_KEY", "")
    if not api_key:
        raise ValueError("GROQ_API_KEY is not set in environment")
    return Groq(api_key=api_key)

VALID_PHASES = {"initial", "progress", "resolved"}


@bp.route("/")
def home():
    return render_template("index.html")


@bp.route("/debug")
def debug():
    """Temporary debug endpoint — remove after confirming env vars are set."""
    key = os.environ.get("GROQ_API_KEY", "")
    return jsonify({
        "GROQ_API_KEY_set": bool(key),
        "GROQ_API_KEY_prefix": key[:8] + "..." if key else "NOT SET",
    })


@bp.route("/detect-phase", methods=["POST"])
@jwt_required
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
        phase = response.choices[0].message.content.strip().lower()
        # strip any punctuation the model may add
        phase = phase.strip('"\'. \n')
        if phase not in VALID_PHASES:
            phase = "initial"
        return jsonify({"phase": phase})

    except Exception as e:
        print(f"[detect-phase] ERROR: {e}")
        return jsonify({"phase": "initial"}), 500


@bp.route("/generate", methods=["POST"])
@jwt_required
def generate():
    """
    Generate a customer communication for a specific incident phase.
    Expects:  { timeline, severity, tone, phase }
    Returns:  { phase, text, summary_entry }
    """
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
            messages=[{
                "role": "user",
                "content": communication_prompt(timeline, severity, tone, phase),
            }],
            max_tokens=1024,
        )

        result = response.choices[0].message.content
        print(f"\n[{phase.upper()}] AI RESPONSE:\n{result}\n")

        customer_message = ""
        summary_entry    = ""

        if "CUSTOMER_MESSAGE:" in result:
            after_cm = result.split("CUSTOMER_MESSAGE:")[1]
            if "SUMMARY_ENTRY:" in after_cm:
                customer_message = after_cm.split("SUMMARY_ENTRY:")[0].strip()
                summary_entry    = after_cm.split("SUMMARY_ENTRY:")[1].strip()
            else:
                customer_message = after_cm.strip()

        return jsonify({
            "phase":         phase,
            "text":          customer_message,
            "summary_entry": summary_entry,
        })

    except Exception as e:
        print(f"[generate] ERROR: {e}")
        return jsonify({
            "phase":         phase,
            "text":          f"Error: {e}",
            "summary_entry": f"Error: {e}",
        }), 500


@bp.route("/incidents/save", methods=["POST"])
@jwt_required
def save_incident_route():
    """Save a completed incident to history."""
    data     = request.get_json() or {}
    severity = data.get("severity", "Low")
    entries  = data.get("entries", [])
    user_id  = request.current_user.get("sub")

    if not entries:
        return jsonify({"error": "No entries provided"}), 400

    ok = save_incident(user_id, severity, entries)
    if ok:
        return jsonify({"saved": True}), 201
    return jsonify({"error": "Failed to save incident"}), 500


@bp.route("/incidents", methods=["GET"])
@jwt_required
def get_incidents_route():
    """Return last 5 incidents for the logged-in user."""
    user_id = request.current_user.get("sub")
    incidents = get_recent_incidents(user_id, limit=5)
    return jsonify({"incidents": incidents}), 200
