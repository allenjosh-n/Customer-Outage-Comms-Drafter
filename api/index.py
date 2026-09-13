"""
Vercel serverless entry point.
"""
import sys
import os
import traceback

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from flask import Flask, jsonify

# Always define app at module level so Vercel can find it
app = Flask(__name__)

try:
    from backend.app import create_app
    app = create_app()
except Exception as _e:
    _tb = traceback.format_exc()

    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def _startup_error(path):
        return f"<pre style='padding:2rem;color:#c00'>STARTUP ERROR\n\n{_tb}</pre>", 500
