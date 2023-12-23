# https://develop.battle.net/documentation/world-of-warcraft/guides/namespaces
BATTLENET_REGION = "us"

BATTLENET_NAMESPACES = {
    "Static": f"static-{BATTLENET_REGION}",
    "Dynamic": f"dynamic-{BATTLENET_REGION}",
    "Profile": f"profile-{BATTLENET_REGION}",
}

BATTLENET_LOCALE = "en_US"

BATTLENET_URL = f"{BATTLENET_REGION}.api.blizzard.com"

BATTLENET_ALT_URL = f"{BATTLENET_REGION}.battle.net"

# Slug name for AR Club
GUILD_NAME = "ar-club"

# Slug name for AR Club's realm, Shandris
GUILD_REALM = "shandris"

BATTLENET_OAUTH_URL = "https://oauth.battle.net"

BATTLENET_OAUTH_AUTHORIZE_URI = f"{BATTLENET_OAUTH_URL}/authorize"

BATTLENET_OAUTH_TOKEN_URI = f"{BATTLENET_OAUTH_URL}/token"

BATTLENET_OAUTH_NAME = "battlenet"
