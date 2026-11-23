import json


def _payload(**fields):
    base = {
        "name": "Jane Doe",
        "phone": "+15125550100",
        "email": "jane@example.com",
        "address": "1 Main St, Austin, TX",
        "message": "Dripping faucet in the kitchen.",
    }
    base.update(fields)
    return {
        "submission_id": "sub_test123",
        "form_id": "contact-v2",
        "submitted_at": "2026-11-17T15:00:00+00:00",
        "delivered_at": "2026-11-17T15:00:01+00:00",
        "fields": base,
    }


def test_health(client):
    assert client.get("/health").json() == {"ok": True}


def test_new_lead_is_saved_and_texted(client):
    resp = client.post("/webhooks/form", content=json.dumps(_payload()))
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"

    leads = client.get("/leads").json()
    assert len(leads) == 1
    assert leads[0]["phone"] == "+15125550100"

    sent = client.outbox.read_text().strip().splitlines()
    assert len(sent) == 1


def test_duplicate_delivery_is_ignored(client):
    body = json.dumps(_payload())
    client.post("/webhooks/form", content=body)
    resp = client.post("/webhooks/form", content=body)
    assert resp.json()["status"] == "duplicate"

    sent = client.outbox.read_text().strip().splitlines()
    assert len(sent) == 1


def test_bad_signature_rejected(client):
    resp = client.post(
        "/webhooks/form",
        content=json.dumps(_payload()),
        headers={"X-Form-Signature": "not-a-real-signature"},
    )
    assert resp.status_code == 401
