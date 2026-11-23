import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

os.environ.setdefault("MOCK_LLM_LATENCY", "0")


@pytest.fixture()
def client(tmp_path, monkeypatch):
    from app import config

    test_settings = config.Settings(
        db_path=str(tmp_path / "test.db"),
        sms_outbox_path=str(tmp_path / "outbox.jsonl"),
        mock_llm_latency=0,
    )
    for module in ("app.config", "app.db", "app.llm", "app.sms", "app.hours", "app.main"):
        monkeypatch.setattr(f"{module}.settings", test_settings, raising=False)

    from fastapi.testclient import TestClient

    from app.main import app

    with TestClient(app) as c:
        c.outbox = tmp_path / "outbox.jsonl"
        yield c
