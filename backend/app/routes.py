from flask import Blueprint, render_template, request, jsonify
from groq import Groq

from backend.config import GROQ_API_KEY
from .prompts import phase_detection_prompt, communication_prompt

bp = Blueprint("main", __name__)
client = Groq(api_key=GROQ_API_KEY)

VALID_PHASES = {"initial", "progress", "resolved"}


@bp.route("/")
def home():
    return render_template("index.html")


@bp.route("/detect-phase", methods=["POST"])
def detect_phase():
   
    data     = request.get_json()
    timeline = (data or {}).get("timeline", "").strip()

    if not timeline:
        return jsonify({"phase": "initial"})

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": phase_detection_prompt(timeline)}],
            max_tokens=5,
            temperature=0,
        )
        phase = response.choices[0].message.content.strip().lower()
        if phase not in VALID_PHASES:
            phase = "initial"
        return jsonify({"phase": phase})

    except Exception as e:
        print(f"[detect-phase] ERROR: {e}")
        return jsonify({"phase": "initial"}), 500


@bp.route("/generate", methods=["POST"])
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
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{
                "role": "user",
                "content": communication_prompt(timeline, severity, tone, phase),
            }],
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
