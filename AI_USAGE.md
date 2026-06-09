# AI Usage Note & Prompt Documentation

This document outlines all AI tools used during the development of the **Customer Outage Comms Drafter** project, the role each tool played, and the prompts used to generate key components.

---

## AI Tools Used

### 1. ChatGPT (OpenAI)
**Role:** Prompt engineering and content generation

ChatGPT was used to design and refine the core AI prompt sent to the Groq/Llama model at runtime. This includes the structure of the outage communication prompt, the output format (INITIAL / PROGRESS / RESOLVED / SUMMARY), and the rules guiding customer-friendly language.

---

### 2. Kiro (Amazon)
**Role:** Code optimization, project setup assistance, and documentation

Kiro was used to assist with:
- Virtual environment setup guidance
- Reviewing and correcting the `config.py` API key configuration
- Advising on minimal dependency installation (avoiding unnecessary packages)
- Generating this AI usage documentation

---

### 3. Groq API + Llama 3.3 70B Versatile
**Role:** Runtime AI inference engine

The Groq API serves as the live AI backend for the application. The `llama-3.3-70b-versatile` model processes the incident timeline, severity, and tone inputs and generates the four communication outputs at runtime.

---

### 4. GitHub Copilot (if used during development)
**Role:** Inline code suggestions

GitHub Copilot may have assisted with boilerplate Flask route structure, JSON parsing patterns, and JavaScript fetch API calls in `script.js`.

---

## Prompt Documentation

### Core Runtime Prompt

This is the prompt template used in `app.py` that is sent to the Groq/Llama model on every generation request:

```text
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
```

---

### Prompt Design Rationale

| Element | Purpose |
|---|---|
| `You are an outage communication specialist` | Sets the AI persona to produce professional incident communications |
| `Technical Timeline: {timeline}` | Injects the raw incident data for the model to process |
| `Severity: {severity}` | Guides urgency and escalation language in the output |
| `Tone: {tone}` | Controls whether output is calm, empathetic, or concise |
| Strict output format (INITIAL / PROGRESS / RESOLVED / SUMMARY) | Ensures predictable parsing in `app.py` |
| Rule: no technical jargon in customer updates | Keeps outputs accessible to non-technical customers |
| Rule: bullet-point internal summary | Structures the internal report for incident management teams |

---

### ChatGPT Prompt Used to Generate the Runtime Prompt

The following prompt was used in ChatGPT to design and iterate on the runtime prompt above:

```text
I am building a Flask web app that takes an outage incident timeline, a severity level,
and a tone as inputs. Using the Groq API with Llama 3.3 70B, I want to generate:

1. An initial customer update
2. A progress update for customers
3. A resolved update for customers
4. An internal incident summary for the tech team

Rules:
- Customer updates must not mention technical components like databases, servers, or APIs.
- The internal summary should be bullet-point style.
- The output must follow a strict labeled format so I can parse it easily in Python.

Write me an AI prompt I can use inside my Python code for this.
```

---

## Notes

- The API key used is a **Groq API key** and should be kept private. It is stored in `config.py` and must never be committed to a public repository.
- The `requirements.txt` in this project contains a large list of packages from the development environment. Only `flask` and `groq` are required to run this application.
- Future versions may replace or supplement Groq/Llama with other models (e.g., GPT-4o, Gemini) depending on performance and cost requirements.

---

*Document last updated: June 2026*
