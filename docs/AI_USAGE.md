# AI Usage Note & Prompt Documentation

This document outlines all AI tools used during development of the **Customer Outage Comms Drafter**, the role each tool played, and the prompts used.

---

## AI Tools Used

### 1. ChatGPT (OpenAI)
**Role:** Prompt engineering and content generation

Used to design and refine the core AI prompt sent to the Groq/Llama model at runtime — including the output format and rules for customer-friendly language.

### 2. Antigravity (Google)
**Role:** Code assistance, project setup, and documentation

Used for: virtual environment guidance, API key configuration, dependency management, UI improvements, file structure restructuring, and feature implementation.

### 3. Groq API + Llama 3.3 70B Versatile
**Role:** Runtime AI inference engine

Processes incident timeline entries and generates customer-facing communications and internal log entries.

### 4. GitHub Copilot
**Role:** Inline code suggestions

Assisted with boilerplate Flask route structure and JavaScript fetch API patterns.

---

## Prompt Documentation

### Phase Detection Prompt

Sent to the AI to classify a timeline entry into one phase (`initial`, `progress`, or `resolved`):

```text
You are classifying an IT incident timeline entry into exactly one phase.

Timeline entry:
"""{timeline}"""

Rules:
- Reply with ONLY one word — no punctuation, no explanation.
- Reply "initial"  if the entry describes an issue being DETECTED or IDENTIFIED.
- Reply "progress" if the entry describes the team INVESTIGATING or WORKING ON the issue.
- Reply "resolved" if the entry describes the issue being FIXED or RESTORED.
- If unsure, reply "initial".
```

### Communication Generation Prompt

Sent after phase detection to produce the customer message and internal log entry:

```text
You are an outage communication specialist.

Technical Timeline Entry: {timeline}
Severity: {severity}
Tone: {tone}
Phase: {phase_label}

Generate exactly:

CUSTOMER_MESSAGE:
<customer-facing message, no technical jargon, 2-4 sentences>

SUMMARY_ENTRY:
<2-4 bullet points for the internal incident log>
```

---

## Prompt Design Rationale

| Element | Purpose |
|---|---|
| One-word phase classification | Forces deterministic output, easy to sanitise |
| Strict section labels | Allows reliable string-split parsing in Python |
| No technical jargon rule | Keeps customer updates accessible |
| Bullet-point summary rule | Structures internal log for incident teams |
| Tone + severity injection | Personalises urgency and language style |

---

*Document last updated: 2026*
