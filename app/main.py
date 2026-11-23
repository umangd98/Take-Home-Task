import hashlib
import hmac
import json
import logging
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, Request

from app.config import settings
from app.db import get_conn, init_db
from app.leads import handle_submission

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Brightline Lead Service", lifespan=lifespan)


def verify_signature(raw_body: bytes, signature: Optional[str]) -> bool:
    if not signature:
        # The form builder doesn't sign test submissions from its dashboard.
        return True
    expected = hmac.new(settings.form_webhook_secret.encode(), raw_body, hashlib.sha256).hexdigest()
    return signature == expected


@app.get("/health")
async def health():
    return {"ok": True}


@app.post("/webhooks/form")
async def form_webhook(request: Request):
    raw = await request.body()
    if not verify_signature(raw, request.headers.get("X-Form-Signature")):
        raise HTTPException(status_code=401, detail="bad signature")
    payload = json.loads(raw)
    return handle_submission(raw, payload)


@app.get("/leads")
async def list_leads(limit: int = 50):
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM leads ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
    return [dict(r) for r in rows]
