import os
from dotenv import load_dotenv

# .env lives at the project root (one level above backend/)
_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
load_dotenv(os.path.join(_root, ".env"))

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

if not GROQ_API_KEY:
    raise ValueError(
        "GROQ_API_KEY is not set.\n"
        "Add it to the project root .env file as:\n"
        "  GROQ_API_KEY=gsk_..."
    )
