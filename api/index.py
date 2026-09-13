"""
Vercel serverless entry point.
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    from backend.app import create_app
    app = create_app()
except Exception as _e:
    # Surface the real import error in the browser so we can diagnose it
    import traceback
    _tb = traceback.format_exc()

    from flask import Flask, jsonify
    app = Flask(__name__)

    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def _error_page(path):
        return (
            f"<pre style='font-family:monospace;padding:2rem;color:#c00'>"
            f"STARTUP ERROR\n\n{_tb}</pre>",
            500,
        )
