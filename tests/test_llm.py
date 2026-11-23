import json

from app.llm import _parse


def test_parse_valid_response():
    raw = json.dumps({"urgency": "emergency", "summary": "Burst pipe", "reply": "On our way."})
    triage = _parse(raw)
    assert triage.urgency == "emergency"
    assert triage.reply == "On our way."


def test_parse_unknown_urgency_falls_back():
    raw = json.dumps({"urgency": "whenever", "summary": "", "reply": None})
    assert _parse(raw).urgency == "routine"
