from datetime import datetime
from typing import Optional

from app.config import settings


def is_business_hours(now: Optional[datetime] = None) -> bool:
    now = now or datetime.now()
    if now.weekday() >= 5:  # Saturday, Sunday
        return False
    return settings.business_open_hour <= now.hour < settings.business_close_hour
