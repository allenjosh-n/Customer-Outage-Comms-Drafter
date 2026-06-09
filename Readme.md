# Customer Outage Comms Drafter

## Overview

Customer Outage Comms Drafter is an AI-powered web application that helps incident response teams quickly generate professional customer communications during service outages.

The application converts technical incident timelines into clear, customer-friendly updates, reducing manual effort and improving communication consistency during critical incidents.

---

## Problem Statement

During service outages, technical teams often have detailed incident timelines but struggle to quickly create clear and professional customer communications.

This project automates the communication process by generating:

* Initial Customer Update
* Progress Update
* Resolved Update
* Internal Incident Summary

based on incident details, severity level, and communication tone.

---

## Features

### AI-Powered Communication Generation

Automatically converts technical outage timelines into customer-friendly messages.

### Severity Selection

Supports:

* Low
* Medium
* High

severity levels.

### Tone Selection

Supports different communication styles:

* Calm
* Empathetic
* Concise

### Internal Incident Summary

Generates a structured internal summary for incident management and reporting.

### Copy to Clipboard

Allows users to quickly copy generated communications for sharing through various channels.

### Modern Responsive UI

Simple and professional interface suitable for operational teams.

---

## Technology Stack

### Frontend

* HTML5
* CSS3
* JavaScript

### Backend

* Python
* Flask

### AI Model

* Groq API
* Llama 3.3 70B Versatile

---

## Project Structure

```text
Customer-Outage-Comms-Drafter/
│
├── app.py
├── config.py
├── requirements.txt
│
├── templates/
│   └── index.html
│
├── static/
│   ├── style.css
│   └── script.js
│
└── README.md
```

---

## Installation

### Clone Repository

```bash
git clone <repository-url>
cd Customer-Outage-Comms-Drafter
```

### Create Virtual Environment

```bash
python -m venv venv
```

### Activate Virtual Environment

Windows:

```bash
venv\Scripts\activate
```

Linux/Mac:

```bash
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Configuration

Create a file named:

```text
config.py
```

Add your Groq API key:

```python
GROQ_API_KEY = "your_groq_api_key"
```

---

## Run Application

```bash
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

---

## Sample Input

### Timeline

```text
09:00 AM - Payment transactions failing for multiple customers

09:10 AM - Incident response team activated

09:30 AM - Root cause traced to payment gateway outage

10:00 AM - Temporary workaround deployed

10:30 AM - Payment processing restored

10:45 AM - Monitoring confirms stability
```

### Severity

```text
High
```

### Tone

```text
Empathetic
```

---

## Expected Output

### Initial Update

Customer-friendly communication acknowledging the issue.

### Progress Update

Communication explaining ongoing efforts and progress.

### Resolved Update

Confirmation that services have been restored.

### Internal Incident Summary

Structured summary containing:

* Incident Start Time
* Investigation Details
* Root Cause Information
* Resolution Time
* Severity Classification

---

## Future Enhancements

* PDF Export
* Email Integration
* Multi-language Support
* Incident Analytics Dashboard
* Automated Status Reports
* Cloud Deployment

---

## Benefits

* Reduces manual communication effort
* Improves consistency of outage messaging
* Enhances customer experience
* Supports incident management teams
* Accelerates communication during critical outages

---

## AI Usage

This project was built with the assistance of several AI tools.

Full details are documented in [AI_USAGE.md](AI_USAGE.md), including:

* Which AI tools were used and their roles
* The core runtime prompt sent to the Groq/Llama model
* The ChatGPT prompt used to design the runtime prompt
* Prompt design rationale

### Tools Used

| Tool | Role |
|---|---|
| ChatGPT (OpenAI) | Prompt engineering and generation |
| Antigravity (Google) | Code optimization and project setup |
| Groq API + Llama 3.3 70B | Runtime AI inference engine |
| GitHub Copilot | Inline code suggestions |

---

