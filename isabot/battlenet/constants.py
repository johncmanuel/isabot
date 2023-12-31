import typing

BATTLENET_REGION = "us"

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

BATTLENET_LOCALE = "en_US"

BATTLENET_URL = f"https://{BATTLENET_REGION}.api.blizzard.com"

BATTLENET_ALT_URL = f"https://{BATTLENET_REGION}.battle.net"

# Slug name for AR Club
GUILD_NAME = "ar-club"

# Slug name for AR Club's realm, Bronzebeard-Shandris
GUILD_REALM = ("shandris", "bronzebeard")

BATTLENET_OAUTH_URL = "https://oauth.battle.net"

BATTLENET_OAUTH_AUTHORIZE_URI = f"{BATTLENET_OAUTH_URL}/authorize"

BATTLENET_OAUTH_TOKEN_URI = f"{BATTLENET_OAUTH_URL}/token"

BATTLENET_OAUTH_NAME = "battlenet"

PVP_BRACKETS = typing.Literal["2v2", "3v3", "rbg"]

# PVP_BRACKETS: typing.Tuple[PVP_BRACKETS_TYPE, ...] = typing.get_args(PVP_BRACKETS_TYPE)
