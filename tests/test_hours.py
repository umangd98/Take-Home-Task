from datetime import datetime

from app.hours import is_business_hours


def test_weekday_morning_is_open():
    assert is_business_hours(datetime(2026, 11, 17, 9, 30)) is True  # Tuesday


def test_weekday_evening_is_closed():
    assert is_business_hours(datetime(2026, 11, 17, 19, 0)) is False


def test_weekend_is_closed():
    assert is_business_hours(datetime(2026, 11, 21, 11, 0)) is False  # Saturday
