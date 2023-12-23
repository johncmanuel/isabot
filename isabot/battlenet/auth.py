# from urllib.parse import quote

# from aiohttp import ClientSession
from authlib.integrations.starlette_client import OAuth

from env import BATTLENET_CLIENT_ID, BATTLENET_CLIENT_SECRET
from isabot.battlenet.constants import (
    BATTLENET_OAUTH_AUTHORIZE_URI,
    BATTLENET_OAUTH_NAME,
    BATTLENET_OAUTH_TOKEN_URI,
    BATTLENET_OAUTH_URL,
    BATTLENET_URL,
)

oauth = OAuth()
oauth.register(
    name=BATTLENET_OAUTH_NAME,
    client_secret=BATTLENET_CLIENT_SECRET,
    client_id=BATTLENET_CLIENT_ID,
    server_metadata_url=f"{BATTLENET_OAUTH_URL}/oauth/.well-known/openid-configuration",
    authorize_url=BATTLENET_OAUTH_AUTHORIZE_URI,
    authorize_token_params={
        "response_type": "code",
    },
    access_token_url=BATTLENET_OAUTH_TOKEN_URI,
    access_token_params={
        "grant_type": "authorization_code",
    },
    api_base_url=BATTLENET_URL,
    client_kwargs={"scope": "offline_access wow.profile"},
)
