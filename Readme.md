# Customer Outage Comms Drafter

> An AI-powered incident communication tool that converts raw technical timelines into professional, customer-safe messages — automatically detecting the incident phase and drafting the right update every time.

---

## Problem Statement

During service outages, technical teams have detailed timelines but no fast, consistent way to turn them into clear customer communications. Writing updates manually under pressure leads to delays, inconsistent tone, and messages that leak technical jargon to customers.

This tool solves that by automating the full communication pipeline — from phase detection to customer message generation — so teams can focus on resolving the incident, not writing about it.

---

## How It Works

1. Paste a single timeline entry (e.g. `09:00 — Users unable to log in`)
2. Click **Draft Update**
3. The AI classifies the entry as `initial`, `progress`, or `resolved`
4. The matching communication card is populated with a customer-facing message
5. Each update appends a bullet-point entry to the internal Incident Summary Log
6. Export the full report as a `.txt` file when the incident is closed

---

## Features

| Feature | Description |
|---|---|
| Auto Phase Detection | Classifies each timeline entry into `initial`, `in-progress`, or `resolved` |
| Customer Message Generation | Produces jargon-free, tone-adjusted customer updates |
| Severity Levels | Supports Low, Medium, and High severity |
| Tone Selection | Calm, Empathetic, or Concise communication styles |
| Internal Incident Log | Structured bullet-point summary for incident management |
| Report Export | Download the full incident log as a `.txt` file |
| Copy to Clipboard | One-click copy for any generated communication |
| Responsive UI | Clean single-page interface built for operational teams |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML5, CSS3, Vanilla JavaScript |
| Backend | Python 3, Flask (Blueprint pattern) |
| AI Inference | Groq API — Llama 3.3 70B Versatile |
| Config | python-dotenv — `.env` based API key management |

---

## Project Structure

```
Customer-Outage-Comms-Drafter/
│
├── backend/
│   ├── app/
│   │   ├── __init__.py       ← App factory
│   │   ├── routes.py         ← API endpoints (/detect-phase, /generate)
│   │   └── prompts.py        ← Isolated AI prompt templates
│   ├── config.py             ← Loads GROQ_API_KEY from .env
│   ├── requirements.txt      ← Python dependencies
│   └── run.py                ← Entry point
│
├── frontend/
│   ├── static/
│   │   ├── css/style.css
│   │   └── js/script.js
│   └── templates/
│       └── index.html
│
├── docs/
│   ├── README.md
│   └── AI_USAGE.md           ← Prompt design & AI tool documentation
│
├── tests/
│   └── test_groq.py          ← Groq API connectivity test
│
├── .env.example              ← Safe API key template
├── .gitignore
└── README.md
```

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/allenjosh-n/Customer-Outage-Comms-Drafter.git
cd Customer-Outage-Comms-Drafter
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r backend/requirements.txt
```

### 4. Configure your API key

```bash
cp .env.example .env
```

Edit `.env` and add your key:

```
GROQ_API_KEY=gsk_your_key_here
```

Get a free key at [console.groq.com](https://console.groq.com).

### 5. Run the app

```bash
python backend/run.py
```

Open `http://127.0.0.1:5000`

---

## API Endpoints

### `POST /detect-phase`

Classifies a timeline entry into one incident phase.

**Request**
```json
{ "timeline": "09:30 — Root cause traced to payment gateway" }
```

**Response**
```json
{ "phase": "progress" }
```

---

### `POST /generate`

Generates a customer message and internal log entry for a given phase.

**Request**
```json
{
  "timeline": "09:30 — Root cause traced to payment gateway",
  "severity": "High",
  "tone": "Empathetic",
  "phase": "progress"
}
```

**Response**
```json
{
  "phase": "progress",
  "text": "We are aware of an issue affecting some of our services and our team is actively working to resolve it...",
  "summary_entry": "• 09:30 — Root cause identified as payment gateway failure\n• Engineering team engaged, mitigation in progress"
}
```

---

## AI Prompt Design

Two-stage LLM pipeline built around deterministic, structured output:

**Stage 1 — Phase Detection**
- Single-token output (`initial` / `progress` / `resolved`)
- Temperature set to `0` for deterministic classification
- Enforces `max_tokens=5` to prevent hallucination

**Stage 2 — Communication Generation**
- Structured output with strict section labels (`CUSTOMER_MESSAGE:` / `SUMMARY_ENTRY:`)
- Labels enable reliable string-split parsing in Python
- Injects severity and tone as prompt variables
- Explicitly bans technical jargon in customer messages

Full prompt documentation in [`docs/AI_USAGE.md`](docs/AI_USAGE.md).

---

## Sample Input / Output

**Input timeline entry:**
```
09:30 AM - Root cause traced to payment gateway outage
```

**Severity:** High | **Tone:** Empathetic

**Customer Message (generated):**
> We're aware that some customers are experiencing difficulties completing payments. Our team has identified the cause and is working urgently to restore full service. We sincerely apologise for the inconvenience and will provide another update shortly.

**Internal Log Entry (generated):**
> • 09:30 — Root cause confirmed as third-party payment gateway failure
> • Incident severity: High — customer transactions affected
> • Engineering team actively investigating mitigation path
> • Next update scheduled within 30 minutes

---

## Future Enhancements

- PDF / email export
- Multi-language support
- Incident analytics dashboard
- Webhook integration for PagerDuty / Slack
- Cloud deployment (Railway / Render)

---

## AI Tools Used During Development

| Tool | Role |
|---|---|
| Groq API + Llama 3.3 70B | Runtime AI inference engine |
| ChatGPT (OpenAI) | Prompt engineering and design |
| Google Gemini (Antigravity) | Code assistance and project setup |
| GitHub Copilot | Inline code suggestions |

---

## License

MIT
