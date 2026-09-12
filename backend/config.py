import os
from dotenv import load_dotenv

# .env lives at the project root (one level above backend/)
# load_dotenv is a no-op if the file doesn't exist (e.g. on Vercel)
_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
load_dotenv(os.path.join(_root, ".env"))

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
