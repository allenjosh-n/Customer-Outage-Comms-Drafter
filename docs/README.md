# Customer Outage Comms Drafter

An AI-powered incident communication tool with role-based access control, shared incident history, and a team Access Manager.

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
│   │   ├── auth.py             ← /auth/register, /auth/login
│   │   ├── auth_middleware.py  ← @jwt_required, @role_required
│   │   ├── models.py           ← User + incident model (Supabase + SQLite)
│   │   └── prompts.py          ← AI prompt templates
│   ├── config.py               ← Environment loader
│   ├── requirements.txt
│   └── run.py                  ← Local entry point
│
├── frontend/
│   ├── static/
│   │   ├── css/style.css
│   │   ├── css/auth.css        ← Auth + Access Manager styles
│   │   └── js/script.js
│   └── templates/
│       ├── index.html
│       ├── login.html
│       └── register.html
│
├── docs/
│   ├── README.md               ← This file
│   └── AI_USAGE.md
│
└── .env.example
```

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

Open `http://127.0.0.1:5000` — first account becomes the Owner.

---

## Roles

| Role | Generate | History | Delete | Access Manager |
|---|---|---|---|---|
| Owner | ✅ | ✅ | ✅ | ✅ |
| Incident Manager | ✅ | ✅ | ❌ | ❌ |
| Viewer | ❌ | ✅ | ❌ | ❌ |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML, CSS, JavaScript |
| Backend | Python, Flask |
| AI | Groq API — Llama 3.3 70B |
| Auth | JWT (PyJWT) + werkzeug |
| Authorization | Role-based `@role_required` decorator |
| Database | Supabase PostgreSQL (pg8000) |

---

## Environment Variables

| Variable | Description |
|---|---|
| `GROQ_API_KEY` | Groq API key |
| `JWT_SECRET` | JWT signing secret |
| `DATABASE_URL` | Supabase pooler URL (port 6543) |

---

## AI Usage

See [AI_USAGE.md](AI_USAGE.md) for prompt design documentation.
