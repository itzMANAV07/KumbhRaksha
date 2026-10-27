"""
Application configuration loaded from environment variables.
All thresholds from AGENTS.md Section 8.
"""
import os
import pathlib
from dotenv import load_dotenv
from pydantic import ConfigDict
from pydantic_settings import BaseSettings

_root_env = pathlib.Path(__file__).resolve().parent.parent.parent / ".env"
_backend_env = pathlib.Path(__file__).resolve().parent.parent / ".env"
if _backend_env.exists():
    load_dotenv(_backend_env)
if _root_env.exists():
    load_dotenv(_root_env)


class Settings(BaseSettings):
    model_config = ConfigDict(env_file=(".env", str(_root_env), str(_backend_env)), env_file_encoding="utf-8", extra="ignore")

    # Database
    database_url: str = "sqlite+aiosqlite:///./kumbh.db"

    # Telegram (required only for M7)
    telegram_bot_token: str = ""
    telegram_webhook_secret: str = ""

    # Web Dashboard URL (for Telegram bot & chat redirection, supports Vercel and custom domains)
    dashboard_url: str = (
        os.getenv("DASHBOARD_URL")
        or (f"https://{os.getenv('VERCEL_PROJECT_PRODUCTION_URL')}" if os.getenv("VERCEL_PROJECT_PRODUCTION_URL") else None)
        or (f"https://{os.getenv('VERCEL_URL')}" if os.getenv("VERCEL_URL") else None)
        or "https://kumbhraksha.org.in"
    )

    # LLM (optional)
    gemini_api_key: str = ""

    # Simulator
    sim_tick_seconds: int = 5

    # Alerts
    alert_cooldown_minutes: int = 10

    # Risk thresholds (p/m²) — per AGENTS.md Section 8
    # green  < 1.0 | yellow 1.0-2.5 | orange 2.5-4.0 | red >= 4.0
    density_yellow: float = 1.0
    density_orange: float = 2.5
    density_red: float = 4.0
    forecast_window_minutes: int = 30


settings = Settings()
