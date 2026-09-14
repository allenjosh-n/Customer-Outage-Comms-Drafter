# Customer Outage Comms Drafter

> An AI-powered incident communication tool that converts raw technical timelines into professional, customer-safe messages — automatically detecting the incident phase and drafting the right update every time.

## Live Deployments

| Platform | URL | Status |
|---|---|---|
| Render | https://customer-outage-comms-drafter.onrender.com | ✅ Live |
| Vercel | https://customer-outage-comms-drafter.vercel.app | ✅ Live |

> **Primary:** Use the Render link for best performance. Vercel serves as a backup.

---

## Problem Statement

During service outages, technical teams have detailed timelines but no fast, consistent way to turn them into clear customer communications. Writing updates manually under pressure leads to delays, inconsistent tone, and messages that leak technical jargon to customers.

This tool solves that by automating the full communication pipeline — from phase detection to customer message generation — so teams can focus on resolving the incident, not writing about it.

---

## How It Works

1. Register or log in to your account
2. Paste a single timeline entry (e.g. `09:00 — Users unable to log in`)
3. Click **Draft Update**
4. The AI classifies the entry as `initial`, `progress`, or `resolved`
5. The matching communication card is populated with a customer-facing message
6. Each update appends a bullet-point entry to the internal Incident Summary Log
7. Export the full report as a `.txt` file when the incident is closed

---

## Features

| Feature | Description |
|---|---|
| JWT Authentication | Register and login with secure JWT-based auth (12h token expiry) |
| Auto Phase Detection | Classifies each timeline entry into `initial`, `in-progress`, or `resolved` |
| Customer Message Generation | Produces jargon-free, tone-adjusted customer updates |
| Severity Levels | Supports Low, Medium, and High severity |
| Tone Selection | Calm, Empathetic, or Concise communication styles |
| Internal Incident Log | Structured bullet-point summary for incident management |
| Report Export | Download the full incident log as a `.txt` file |
| Copy to Clipboard | One-click copy for any generated communication |
| Persistent User Accounts | User data stored in Supabase PostgreSQL — survives server restarts |
| Responsive UI | Clean single-page interface built for operational teams |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML5, CSS3, Vanilla JavaScript |
| Backend | Python 3, Flask (Blueprint pattern) |
| AI Inference | Groq API — Llama 3.3 70B Versatile |
| Authentication | JWT (PyJWT) + werkzeug password hashing |
| Database | Supabase PostgreSQL (via pg8000) |
| Config | python-dotenv — `.env` based configuration |

---

## Project Structure

```
Customer-Outage-Comms-Drafter/
│
├── api/
│   └── index.py              ← Vercel serverless entry point
│
├── backend/
│   ├── app/
│   │   ├── __init__.py       ← App factory
│   │   ├── routes.py         ← API endpoints (/detect-phase, /generate)
│   │   ├── auth.py           ← Auth routes (/auth/register, /auth/login)
│   │   ├── auth_middleware.py← JWT @jwt_required decorator
│   │   ├── models.py         ← User model (Supabase + SQLite fallback)
│   │   └── prompts.py        ← Isolated AI prompt templates
│   ├── config.py             ← Loads env vars from .env
│   ├── requirements.txt      ← Python dependencies
│   └── run.py                ← Local entry point
│
├── frontend/
│   ├── static/
│   │   ├── css/style.css     ← App styles
│   │   ├── css/auth.css      ← Auth page styles
│   │   └── js/script.js      ← Client-side logic + auth token handling
│   └── templates/
│       ├── index.html        ← Main app
│       ├── login.html        ← Login page
│       └── register.html     ← Register page
│
├── docs/
│   ├── README.md
│   └── AI_USAGE.md
│
├── tests/
│   └── test_groq.py
│
├── .env.example              ← Safe config template
├── render.yaml               ← Render deployment config
├── vercel.json               ← Vercel deployment config
└── requirements.txt          ← Root requirements for Vercel
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

### 4. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env`:

```env
GROQ_API_KEY=gsk_your_key_here
JWT_SECRET=your-long-random-secret
DATABASE_URL=postgresql://postgres.xxxx:password@aws-0-region.pooler.supabase.com:6543/postgres
```

- Get a free Groq key at [console.groq.com](https://console.groq.com)
- Get a free Supabase DB at [supabase.com](https://supabase.com)
- `JWT_SECRET` can be any long random string

### 5. Run the app

```bash
python backend/run.py
```

Open `http://127.0.0.1:5000` — you'll be redirected to the login page.

---

## Authentication Flow

```
Register / Login → JWT token (stored in localStorage)
        ↓
Every API call sends: Authorization: Bearer <token>
        ↓
@jwt_required validates token on /detect-phase and /generate
        ↓
Token expires after 12h → user redirected to login
```

User accounts are stored persistently in **Supabase PostgreSQL**.

---

## API Endpoints

### `POST /auth/register`
Register a new account. Returns a JWT token.

```json
{ "username": "john", "email": "john@co.com", "password": "secret123" }
```

### `POST /auth/login`
Login with existing credentials. Returns a JWT token.

```json
{ "username": "john", "password": "secret123" }
```

### `POST /detect-phase` 🔒
Classifies a timeline entry. Requires `Authorization: Bearer <token>`.

```json
{ "timeline": "09:30 — Root cause traced to payment gateway" }
→ { "phase": "progress" }
```

### `POST /generate` 🔒
Generates customer message and internal log entry.

```json
{ "timeline": "...", "severity": "High", "tone": "Empathetic", "phase": "progress" }
→ { "phase": "progress", "text": "...", "summary_entry": "..." }
```

---

## AI Prompt Design

Two-stage LLM pipeline:

**Stage 1 — Phase Detection**
- Single-word output (`initial` / `progress` / `resolved`)
- Temperature `0` for deterministic classification

**Stage 2 — Communication Generation**
- Structured output with strict section labels (`CUSTOMER_MESSAGE:` / `SUMMARY_ENTRY:`)
- Injects severity and tone as prompt variables
- Explicitly bans technical jargon in customer messages

Full prompt documentation in [`docs/AI_USAGE.md`](docs/AI_USAGE.md).

---

## Deployment

### Vercel
Set these environment variables in Vercel → Settings → Environment Variables:
```
GROQ_API_KEY
JWT_SECRET
DATABASE_URL   ← Supabase pooler URL (port 6543)
```

### Render
Set the same variables in Render → Environment.

---

## Future Enhancements

- PDF / email export
- Multi-language support
- Incident analytics dashboard
- Webhook integration for PagerDuty / Slack
- Admin role and team management

---

## AI Tools Used During Development

| Tool | Role |
|---|---|
| Groq API + Llama 3.3 70B | Runtime AI inference engine |
| ChatGPT (OpenAI) | Prompt engineering and design |
| Kiro (Amazon) | Code assistance, debugging, deployment fixes |
| GitHub Copilot | Inline code suggestions |

---

## License

MIT
