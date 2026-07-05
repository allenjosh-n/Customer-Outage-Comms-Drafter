"""
Quick connectivity test — verifies the Groq API key and model are reachable.
Run from the project root:
    python tests/test_groq.py
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from groq import Groq
from backend.config import GROQ_API_KEY

client = Groq(api_key=GROQ_API_KEY)

response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": "Say hello in one sentence."}],
)

print("✓ Groq API connected successfully.")
print("Response:", response.choices[0].message.content)
