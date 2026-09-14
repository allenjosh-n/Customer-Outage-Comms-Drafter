# Customer Outage Comms Drafter

> An AI-powered incident communication tool that converts raw technical timelines into professional, customer-safe messages — with role-based access control, shared incident history, and a team management panel.

## Live Deployments

| Platform | URL | Status |
|---|---|---|
| Render | https://customer-outage-comms-drafter.onrender.com | ✅ Live |
| Vercel | https://customer-outage-comms-drafter.vercel.app | ✅ Live |

---

## Problem Statement

During service outages, technical teams have detailed timelines but no fast, consistent way to turn them into clear customer communications. Writing updates manually under pressure leads to delays, inconsistent tone, and messages that leak technical jargon to customers.

This tool solves that by automating the full communication pipeline — from phase detection to customer message generation — so teams can focus on resolving the incident, not writing about it.

---

## How It Works

1. Register or log in — the first user automatically becomes the **Owner**
2. Owner promotes team members to **Incident Manager** via the Access Manager
3. Incident Manager enters a timeline update and clicks **Draft Update**
4. The AI classifies the entry as `initial`, `progress`, or `resolved`
5. The matching communication card is populated with a customer-facing message
6. Each update appends a bullet-point entry to the internal Incident Summary Log
7. Click **Start New Incident** to save the incident to shared history and reset
8. All roles can view the **History** tab — Viewers see only this tab

---

## Features

| Feature | Description |
|---|---|
| JWT Authentication | Secure register/login with 12h token expiry |
| Role-Based Access Control | Owner, Incident Manager, Viewer roles with enforced permissions |
| Access Manager | Owner-only panel to grant/revoke team member roles |
| Auto Phase Detection | Classifies each timeline entry into `initial`, `in-progress`, or `resolved` |
| Customer Message Generation | Produces jargon-free, tone-adjusted customer updates |
| Severity Levels | Low, Medium, and High severity with visual indicator |
| Tone Selection | Calm, Empathetic, or Concise communication styles |
| Shared Incident History | Last 5 incidents visible to all roles, with `drafted by` attribution |
| Delete Incident | Owner can delete any incident from shared history |
| Internal Incident Log | Structured bullet-point summary for the incident team |
| Report Export | Download the full incident log as a `.txt` file |
| Copy to Clipboard | One-click copy for any generated communication |
| Persistent User Accounts | Users and incidents stored in Supabase PostgreSQL |
| Responsive UI | Clean single-page interface built for operational teams |

---

## Roles & Permissions

| Role | Generate Updates | View History | Delete Incidents | Access Manager |
|---|---|---|---|---|
| **Owner** | ✅ | ✅ | ✅ | ✅ |
| **Incident Manager** | ✅ | ✅ | ❌ | ❌ |
| **Viewer** | ❌ | ✅ | ❌ | ❌ |

- The **first user to register** becomes the Owner — there can only be one
- All other users default to **Viewer** until the Owner promotes them
- The Owner opens **Access Manager** (top header) to change roles

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML5, CSS3, Vanilla JavaScript |
| Backend | Python 3, Flask (Blueprint pattern) |
| AI Inference | Groq API — Llama 3.3 70B Versatile |
| Authentication | JWT (PyJWT) + werkzeug password hashing |
| Authorization | Role-based `@role_required` decorator |
| Database | Supabase PostgreSQL (via pg8000) |
| Config | python-dotenv — `.env` based configuration |

---

## Project Structure

```
Customer-Outage-Comms-Drafter/
│
├── api/
│   └── index.py                ← Vercel serverless entry point
│
├── backend/
│   ├── app/
│   │   ├── __init__.py         ← App factory
│   │   ├── routes.py           ← API endpoints
│   │   ├── auth.py             ← Auth routes (/auth/register, /auth/login)
│   │   ├── auth_middleware.py  ← @jwt_required, @role_required decorators
│   │   ├── models.py           ← User + incident model (Supabase + SQLite fallback)
│   │   └── prompts.py          ← AI prompt templates
│   ├── config.py               ← Environment variable loader
│   ├── requirements.txt        ← Python dependencies
│   └── run.py                  ← Local entry point
│
├── frontend/
│   ├── static/
│   │   ├── css/style.css       ← App styles
│   │   ├── css/auth.css        ← Auth + Access Manager styles
│   │   └── js/script.js        ← Client-side logic, role-aware UI
│   └── templates/
│       ├── index.html          ← Main app
│       ├── login.html          ← Login page
│       └── register.html       ← Register page
│
├── docs/
│   ├── README.md
│   └── AI_USAGE.md
│
├── tests/
│   └── test_groq.py
│
├── .env.example
├── render.yaml
├── vercel.json
└── requirements.txt
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

### 5. Set up Supabase (first time only)

Run this in your Supabase SQL Editor:

```sql
CREATE TABLE IF NOT EXISTS users (
    id       SERIAL PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    email    TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    role     TEXT NOT NULL DEFAULT 'viewer',
    created  TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS incidents (
    id         SERIAL PRIMARY KEY,
    drafted_by TEXT NOT NULL DEFAULT '',
    severity   TEXT NOT NULL DEFAULT 'Low',
    entries    TEXT NOT NULL,
    created    TIMESTAMPTZ DEFAULT NOW()
);
```

### 6. Run the app

```bash
python backend/run.py
```

Open `http://127.0.0.1:5000` — the first account you create will be the Owner.

---

## API Endpoints

### Auth
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/auth/register` | None | Register — first user becomes Owner |
| POST | `/auth/login` | None | Login, returns JWT + role |
| GET | `/auth/owner-exists` | None | Check if an owner account exists |

### Incident Operations
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/detect-phase` | Owner, Manager | Classify timeline entry |
| POST | `/generate` | Owner, Manager | Generate customer message + log entry |
| POST | `/incidents/save` | Owner, Manager | Save completed incident to history |
| GET | `/incidents` | All roles | Get last 5 shared incidents |
| DELETE | `/incidents/<id>` | Owner only | Delete an incident from history |

### Admin
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/admin/users` | Owner only | List all users with roles |
| PATCH | `/admin/users/<id>/role` | Owner only | Change a user's role |

---

## Deployment — Environment Variables

Set these in Vercel → Settings → Environment Variables (and Render → Environment):

| Variable | Description |
|---|---|
| `GROQ_API_KEY` | Groq API key for AI inference |
| `JWT_SECRET` | Secret for signing JWT tokens |
| `DATABASE_URL` | Supabase PostgreSQL pooler URL (port 6543) |

---

## Future Enhancements

- PDF / email export
- Multi-language customer message support
- Incident analytics dashboard
- Webhook integration (PagerDuty, Slack, Microsoft Teams)
- Incident template library per service type

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
