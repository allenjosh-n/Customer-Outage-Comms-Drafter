# Customer Outage Comms Drafter — Project Report

**Project Title:** Customer Outage Comms Drafter  
**Technology Stack:** Python, Flask, Groq API, HTML/CSS/JavaScript  
**Deployment:** Vercel — https://customer-outage-comms-drafter.vercel.app  
**Repository:** https://github.com/allenjosh-n/Customer-Outage-Comms-Drafter

---

## 1. Introduction

During service outages, technical teams have detailed incident timelines but no fast, consistent way to turn them into clear customer communications. Writing updates manually under pressure leads to delays, inconsistent tone, and messages that leak technical jargon to customers.

**Customer Outage Comms Drafter** solves this by automating the full communication pipeline — from phase detection to customer message generation — so teams can focus on resolving the incident, not writing about it.

The system accepts a single timeline entry at a time, automatically detects which phase of the incident it represents (Initial Alert, In Progress, or Resolved), and drafts the appropriate customer-facing communication along with a structured internal log entry.

---

## 2. Problem Statement

When a service outage occurs, incident teams face two simultaneous pressures:

- **Technical pressure** — diagnosing and resolving the issue
- **Communication pressure** — keeping customers informed in real time

Manual drafting of customer updates is slow, inconsistent, and error-prone. Different team members produce different tones, levels of detail, and sometimes accidentally expose internal technical details to customers. This tool removes that burden entirely.

---

## 3. System Overview

### 3.1 How It Works

The application follows a two-step workflow:

**Step 1 — Incident Details**
- The engineer enters a single timeline update (e.g. `09:00 AM – Payment transactions failing for multiple customers`)
- Selects severity (Low / Medium / High) and tone (Calm / Empathetic / Concise)
- Clicks **Draft Update**

**Step 2 — Live Drafts**
- The AI detects the phase: `initial`, `progress`, or `resolved`
- Only the matching communication card is populated
- The entry is appended to the internal Incident Summary Log
- The full report can be downloaded at any time

### 3.2 AI Pipeline (Two-Stage)

```
Timeline Entry
      │
      ▼
[Stage 1] Phase Detection
  → Groq API classifies as: initial / progress / resolved
      │
      ▼
[Stage 2] Communication Generation
  → Groq API generates:
      • CUSTOMER_MESSAGE  (jargon-free, tone-adjusted)
      • SUMMARY_ENTRY     (bullet-point internal log)
```

---

## 4. Features

| Feature | Description |
|---|---|
| Auto Phase Detection | Classifies each timeline entry into `initial`, `in-progress`, or `resolved` |
| Customer Message Generation | Produces jargon-free, tone-adjusted customer updates |
| Severity Levels | Low, Medium, and High severity with visual indicator |
| Tone Selection | Calm, Empathetic, or Concise communication styles |
| Internal Incident Log | Structured bullet-point summary for the incident team |
| Report Export | Download the full incident log as a `.txt` file |
| Copy to Clipboard | One-click copy for any generated communication |
| Responsive UI | Clean single-page interface optimised for operational teams |

---

## 5. Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML5, CSS3, Vanilla JavaScript |
| Backend | Python 3, Flask (Blueprint pattern) |
| AI Inference | Groq API — `openai/gpt-oss-20b` (reasoning model) |
| Config | python-dotenv — `.env` based API key management |
| Deployment | Vercel (serverless), Render (web service) |

---

## 6. Project Structure

```
Customer-Outage-Comms-Drafter/
│
├── api/
│   └── index.py              ← Vercel serverless entry point
│
├── backend/
│   ├── app/
│   │   ├── __init__.py       ← Flask app factory
│   │   ├── routes.py         ← API endpoints (/detect-phase, /generate, /debug)
│   │   └── prompts.py        ← AI prompt templates
│   ├── config.py             ← Environment variable loader
│   ├── requirements.txt      ← Python dependencies
│   └── run.py                ← Local development entry point
│
├── frontend/
│   ├── static/
│   │   ├── css/style.css     ← Application styles
│   │   └── js/script.js      ← Client-side logic
│   └── templates/
│       └── index.html        ← Single-page UI template
│
├── docs/
│   ├── README.md             ← Setup and usage guide
│   ├── AI_USAGE.md           ← Prompt design documentation
│   └── PROJECT_REPORT.md     ← This file
│
├── tests/
│   └── test_groq.py          ← Groq API connectivity test
│
├── .env.example              ← Safe API key template
├── render.yaml               ← Render deployment config
├── vercel.json               ← Vercel deployment config
└── requirements.txt          ← Root-level requirements for Vercel
```

---

## 7. API Endpoints

### `POST /detect-phase`
Classifies a timeline entry into one incident phase.

**Request**
```json
{ "timeline": "09:30 AM — Root cause traced to payment gateway" }
```
**Response**
```json
{ "phase": "progress" }
```

---

### `POST /generate`
Generates a customer message and internal log entry.

**Request**
```json
{
  "timeline": "09:30 AM — Root cause traced to payment gateway",
  "severity": "High",
  "tone": "Empathetic",
  "phase": "progress"
}
```
**Response**
```json
{
  "phase": "progress",
  "text": "We're sorry for the inconvenience you've experienced...",
  "summary_entry": "• Root cause identified as payment gateway failure\n• Engineering team engaged"
}
```

---

### `GET /debug`
Returns environment variable status for deployment verification.

**Response**
```json
{
  "GROQ_API_KEY_set": true,
  "GROQ_API_KEY_prefix": "gsk_xxxx..."
}
```

---

## 8. AI Prompt Design

### Phase Detection Prompt

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

Your one-word answer:
```

### Communication Generation Prompt

```text
You are an outage communication specialist.

Technical Timeline Entry: {timeline}
Severity: {severity}
Tone: {tone}
Phase: {phase_label}

Generate exactly in this format:

CUSTOMER_MESSAGE:
<customer-facing message, no technical jargon, 2-4 sentences>

SUMMARY_ENTRY:
<2-4 bullet points for the internal incident log>
```

### Prompt Design Rationale

| Element | Purpose |
|---|---|
| One-word phase classification | Forces deterministic output, easy to sanitise |
| `max_tokens=100` for phase detection | Allows reasoning model to think before answering |
| Strict section labels | Enables reliable `string.split()` parsing in Python |
| No technical jargon rule | Keeps customer updates accessible |
| Tone + severity injection | Personalises urgency and language style |
| `temperature=0` | Deterministic, repeatable phase classification |

---

## 9. Screenshots

### 9.1 Initial State — Empty Dashboard

The application loads with three phase cards ready and the incident summary log empty.

![Empty Dashboard](../screenshots/01_empty_dashboard.png)

---

### 9.2 Initial Alert Detected

The first timeline entry (`09:00 AM – Payment transactions failing for multiple customers`) is detected as **INITIAL ALERT** and the Initial Update card is populated with a customer-facing message.

![Initial Alert](../screenshots/02_initial_alert.png)

---

### 9.3 In-Progress Update

A follow-up entry (`10:00 AM – Temporary workaround deployed`) is detected as **IN PROGRESS** and the Progress Update card is populated. The Initial card remains with its previous content.

![In Progress](../screenshots/03_in_progress.png)

---

### 9.4 Resolved Update — All Three Cards Filled

After the final entry, the Resolved Update card is also populated. All three phase cards now contain live content and the "Resolved draft ready" toast notification is shown.

![All Cards Filled](../screenshots/04_resolved_all_cards.png)

---

### 9.5 Incident Summary Log — Internal View

The internal log builds up as each phase entry is submitted. Each entry shows the timeline timestamp, bullet-point technical details, and the phase label.

![Incident Summary Log](../screenshots/05_summary_log.png)

---

### 9.6 Full Log with Multiple Entries

Multiple entries across all phases displayed in the incident summary log, demonstrating the chronological build-up of the internal incident record.

![Full Log](../screenshots/06_full_log.png)

---

## 10. Sample End-to-End Incident

**Scenario:** Payment processing outage

| Time | Timeline Entry | Detected Phase | Customer Message |
|---|---|---|---|
| 09:00 AM | Payment transactions failing for multiple customers | Initial Alert | "We're aware that some of your recent payment attempts have not gone through. We're working hard to resolve the issue as quickly as possible..." |
| 10:00 AM | Temporary workaround deployed | In Progress | "We're sorry for the inconvenience. We have deployed a temporary workaround at 10:00 AM to help mitigate the issue..." |
| 10:30 AM | Payment processing restored | Resolved | "We are pleased to inform you that the recent service interruption has been fully resolved. Monitoring shows the system is operating normally..." |

---

## 11. Deployment

### Vercel (Primary)

The app is deployed as a Python serverless function on Vercel.

```json
{
  "version": 2,
  "builds": [{ "src": "api/index.py", "use": "@vercel/python" }],
  "routes": [{ "src": "/(.*)", "dest": "api/index.py" }]
}
```

**Environment variable required:**
```
GROQ_API_KEY = gsk_...
```
Set in Vercel → Project → Settings → Environment Variables.

### Render (Backup)

```yaml
services:
  - type: web
    name: customer-outage-comms-drafter
    runtime: python
    buildCommand: pip install -r backend/requirements.txt
    startCommand: gunicorn --chdir backend "app:create_app()" --bind 0.0.0.0:$PORT
```

---

## 12. Known Issues & Fixes Applied

| Issue | Root Cause | Fix Applied |
|---|---|---|
| `model_not_found` 404 error | `llama-3.3-70b-versatile` not available on this Groq account | Switched to `openai/gpt-oss-20b` |
| Phase always returns `initial` | `max_tokens=5` too low for reasoning model — `content` field returned empty | Increased to `max_tokens=100` for phase detection |
| App crashed on Vercel startup | `config.py` raised `ValueError` when no `.env` file present | Removed startup exception; error is now handled per-request |
| Groq client created at import time | Module-level client captured empty API key before env vars loaded | Moved to lazy `get_client()` function called per-request |

---

## 13. Future Enhancements

- PDF / formatted email export
- Multi-language customer message support
- Incident analytics dashboard
- Webhook integration (PagerDuty, Slack, Microsoft Teams)
- User authentication and team collaboration
- Incident template library per service type

---

## 14. AI Tools Used During Development

| Tool | Role |
|---|---|
| Groq API (`openai/gpt-oss-20b`) | Runtime AI inference — phase detection and message generation |
| ChatGPT (OpenAI) | Prompt engineering and design |
| Kiro (Amazon) | Code assistance, debugging, deployment fixes |
| GitHub Copilot | Inline code suggestions |

---

*Report generated: September 2026*
