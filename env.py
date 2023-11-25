from os import getenv

from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = getenv("DISCORD_TOKEN")

DISCORD_APP_ID = getenv("DISCORD_APP_ID")

DISCORD_PUBLIC_KEY = getenv("DISCORD_PUBLIC_KEY")

DISCORD_WEBHOOK_URL = getenv("DISCORD_WEBHOOK_URL")

BATTLENET_CLIENT_SECRET = getenv("BATTLENET_CLIENT_SECRET")

BATTLENET_CLIENT_ID = getenv("BATTLENET_CLIENT_ID")

PORT = int(getenv("PORT", "8000"))
