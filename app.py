from flask import Flask, render_template, request, jsonify
from groq import Groq
from config import GROQ_API_KEY

app = Flask(__name__)

client = Groq(api_key=GROQ_API_KEY)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():

    data = request.get_json()

    timeline = data.get("timeline", "")
    severity = data.get("severity", "")
    tone = data.get("tone", "")

    prompt = f"""
You are an outage communication specialist.

Technical Timeline:
{timeline}

Severity: {severity}
Tone: {tone}

Generate exactly in this format:

INITIAL:
<initial update>

PROGRESS:
<progress update>

RESOLVED:
<resolved update>

SUMMARY:
<internal incident summary>

Rules:
- Use timeline details.
- Customer-friendly language.
- Reflect severity and tone.
- Summary is for internal teams.
- Do not mention database, server, API, or technical components in customer updates.
- Use simple customer-friendly language.
- Internal summary should be bullet-point style.
"""

    try:

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        result = response.choices[0].message.content

        print("\nAI RESPONSE:\n")
        print(result)

        initial = ""
        progress = ""
        resolved = ""
        summary = ""

        if "INITIAL:" in result:
            initial = result.split("INITIAL:")[1].split("PROGRESS:")[0].strip()

        if "PROGRESS:" in result:
            progress = result.split("PROGRESS:")[1].split("RESOLVED:")[0].strip()

        if "RESOLVED:" in result:
            resolved = result.split("RESOLVED:")[1].split("SUMMARY:")[0].strip()

        if "SUMMARY:" in result:
            summary = result.split("SUMMARY:")[1].strip()

        return jsonify({
            "initial": initial,
            "progress": progress,
            "resolved": resolved,
            "summary": summary
        })

    except Exception as e:

        print("ERROR:", e)

        return jsonify({
            "initial": str(e),
            "progress": str(e),
            "resolved": str(e),
            "summary": str(e)
        })


if __name__ == "__main__":
    app.run(debug=True)