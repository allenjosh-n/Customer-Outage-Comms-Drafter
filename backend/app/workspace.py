"""
Collaborative Incident Workspace blueprint.
Routes:
  GET  /workspace-page               — list page (HTML)
  GET  /workspace-page/<id>          — detail page (HTML)
  POST /workspace                    — create workspace (JSON API)
  GET  /workspace                    — list workspaces (JSON API)
  GET  /workspace/<id>               — get workspace detail (JSON API)
  POST /workspace/<id>/updates       — add update + AI generate
  POST /workspace/<id>/members       — add collaborator
  DELETE /workspace/<id>/members/<uid> — remove collaborator
  PATCH /workspace/<id>/status       — close workspace
"""
from flask import Blueprint, request, jsonify, render_template
from groq import Groq
import os

from .auth_middleware import jwt_required, role_required
from .models import (
    create_workspace, get_all_workspaces, get_workspace,
    get_workspace_members, add_workspace_member, remove_workspace_member,
    add_workspace_update, close_workspace, get_all_users,
)
from .prompts import phase_detection_prompt, communication_prompt

workspace_bp = Blueprint("workspace", __name__)

VALID_PHASES = {"initial", "progress", "resolved"}


def get_client():
    api_key = os.environ.get("GROQ_API_KEY", "")
    if not api_key:
        raise ValueError("GROQ_API_KEY is not set")
    return Groq(api_key=api_key)


def _is_member(workspace_id: int, user_id: int) -> bool:
    members = get_workspace_members(workspace_id)
    return any(m["user_id"] == user_id for m in members)


# ── HTML pages ────────────────────────────────────────────────────────────────

@workspace_bp.route("/workspace-page")
@jwt_required
def workspace_list_page():
    return render_template("workspace_list.html")


@workspace_bp.route("/workspace-page/<int:workspace_id>")
@jwt_required
def workspace_detail_page(workspace_id):
    return render_template("workspace_detail.html", workspace_id=workspace_id)


# ── JSON API ──────────────────────────────────────────────────────────────────

@workspace_bp.route("/workspace", methods=["POST"])
@role_required("owner", "incident_manager")
def create_workspace_route():
    data      = request.get_json() or {}
    title     = data.get("title", "").strip()
    severity  = data.get("severity", "Medium")
    user_id   = request.current_user.get("sub")
    username  = request.current_user.get("username", "")

    if not title:
        return jsonify({"error": "Title is required"}), 400

    try:
        ws = create_workspace(title, severity, username, user_id)
        return jsonify({"workspace": ws}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@workspace_bp.route("/workspace", methods=["GET"])
@role_required("owner", "incident_manager")
def list_workspaces_route():
    workspaces = get_all_workspaces()
    return jsonify({"workspaces": workspaces}), 200


@workspace_bp.route("/workspace/<int:workspace_id>", methods=["GET"])
@role_required("owner", "incident_manager")
def get_workspace_route(workspace_id):
    ws = get_workspace(workspace_id)
    if not ws:
        return jsonify({"error": "Workspace not found"}), 404
    # Also return all users for the "add member" dropdown
    all_users = [u for u in get_all_users() if u["role"] in ("owner", "incident_manager")]
    member_ids = {m["user_id"] for m in ws["members"]}
    ws["addable_users"] = [u for u in all_users if u["id"] not in member_ids]
    return jsonify({"workspace": ws}), 200


@workspace_bp.route("/workspace/<int:workspace_id>/updates", methods=["POST"])
@role_required("owner", "incident_manager")
def add_update_route(workspace_id):
    user_id  = request.current_user.get("sub")
    username = request.current_user.get("username", "")
    role     = request.current_user.get("role", "")

    ws = get_workspace(workspace_id)
    if not ws:
        return jsonify({"error": "Workspace not found"}), 404
    if ws["status"] == "closed":
        return jsonify({"error": "This workspace is closed"}), 403
    # Only members can add updates (owners bypass membership check)
    if role != "owner" and not _is_member(workspace_id, user_id):
        return jsonify({"error": "You are not a member of this workspace"}), 403

    data     = request.get_json() or {}
    timeline = data.get("timeline", "").strip()
    severity = data.get("severity", "Medium")
    tone     = data.get("tone", "Empathetic")

    if not timeline:
        return jsonify({"error": "Timeline entry is required"}), 400

    try:
        # Stage 1 — detect phase
        client = get_client()
        phase_resp = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[{"role": "user", "content": phase_detection_prompt(timeline)}],
            max_tokens=100,
            temperature=0,
        )
        phase = phase_resp.choices[0].message.content.strip().lower().strip('"\'. \n')
        if phase not in VALID_PHASES:
            phase = "initial"

        # Stage 2 — generate customer message
        gen_resp = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[{"role": "user", "content": communication_prompt(timeline, severity, tone, phase)}],
            max_tokens=1024,
        )
        result = gen_resp.choices[0].message.content
        customer_message = ""
        summary_entry    = ""
        if "CUSTOMER_MESSAGE:" in result:
            after_cm = result.split("CUSTOMER_MESSAGE:")[1]
            if "SUMMARY_ENTRY:" in after_cm:
                customer_message = after_cm.split("SUMMARY_ENTRY:")[0].strip()
                summary_entry    = after_cm.split("SUMMARY_ENTRY:")[1].strip()
            else:
                customer_message = after_cm.strip()

        update = add_workspace_update(
            workspace_id, username, timeline,
            phase, customer_message, summary_entry
        )
        return jsonify({"update": update}), 201

    except Exception as e:
        print(f"[workspace/updates] ERROR: {e}")
        return jsonify({"error": str(e)}), 500


@workspace_bp.route("/workspace/<int:workspace_id>/members", methods=["POST"])
@role_required("owner", "incident_manager")
def add_member_route(workspace_id):
    user_id  = request.current_user.get("sub")
    role     = request.current_user.get("role", "")

    ws = get_workspace(workspace_id)
    if not ws:
        return jsonify({"error": "Workspace not found"}), 404
    if role != "owner" and not _is_member(workspace_id, user_id):
        return jsonify({"error": "Only members or the owner can add collaborators"}), 403

    data           = request.get_json() or {}
    new_user_id    = data.get("user_id")
    new_username   = data.get("username", "")

    if not new_user_id:
        return jsonify({"error": "user_id is required"}), 400

    ok = add_workspace_member(workspace_id, new_user_id, new_username)
    if ok:
        return jsonify({"added": True}), 201
    return jsonify({"error": "User is already a member"}), 409


@workspace_bp.route("/workspace/<int:workspace_id>/members/<int:target_user_id>", methods=["DELETE"])
@role_required("owner")
def remove_member_route(workspace_id, target_user_id):
    ok = remove_workspace_member(workspace_id, target_user_id)
    return jsonify({"removed": ok}), 200


@workspace_bp.route("/workspace/<int:workspace_id>/status", methods=["PATCH"])
@role_required("owner", "incident_manager")
def update_status_route(workspace_id):
    user_id = request.current_user.get("sub")
    role    = request.current_user.get("role", "")

    ws = get_workspace(workspace_id)
    if not ws:
        return jsonify({"error": "Workspace not found"}), 404
    if role != "owner" and not _is_member(workspace_id, user_id):
        return jsonify({"error": "Not a member of this workspace"}), 403

    data   = request.get_json() or {}
    status = data.get("status", "closed")
    if status not in ("active", "closed"):
        return jsonify({"error": "Invalid status"}), 400

    if status == "closed":
        ok = close_workspace(workspace_id)
    else:
        # Reopen
        try:
            from .models import _pg_conn, _sqlite_conn, DATABASE_URL
            if DATABASE_URL:
                conn = _pg_conn()
                conn.run("UPDATE workspaces SET status = 'active' WHERE id = :id", id=workspace_id)
                conn.close()
            else:
                with _sqlite_conn() as conn:
                    conn.execute("UPDATE workspaces SET status = 'active' WHERE id = ?", (workspace_id,))
                    conn.commit()
            ok = True
        except Exception:
            ok = False

    return jsonify({"updated": ok}), 200
