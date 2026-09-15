# Customer Outage Comms Drafter

> An AI-powered, role-based collaborative incident communication platform where multiple incident managers can work together on the same incident, generate customer-safe communications, and maintain a shared incident history.

## Live Deployments

| Platform | URL | Status |
|---|---|---|
| Render | https://customer-outage-comms-drafter.onrender.com | ✅ Live |
| Vercel | https://customer-outage-comms-drafter.vercel.app | ✅ Live |

---

## Problem Statement

During service outages, technical teams have detailed timelines but no fast, consistent way to turn them into clear customer communications. Writing updates manually under pressure leads to delays, inconsistent tone, and messages that leak technical jargon to customers.

This platform solves that by combining AI-powered communication drafting with real-time team collaboration — so every team member sees the same incident, contributes to the same timeline, and produces consistent, jargon-free customer updates.

---

## Two Ways to Work

### 1. Incident Drafter (`/`)
Quick single-user mode. Enter a timeline update, the AI detects the phase and drafts a customer message. Best for solo responders who need to move fast.

### 2. Collaborative Workspace (`/workspace-page`)
Multi-user shared incident workspace. Create an incident, add collaborators, and every Incident Manager on the team can add timeline updates and generate communications on the same shared incident. Full activity history with "drafted by" attribution.

---

## How It Works

**Incident Drafter:**
1. Log in — first user becomes the Owner
2. Enter a single timeline update
3. AI auto-detects phase (Initial / In Progress / Resolved)
4. Matching communication card is populated
5. Click **Start New Incident** to save to shared history

**Collaborative Workspace:**
1. Owner or Incident Manager creates an incident workspace with a title and severity
2. Creator is automatically added as the first collaborator
3. Other team members can be added as collaborators
4. Each member can add timeline entries → AI generates customer message + internal summary
5. Full timeline visible to all members in real time
6. Owner or member can close the incident when resolved

---

## Features

| Feature | Description |
|---|---|
| JWT Authentication | Secure register/login with 12h token expiry |
| Role-Based Access Control | Owner, Incident Manager, Viewer with enforced permissions |
| Access Manager | Owner-only panel to grant/revoke team member roles |
| Collaborative Workspace | Shared incident with multiple collaborators — real-time timeline |
| Auto Phase Detection | Classifies timeline entries into initial / in-progress / resolved |
| Customer Message Generation | Jargon-free, tone-adjusted customer updates |
| Drafted By Attribution | History and workspace updates show which member drafted each entry |
| Shared Incident History | Last 5 incidents visible to all roles with full details |
| Delete Incident | Owner can delete any incident from shared history |
| Severity & Tone | Low/Medium/High severity, Calm/Empathetic/Concise tone |
| Internal Incident Log | Structured bullet-point summary for the incident team |
| Report Export | Download the full incident log as `.txt` |
| Viewer-Only Mode | Viewers see history only — input panel hidden, full-width layout |
| Persistent Data | All users, incidents, and workspaces stored in Supabase PostgreSQL |

---

## Roles & Permissions

| Role | Incident Drafter | Workspace | History | Delete | Access Manager |
|---|---|---|---|---|---|
| **Owner** | ✅ | ✅ Create + Collaborate | ✅ | ✅ | ✅ |
| **Incident Manager** | ✅ | ✅ Create + Collaborate | ✅ | ❌ | ❌ |
| **Viewer** | ❌ | ❌ | ✅ Read-only | ❌ | ❌ |

- The **first user to register** becomes the Owner — only one ever
- All other users default to **Viewer** until the Owner promotes them
- Owner uses **Access Manager** (header button) to assign roles

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML5, CSS3, Vanilla JavaScript |
| Backend | Python 3, Flask (Blueprint pattern) |
| AI Inference | Groq API — Llama 3.3 70B Versatile |
| Authentication | JWT (PyJWT) + werkzeug password hashing |
| Authorization | Role-based `@role_required` decorator |
| Database | Supabase PostgreSQL (via pg8000, pure Python) |
| Config | python-dotenv — `.env` based configuration |
| Deployment | Vercel (serverless), Render (web service) |

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
│   │   ├── routes.py           ← Incident Drafter API endpoints
│   │   ├── workspace.py        ← Collaborative Workspace blueprint
│   │   ├── auth.py             ← /auth/register, /auth/login
│   │   ├── auth_middleware.py  ← @jwt_required, @role_required decorators
│   │   ├── models.py           ← All DB models (users, incidents, workspaces)
│   │   └── prompts.py          ← AI prompt templates
│   ├── config.py
│   ├── requirements.txt
│   └── run.py
│
├── frontend/
│   ├── static/
│   │   ├── css/style.css       ← Main app styles
│   │   ├── css/auth.css        ← Auth + Access Manager styles
│   │   ├── css/workspace.css   ← Workspace page styles + nav
│   │   └── js/
│   │       ├── script.js       ← Incident Drafter logic
│   │       └── workspace.js    ← Workspace list + detail logic
│   └── templates/
│       ├── index.html          ← Incident Drafter
│       ├── workspace_list.html ← Workspace list page
│       ├── workspace_detail.html ← Workspace detail page
│       ├── login.html
│       └── register.html
│
├── docs/
├── .env.example
├── render.yaml
└── vercel.json
```

---

## Setup

### 1. Clone and install

```bash
git clone https://github.com/allenjosh-n/Customer-Outage-Comms-Drafter.git
cd Customer-Outage-Comms-Drafter
python -m venv venv && venv\Scripts\activate
pip install -r backend/requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
```

```env
GROQ_API_KEY=gsk_your_key_here
JWT_SECRET=your-long-random-secret
DATABASE_URL=postgresql://postgres.xxxx:password@aws-0-region.pooler.supabase.com:6543/postgres
```

### 3. Set up Supabase (first time)

Run in Supabase SQL Editor:

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
CREATE TABLE IF NOT EXISTS workspaces (
    id         SERIAL PRIMARY KEY,
    title      TEXT NOT NULL,
    severity   TEXT NOT NULL DEFAULT 'Medium',
    status     TEXT NOT NULL DEFAULT 'active',
    created_by TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS workspace_members (
    id           SERIAL PRIMARY KEY,
    workspace_id INTEGER NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    user_id      INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    username     TEXT NOT NULL,
    joined_at    TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(workspace_id, user_id)
);
CREATE TABLE IF NOT EXISTS workspace_updates (
    id               SERIAL PRIMARY KEY,
    workspace_id     INTEGER NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    created_by       TEXT NOT NULL,
    timeline         TEXT NOT NULL,
    phase            TEXT NOT NULL DEFAULT 'initial',
    customer_message TEXT NOT NULL DEFAULT '',
    summary_entry    TEXT NOT NULL DEFAULT '',
    created_at       TIMESTAMPTZ DEFAULT NOW()
);
```

### 4. Run locally

```bash
python backend/run.py
```

Open `http://127.0.0.1:5000` — first account you create will be the Owner.

---

## API Reference

### Auth
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/auth/register` | None | Register — first user becomes Owner |
| POST | `/auth/login` | None | Login, returns JWT + role |

### Incident Drafter
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/detect-phase` | Owner, Manager | Classify timeline entry |
| POST | `/generate` | Owner, Manager | Generate customer message |
| POST | `/incidents/save` | Owner, Manager | Save to shared history |
| GET | `/incidents` | All roles | Last 5 incidents |
| DELETE | `/incidents/<id>` | Owner only | Delete incident |

### Collaborative Workspace
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/workspace` | Owner, Manager | Create workspace |
| GET | `/workspace` | Owner, Manager | List all workspaces |
| GET | `/workspace/<id>` | Owner, Manager | Get workspace + members + updates |
| POST | `/workspace/<id>/updates` | Member, Owner | Add update + AI generate |
| POST | `/workspace/<id>/members` | Member, Owner | Add collaborator |
| DELETE | `/workspace/<id>/members/<uid>` | Owner | Remove collaborator |
| PATCH | `/workspace/<id>/status` | Member, Owner | Close workspace |

### Admin
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/admin/users` | Owner | List all users + roles |
| PATCH | `/admin/users/<id>/role` | Owner | Change user role |

---

## Deployment

Set these in Vercel → Settings → Environment Variables:

```
GROQ_API_KEY
JWT_SECRET
DATABASE_URL   ← Supabase pooler URL (port 6543)
```

---

## Future Enhancements

- Real-time updates via WebSockets (multiple people see new entries instantly)
- PDF / email export
- Incident analytics dashboard
- Webhook integration (PagerDuty, Slack, Microsoft Teams)
- Incident template library

---

## AI Tools Used During Development

| Tool | Role |
|---|---|
| Groq API + Llama 3.3 70B | Runtime AI inference engine |
| ChatGPT (OpenAI) | Prompt engineering and design |
| Kiro (Amazon) | Code assistance, debugging, deployment |
| GitHub Copilot | Inline code suggestions |

---

## License

MIT
