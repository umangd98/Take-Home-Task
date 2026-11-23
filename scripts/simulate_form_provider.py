"""Replays sample leads the way Brightline's form builder delivers them.

The form builder POSTs each submission to our webhook, signs it with the
shared secret, waits up to 2 seconds for a response, and retries up to
3 times on a timeout or a 5xx.

Usage:
    python scripts/simulate_form_provider.py                # all sample leads
    python scripts/simulate_form_provider.py --only 1       # just one lead (1-based)
    python scripts/simulate_form_provider.py --url http://localhost:8000
"""

import argparse
import hashlib
import hmac
import json
import os
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

import httpx

SECRET = os.getenv("FORM_WEBHOOK_SECRET", "bl_whsec_4f9a1c7e2b8d6035aa71")
TIMEOUT_SECONDS = 2.0
MAX_ATTEMPTS = 3
SAMPLES = Path(__file__).resolve().parent.parent / "data" / "sample_leads.json"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def deliver(url: str, fields: dict) -> None:
    submission_id = f"sub_{uuid.uuid4().hex[:16]}"
    submitted_at = now_iso()

    for attempt in range(1, MAX_ATTEMPTS + 1):
        payload = {
            "submission_id": submission_id,
            "form_id": "contact-v2",
            "submitted_at": submitted_at,
            "delivered_at": now_iso(),
            "fields": fields,
        }
        body = json.dumps(payload).encode()
        signature = hmac.new(SECRET.encode(), body, hashlib.sha256).hexdigest()
        try:
            resp = httpx.post(
                f"{url}/webhooks/form",
                content=body,
                headers={"content-type": "application/json", "X-Form-Signature": signature},
                timeout=TIMEOUT_SECONDS,
            )
            if resp.status_code < 500:
                print(f"  {submission_id} attempt {attempt}: {resp.status_code} {resp.text[:120]}")
                return
            print(f"  {submission_id} attempt {attempt}: {resp.status_code}, retrying")
        except httpx.TimeoutException:
            print(f"  {submission_id} attempt {attempt}: timed out, retrying")
        time.sleep(0.5 * attempt)

    print(f"  {submission_id}: gave up after {MAX_ATTEMPTS} attempts")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://localhost:8000")
    parser.add_argument("--only", type=int, help="1-based index of a single sample lead")
    args = parser.parse_args()

    leads = json.loads(SAMPLES.read_text())
    if args.only:
        leads = [leads[args.only - 1]]

    for fields in leads:
        print(f"Delivering lead from {fields.get('name')}")
        deliver(args.url, fields)


if __name__ == "__main__":
    main()
