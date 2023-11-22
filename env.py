from dotenv import load_dotenv
from os import getenv

load_dotenv()

DISCORD_TOKEN = getenv("DISCORD_TOKEN")

DISCORD_APP_ID = getenv("DISCORD_APP_ID")

DISCORD_PUBLIC_KEY = getenv("DISCORD_PUBLIC_KEY")

PORT = getenv("PORT")