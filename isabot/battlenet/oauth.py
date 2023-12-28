# Ongoing issue with the authlib's typings
# https://github.com/lepture/authlib/issues/527
# It's probably best to turn off type checkers to avoid errors
# pyright: reportOptionalMemberAccess=false

from datetime import datetime, timezone
from typing import Union

from aiohttp import BasicAuth, ClientSession
from authlib.integrations.starlette_client import OAuth
from fastapi import Request
from starlette.datastructures import URL

from env import BATTLENET_CLIENT_ID, BATTLENET_CLIENT_SECRET
from isabot.battlenet.constants import (
    BATTLENET_OAUTH_AUTHORIZE_URI,
    BATTLENET_OAUTH_NAME,
    BATTLENET_OAUTH_TOKEN_URI,
    BATTLENET_OAUTH_URL,
    BATTLENET_URL,
)
from isabot.battlenet.helpers import convert_to_utc_seconds
from isabot.battlenet.store import store_cc_access_token
from isabot.firebase.crud import get_first_doc_in_collection

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


async def bnet_redirect_authorization(request: Request, url: Union[URL, str]):
    return await oauth.battlenet.authorize_redirect(request, redirect_uri=url)


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


async def cc_get_access_token(
    collection_path: str = "client_credentials_token",
):
    token = get_first_doc_in_collection(collection_path)

    if token and not await is_access_token_expired(token):
        return token

    token = await cc_handler(
        BATTLENET_OAUTH_TOKEN_URI,
        BATTLENET_CLIENT_ID,
        BATTLENET_CLIENT_SECRET,
    )
    token["expires_at"] = convert_to_utc_seconds(token["expires_in"])

    store_cc_access_token(collection_name=token["sub"], token=token)

    return token


async def is_access_token_expired(token: dict) -> bool:
    return token["expires_at"] < datetime.now(timezone.utc).timestamp()
