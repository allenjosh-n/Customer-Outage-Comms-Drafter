"""
Vercel serverless entry point.
Vercel looks for a callable named `app` in this file.
"""
import sys
import os

# Add project root to path so backend package resolves correctly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app import create_app

app = create_app()
