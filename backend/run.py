"""
Entry point — run from the project root:
    python backend/run.py
"""
import sys
import os

# Ensure the project root is on the path so `backend.config` resolves correctly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
