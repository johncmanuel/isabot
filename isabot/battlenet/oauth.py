from datetime import datetime, timedelta

from aiohttp import BasicAuth, ClientSession
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
    client_kwargs={"scope": "wow.profile"},
)


# Functions below are for the client credentials flow, not the authorization code flow


async def cc_handler(url: str, client_id: str, client_secret: str):
    async with ClientSession() as session:
        async with session.post(
            url=url,
            auth=BasicAuth(client_id, client_secret),
            data={
                "grant_type": "client_credentials",
            },
        ) as response:
            if not response.ok:
                raise Exception(
                    f"Failed to fetch endpoint: {url}, {response.status}, {await response.text()}"
                )
            return await response.json()


async def cc_get_access_token(url: str, client_id: str, client_secret: str):
    token: dict = await cc_handler(url, client_id, client_secret)

    expiration_date_seconds = token.get("expires_in", None)
    if not expiration_date_seconds:
        raise Exception("Token has no 'expires_in' key.")

    token["expires_in"] = (
        datetime.utcnow() + timedelta(seconds=expiration_date_seconds)
    ).timestamp()

    return token


async def cc_is_access_token_expired(token: dict):
    return token["expires_in"] < datetime.utcnow().timestamp()
    #     return await cc_get_access_token(url, client_id, client_secret)
    # return token