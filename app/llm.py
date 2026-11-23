import hashlib
import json
import logging
import random
import time
from dataclasses import dataclass
from typing import Optional

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

URGENCY_LEVELS = ("emergency", "soon", "routine")

PROMPT = """You are a helpful assistant for Brightline Plumbing in Austin, TX.

Read the customer's message and respond with JSON containing:
- "urgency": one of emergency, soon, routine
- "summary": a one-line summary for the dispatcher
- "reply": a short, friendly SMS reply to the customer (under 300 characters)

Customer message:
{message}
"""


@dataclass
class Triage:
    urgency: str
    summary: str
    reply: Optional[str]


def classify_lead(message: str) -> Triage:
    text = message.strip()[: settings.max_message_chars]
    prompt = PROMPT.format(message=text)

    if settings.llm_mode == "openai_compat":
        raw = _call_openai_compat(prompt)
    elif settings.llm_mode == "anthropic":
        raw = _call_anthropic(prompt)
    else:
        raw = _mock_llm(text)

    return _parse(raw)


def _parse(raw: str) -> Triage:
    try:
        data = json.loads(raw)
        urgency = data["urgency"]
        if urgency not in URGENCY_LEVELS:
            urgency = "routine"
        return Triage(urgency=urgency, summary=data.get("summary", ""), reply=data.get("reply"))
    except (KeyError, ValueError):
        logger.warning("Could not parse LLM response, using defaults")
        return Triage(urgency="routine", summary="", reply=None)


def _call_openai_compat(prompt: str) -> str:
    headers = {"content-type": "application/json"}
    if settings.llm_api_key:
        headers["authorization"] = f"Bearer {settings.llm_api_key}"
    resp = httpx.post(
        f"{settings.llm_base_url.rstrip('/')}/chat/completions",
        headers=headers,
        json={
            "model": settings.llm_model,
            "max_tokens": 400,
            "messages": [{"role": "user", "content": prompt}],
        },
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def _call_anthropic(prompt: str) -> str:
    resp = httpx.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": settings.anthropic_api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": settings.llm_model,
            "max_tokens": 400,
            "messages": [{"role": "user", "content": prompt}],
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["content"][0]["text"]


# ---------------------------------------------------------------------------
# Mock model so the service runs locally without keys. Latency and output are
# modeled on what we logged from the hosted model in production.
# ---------------------------------------------------------------------------

_EMERGENCY_WORDS = ("burst", "flood", "water coming", "ceiling", "sewage", "gas smell", "no water at all")
_SOON_WORDS = ("no hot water", "leak", "clog", "backed up", "running toilet", "won't drain")


def _mock_llm(text: str) -> str:
    if settings.mock_llm_latency > 0:
        time.sleep(random.uniform(0.3, 1.0) * settings.mock_llm_latency)
    lower = text.lower()

    if any(w in lower for w in _EMERGENCY_WORDS):
        urgency = "emergency"
    elif any(w in lower for w in _SOON_WORDS):
        urgency = "soon"
    else:
        urgency = "routine"

    bucket = int(hashlib.md5(text.encode()).hexdigest(), 16) % 4
    if bucket == 1:
        urgency = urgency.capitalize()

    body = json.dumps(
        {
            "urgency": urgency,
            "summary": text[:80],
            "reply": "Thanks for reaching out to Brightline Plumbing! A team member will contact you shortly.",
        }
    )
    if bucket == 2:
        return f"Here is the classification:\n```json\n{body}\n```"
    return body
