# Customer Outage Comms Drafter

An AI-powered, role-based collaborative incident communication platform.

---

## Two Modes

| Mode | URL | Who |
|---|---|---|
| Incident Drafter | `/` | Quick single-user drafting |
| Collaborative Workspace | `/workspace-page` | Multi-user shared incident |

---

## Project Structure

```
├── backend/app/
│   ├── routes.py           ← Incident Drafter API
│   ├── workspace.py        ← Collaborative Workspace API
│   ├── auth.py             ← Register / Login
│   ├── auth_middleware.py  ← @jwt_required, @role_required
│   ├── models.py           ← All DB models
│   └── prompts.py          ← AI prompt templates
│
├── frontend/
│   ├── static/css/
│   │   ├── style.css       ← Main styles
│   │   ├── auth.css        ← Auth + Access Manager
│   │   └── workspace.css   ← Workspace + nav
│   ├── static/js/
│   │   ├── script.js       ← Drafter logic
│   │   └── workspace.js    ← Workspace logic
│   └── templates/
│       ├── index.html
│       ├── workspace_list.html
│       ├── workspace_detail.html
│       ├── login.html
│       └── register.html
```

---

## Roles

| Role | Drafter | Workspace | History | Delete | Access Manager |
|---|---|---|---|---|---|
| Owner | ✅ | ✅ | ✅ | ✅ | ✅ |
| Incident Manager | ✅ | ✅ | ✅ | ❌ | ❌ |
| Viewer | ❌ | ❌ | ✅ | ❌ | ❌ |

First user to register = Owner. All others default to Viewer.

---

## Setup

```bash
git clone https://github.com/allenjosh-n/Customer-Outage-Comms-Drafter.git
cd Customer-Outage-Comms-Drafter
python -m venv venv && venv\Scripts\activate
pip install -r backend/requirements.txt
cp .env.example .env   # fill in GROQ_API_KEY, JWT_SECRET, DATABASE_URL
python backend/run.py
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML, CSS, JavaScript |
| Backend | Python, Flask |
| AI | Groq API — Llama 3.3 70B |
| Auth | JWT + werkzeug |
| Authorization | Role-based `@role_required` |
| Database | Supabase PostgreSQL (pg8000) |

---

## Environment Variables

| Variable | Description |
|---|---|
| `GROQ_API_KEY` | Groq API key |
| `JWT_SECRET` | JWT signing secret |
| `DATABASE_URL` | Supabase pooler URL (port 6543) |

---

See [AI_USAGE.md](AI_USAGE.md) for prompt documentation.
