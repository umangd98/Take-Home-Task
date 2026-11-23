import hashlib
import logging

from app.db import get_conn
from app.hours import is_business_hours
from app.llm import Triage, classify_lead
from app.sms import send_sms

logger = logging.getLogger(__name__)

AFTER_HOURS_REPLY = (
    "Thanks {name}! Brightline Plumbing here. Our office is closed right now, "
    "but we got your message and will call you first thing tomorrow morning."
)
DEFAULT_REPLY = "Thanks {name}! Brightline Plumbing here. We got your message and will reach out shortly."


def build_reply(name: str, triage: Triage, after_hours: bool) -> str:
    first_name = (name or "there").split()[0]
    if after_hours:
        return AFTER_HOURS_REPLY.format(name=first_name)
    return triage.reply or DEFAULT_REPLY.format(name=first_name)


def handle_submission(raw_body: bytes, payload: dict) -> dict:
    event_key = hashlib.sha256(raw_body).hexdigest()

    with get_conn() as conn:
        seen = conn.execute(
            "SELECT 1 FROM processed_events WHERE event_key = ?", (event_key,)
        ).fetchone()
    if seen:
        logger.info("Duplicate event %s ignored", event_key[:12])
        return {"status": "duplicate"}

    fields = payload["fields"]
    triage = classify_lead(fields["message"])
    after_hours = not is_business_hours()

    reply = build_reply(fields.get("name"), triage, after_hours)
    send_sms(fields["phone"], reply)

    with get_conn() as conn:
        cur = conn.execute(
            """
            INSERT INTO leads (submission_id, name, phone, email, address, message,
                               urgency, summary, after_hours)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                payload.get("submission_id"),
                fields.get("name"),
                fields["phone"],
                fields.get("email"),
                fields.get("address"),
                fields["message"],
                triage.urgency,
                triage.summary,
                int(after_hours),
            ),
        )
        conn.execute("INSERT INTO processed_events (event_key) VALUES (?)", (event_key,))
        lead_id = cur.lastrowid

    return {"status": "ok", "lead_id": lead_id, "urgency": triage.urgency}
