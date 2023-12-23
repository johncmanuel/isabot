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

DISCORD_CHANNEL_ID = handle_getenv("DISCORD_CHANNEL_ID")

BATTLENET_CLIENT_SECRET = handle_getenv("BATTLENET_CLIENT_SECRET")

BATTLENET_CLIENT_ID = handle_getenv("BATTLENET_CLIENT_ID")

PORT = int(handle_getenv("PORT", "8000"))

APP_URL = handle_getenv("APP_URL", f"https://localhost:{PORT}")

FIREBASE_PROJECT_ID = handle_getenv("FIREBASE_PROJECT_ID")

FIREBASE_CLIENT_EMAIL = handle_getenv("FIREBASE_CLIENT_EMAIL")

FIREBASE_PRIVATE_KEY = handle_getenv("FIREBASE_PRIVATE_KEY")
