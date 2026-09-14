# Customer Outage Comms Drafter

An AI-powered web application that converts raw incident timelines into professional, customer-safe communications — automatically detecting the phase (initial, in-progress, or resolved) and drafting the right message each time.

---

## Project Structure

```
project/
├── api/
│   └── index.py              ← Vercel serverless entry point
│
├── backend/                  ← Flask application
│   ├── app/
│   │   ├── __init__.py       ← App factory
│   │   ├── routes.py         ← API endpoints (/detect-phase, /generate)
│   │   ├── auth.py           ← Auth routes (/auth/register, /auth/login)
│   │   ├── auth_middleware.py← JWT decorator
│   │   ├── models.py         ← User model (Supabase PostgreSQL)
│   │   └── prompts.py        ← AI prompt templates
│   ├── config.py             ← Environment variable loader
│   ├── requirements.txt      ← Python dependencies
│   └── run.py                ← Local entry point
│
├── frontend/                 ← UI layer
│   ├── static/
│   │   ├── css/style.css     ← App styles
│   │   ├── css/auth.css      ← Auth page styles
│   │   └── js/script.js      ← Client-side logic
│   └── templates/
│       ├── index.html        ← Main app
│       ├── login.html        ← Login page
│       └── register.html     ← Register page
│
├── docs/                     ← Documentation
│   ├── README.md             ← This file
│   └── AI_USAGE.md           ← AI tools & prompt documentation
│
├── tests/
│   └── test_groq.py          ← Groq API connectivity test
│
├── .env                      ← Secrets (never commit this)
├── .env.example              ← Safe template to share
└── .gitignore
```

---

## Setup

### 1. Clone and enter the project

```bash
git clone https://github.com/allenjosh-n/Customer-Outage-Comms-Drafter.git
cd Customer-Outage-Comms-Drafter
```

### 2. Create and activate virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r backend/requirements.txt
```

### 4. Configure environment variables

Copy `.env.example` to `.env` and fill in your values:

```env
GROQ_API_KEY=gsk_your_key_here
JWT_SECRET=your-long-random-secret
DATABASE_URL=postgresql://postgres.xxxx:password@aws-0-region.pooler.supabase.com:6543/postgres
```

- Groq key: [console.groq.com](https://console.groq.com)
- Supabase DB: [supabase.com](https://supabase.com) → Project Settings → Database → Connection string (use port 6543 pooler URL)

### 5. Run the app

```bash
python backend/run.py
```

Open `http://127.0.0.1:5000` — redirects to login page automatically.

---

## How It Works

1. Register or log in to your account
2. Enter a single timeline update (e.g. `09:00 — Users unable to log in`)
3. Click **Draft Update**
4. The AI classifies it as `initial`, `progress`, or `resolved`
5. Only the matching card is populated — others stay locked
6. Each update appends to the Incident Summary Log
7. Download the full report as a `.txt` file when done

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML, CSS, JavaScript |
| Backend | Python, Flask |
| AI | Groq API — Llama 3.3 70B |
| Auth | JWT (PyJWT) + werkzeug hashing |
| Database | Supabase PostgreSQL (pg8000) |

---

## Environment Variables

| Variable | Description |
|---|---|
| `GROQ_API_KEY` | Groq API key for AI inference |
| `JWT_SECRET` | Secret for signing JWT tokens |
| `DATABASE_URL` | Supabase PostgreSQL pooler connection string |

---

## AI Usage

See [AI_USAGE.md](AI_USAGE.md) for full details on AI tools used and prompt design.
