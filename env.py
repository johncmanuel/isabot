from os import getenv
from typing import Any

from dotenv import load_dotenv


def handle_getenv(env: str, default: Any = None):
    """Ensures that the env variables are not None."""
    value = getenv(env, default)
    if not value:
        raise ValueError(f"Environment variable {env} is not set.")
    return value


load_dotenv()

DISCORD_TOKEN = handle_getenv("DISCORD_TOKEN")

DISCORD_APP_ID = handle_getenv("DISCORD_APP_ID")

DISCORD_PUBLIC_KEY = handle_getenv("DISCORD_PUBLIC_KEY")

DISCORD_WEBHOOK_URL = handle_getenv("DISCORD_WEBHOOK_URL")

BATTLENET_CLIENT_SECRET = handle_getenv("BATTLENET_CLIENT_SECRET")

BATTLENET_CLIENT_ID = handle_getenv("BATTLENET_CLIENT_ID")

PORT = int(handle_getenv("PORT", "8000"))
