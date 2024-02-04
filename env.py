from os import getenv
from typing import Any

from dotenv import load_dotenv


def handle_getenv(env: str, default: Any = None):
    """
    Retrieve an environment variable. Ensure that the env variables are not None.
    """
    value = getenv(env, default)
    if not value:
        raise ValueError(f"Environment variable {env} is not set.")
    return value


load_dotenv()

# DISCORD_TOKEN: Discord token for this application
DISCORD_TOKEN = handle_getenv("DISCORD_TOKEN")

# DISCORD_APP_ID: Discord application ID for this application
DISCORD_APP_ID = handle_getenv("DISCORD_APP_ID")

# DISCORD_PUBLIC_KEY: Discord public key for this application
DISCORD_PUBLIC_KEY = handle_getenv("DISCORD_PUBLIC_KEY")

# DISCORD_WEBHOOK_URL: Discord webhook URL for a specific channel within a
# Discord server. This will be used to send leaderboard data to that channel.
DISCORD_WEBHOOK_URL = handle_getenv("DISCORD_WEBHOOK_URL")

# BATTLENET_CLIENT_SECRET: Battle.net developer client secret for
# this application
BATTLENET_CLIENT_SECRET = handle_getenv("BATTLENET_CLIENT_SECRET")

# BATTLENET_CLIENT_ID: Battle.net developer client ID for this
# application
BATTLENET_CLIENT_ID = handle_getenv("BATTLENET_CLIENT_ID")

# PORT: Port number for the application. Defaults to 8000.
PORT = int(handle_getenv("PORT", "8000"))

# APP_URL: URL for the application. Defaults to https://localhost:<PORT>
APP_URL = handle_getenv("APP_URL", f"https://localhost:{PORT}")

# FIREBASE_PROJECT_ID: Firebase project ID for this application's
# database
FIREBASE_PROJECT_ID = handle_getenv("FIREBASE_PROJECT_ID")

# FIREBASE_CLIENT_EMAIL: Firebase client email for this application's
# database
FIREBASE_CLIENT_EMAIL = handle_getenv("FIREBASE_CLIENT_EMAIL")

# FIREBASE_PRIVATE_KEY: Firebase private key for this application's
# database.
FIREBASE_PRIVATE_KEY = handle_getenv("FIREBASE_PRIVATE_KEY")

# MIDDLEWARE_SECRET: Secret key for the middleware
MIDDLEWARE_SECRET = handle_getenv("MIDDLEWARE_SECRET")

# GOOGLE_SERVICE_ACCOUNT: Google service account for this application
GOOGLE_SERVICE_ACCOUNT = handle_getenv("GOOGLE_SERVICE_ACCOUNT")

# CURRENT_ENV: Sets the current environment: either development or production (by default)
CURRENT_ENV = handle_getenv("CURRENT_ENV", "production")
