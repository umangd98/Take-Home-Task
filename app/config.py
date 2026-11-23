import os
from dataclasses import dataclass, field


def _env_float(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, default))
    except ValueError:
        return default


@dataclass(frozen=True)
class Settings:
    db_path: str = field(default_factory=lambda: os.getenv("BRIGHTLINE_DB", "data/brightline.db"))

    # LLM
    llm_mode: str = field(default_factory=lambda: os.getenv("LLM_MODE", "mock"))  # mock | openai_compat | anthropic
    llm_model: str = field(default_factory=lambda: os.getenv("LLM_MODEL", "llama3.2"))
    # Any OpenAI-compatible endpoint: Ollama, Groq, Gemini, OpenRouter, OpenAI...
    llm_base_url: str = field(default_factory=lambda: os.getenv("LLM_BASE_URL", "http://localhost:11434/v1"))
    llm_api_key: str = field(default_factory=lambda: os.getenv("LLM_API_KEY", ""))
    anthropic_api_key: str = field(default_factory=lambda: os.getenv("ANTHROPIC_API_KEY", ""))
    mock_llm_latency: float = field(default_factory=lambda: _env_float("MOCK_LLM_LATENCY", 2.8))
    # One SMS segment. Keeps prompts small and token cost predictable.
    max_message_chars: int = 160

    # SMS
    sms_mode: str = field(default_factory=lambda: os.getenv("SMS_MODE", "mock"))  # mock | twilio
    sms_from: str = "+15125550199"
    sms_outbox_path: str = field(default_factory=lambda: os.getenv("SMS_OUTBOX", "data/sms_outbox.jsonl"))

    # Form provider
    form_webhook_secret: str = field(
        default_factory=lambda: os.getenv("FORM_WEBHOOK_SECRET", "bl_whsec_4f9a1c7e2b8d6035aa71")
    )

    # Business
    business_name: str = "Brightline Plumbing"
    business_tz: str = "America/Chicago"
    business_open_hour: int = 8
    business_close_hour: int = 18


settings = Settings()
