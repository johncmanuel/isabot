from dotenv import load_dotenv
from os import getenv

load_dotenv()

DISCORD_TOKEN = getenv("DISCORD_TOKEN")

DISCORD_APP_ID = getenv("DISCORD_APP_ID")

DISCORD_PUBLIC_KEY = getenv("DISCORD_PUBLIC_KEY")

BATTLENET_CLIENT_SECRET = getenv("BATTLENET_CLIENT_SECRET")

BATTLENET_CLIENT_ID = getenv("BATTLENET_CLIENT_ID")

PORT = int(getenv("PORT"))