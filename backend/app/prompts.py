"""
AI prompt templates.
Isolated here so they can be tuned independently of routing logic.
"""


def phase_detection_prompt(timeline: str) -> str:
    """Classify a single timeline entry into one incident phase."""
    return f"""You are classifying an IT incident timeline entry into exactly one phase.

Timeline entry:
\"\"\"{timeline}\"\"\"

Rules:
- Reply with ONLY one word — no punctuation, no explanation.
- Reply "initial"  if the entry describes an issue being DETECTED or IDENTIFIED for the first time.
- Reply "progress" if the entry describes the team INVESTIGATING, WORKING ON, or MITIGATING the issue.
- Reply "resolved" if the entry describes the issue being FIXED, RESTORED, or RESOLVED.
- If unsure, reply "initial".

Your one-word answer:"""


def communication_prompt(timeline: str, severity: str, tone: str, phase: str) -> str:
    """Generate a customer-facing message and internal log entry for a given phase."""
    phase_labels = {
        "initial":  "INITIAL ALERT",
        "progress": "IN-PROGRESS UPDATE",
        "resolved": "RESOLVED UPDATE",
    }
    phase_label = phase_labels.get(phase, "INITIAL ALERT")

    return f"""You are an outage communication specialist.

Technical Timeline Entry:
{timeline}

Severity: {severity}
Tone: {tone}
Phase: {phase_label}

Generate exactly in this format — nothing else:

CUSTOMER_MESSAGE:
<Write a single customer-facing {phase_label} message. Do NOT mention databases, servers, APIs, or technical components. Use clear, {tone.lower()} language.>

SUMMARY_ENTRY:
<Write 2-4 bullet points for the internal incident log for this phase. Include technical details, timeline reference, and what action was taken or is being taken.>

Rules:
- Output ONLY the two sections above, in that exact order.
- CUSTOMER_MESSAGE must be plain prose, 2-4 sentences.
- SUMMARY_ENTRY must use bullet points starting with "•".
- Reflect severity level: {severity}.
"""
