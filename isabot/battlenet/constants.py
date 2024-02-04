from typing import Literal

# Region and locale to retrieve Battle Net data from.
# https://develop.battle.net/documentation/guides/regionality-and-apis
BATTLENET_REGION = "us"
BATTLENET_LOCALE = "en_US"

# Available options are: Static, Dynamic, and Profile
# More information here:
# https://develop.battle.net/documentation/world-of-warcraft/guides/namespaces
#
# Something to note: profile-related data are updated after a character logs out
BATTLENET_NAMESPACES = {
    "static": f"static-{BATTLENET_REGION}",
    "dynamic": f"dynamic-{BATTLENET_REGION}",
    "profile": f"profile-{BATTLENET_REGION}",
}

# Base URL for Battle Net API
BATTLENET_URL = f"https://{BATTLENET_REGION}.api.blizzard.com"

# Slug name for AR Club
GUILD_NAME = "ar-club"

# Slug name for AR Club's realm, Bronzebeard-Shandris
GUILD_REALM = ("shandris", "bronzebeard")

# Battle Net OAuth URL
BATTLENET_OAUTH_URL = "https://oauth.battle.net"

# Battle Net OAuth authorize and token URIs
BATTLENET_OAUTH_AUTHORIZE_URI = f"{BATTLENET_OAUTH_URL}/authorize"
BATTLENET_OAUTH_TOKEN_URI = f"{BATTLENET_OAUTH_URL}/token"

# Battle Net OAuth name
BATTLENET_OAUTH_NAME = "battlenet"

# WoW's supported PVP brackets
PVP_BRACKETS = Literal["2v2", "3v3", "rbg"]
