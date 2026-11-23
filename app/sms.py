import json
import logging
import os
from datetime import datetime, timezone

from app.config import settings

logger = logging.getLogger(__name__)


def send_sms(to: str, body: str) -> bool:
    if settings.sms_mode == "mock":
        return _mock_send(to, body)
    raise NotImplementedError("Twilio sending is configured on the production server only")


def _mock_send(to: str, body: str) -> bool:
    folder = os.path.dirname(settings.sms_outbox_path)
    if folder:
        os.makedirs(folder, exist_ok=True)
    record = {
        "sent_at": datetime.now(timezone.utc).isoformat(),
        "from": settings.sms_from,
        "to": to,
        "body": body,
    }
    with open(settings.sms_outbox_path, "a") as f:
        f.write(json.dumps(record) + "\n")
    logger.info("SMS sent to %s", to)
    return True
