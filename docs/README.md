# Customer Outage Comms Drafter

An AI-powered web application that converts raw incident timelines into professional, customer-safe communications — automatically detecting the phase (initial, in-progress, or resolved) and drafting the right message each time.

---

## Project Structure

```
project/
├── backend/                  ← Flask application
│   ├── app/
│   │   ├── __init__.py       ← App factory
│   │   ├── routes.py         ← API endpoints
│   │   └── prompts.py        ← AI prompt templates
│   ├── config.py             ← Loads GROQ_API_KEY from .env
│   ├── requirements.txt      ← Python dependencies
│   └── run.py                ← Entry point
│
├── frontend/                 ← UI layer
│   ├── static/
│   │   ├── css/style.css     ← Styles
│   │   └── js/script.js      ← Client-side logic
│   └── templates/
│       └── index.html        ← Single-page UI
│
├── docs/                     ← Documentation
│   ├── README.md             ← This file
│   └── AI_USAGE.md           ← AI tools & prompt documentation
│
├── tests/
│   └── test_groq.py          ← Groq API connectivity test
│
├── .env                      ← API key (never commit this)
├── .env.example              ← Safe template to share
└── .gitignore
```

---

## Setup

### 1. Clone and enter the project

```bash
git clone <repository-url>
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

### 4. Configure your API key

Copy `.env.example` to `.env` and add your Groq API key:

```bash
cp .env.example .env
```

Edit `.env`:

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

## How It Works

1. Enter a single timeline update (e.g. `09:00 — Users unable to log in`)
2. Click **Draft Update**
3. The AI classifies it as `initial`, `progress`, or `resolved`
4. Only the matching card is populated — others stay locked
5. Each update appends to the Incident Summary Log
6. Once complete, download the full report as a `.txt` file

---

## Tech Stack

| Layer    | Technology                  |
|----------|-----------------------------|
| Frontend | HTML, CSS, JavaScript       |
| Backend  | Python, Flask               |
| AI       | Groq API — Llama 3.3 70B    |

---

## AI Usage

See [AI_USAGE.md](AI_USAGE.md) for full details on AI tools used and prompt design.
