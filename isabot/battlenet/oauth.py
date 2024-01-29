# Ongoing issue with the authlib's typings
# https://github.com/lepture/authlib/issues/527
# It's probably best to turn off type checkers to avoid errors
# pyright: reportOptionalMemberAccess=false

import asyncio
from datetime import datetime, timedelta
from typing import Union

from aiohttp import BasicAuth
from authlib.integrations.starlette_client import OAuth
from fastapi import Request
from starlette.datastructures import URL

import isabot.battlenet.store as store
from env import BATTLENET_CLIENT_ID, BATTLENET_CLIENT_SECRET
from isabot.battlenet.constants import (
    BATTLENET_OAUTH_AUTHORIZE_URI,
    BATTLENET_OAUTH_NAME,
    BATTLENET_OAUTH_TOKEN_URI,
    BATTLENET_OAUTH_URL,
    BATTLENET_URL,
)
from isabot.utils.client import http_client

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
    """Redirects users to the Battle Net OAuth server to login."""
    return await oauth.battlenet.authorize_redirect(request, url)


async def cc_handler(url: str, client_id: str, client_secret: str):
    """Get OAuth client credentials"""
    r = await http_client.post(
        url=url,
        auth=BasicAuth(client_id, client_secret),
        data={
            "grant_type": "client_credentials",
        },
    )
    return await r.json()


async def cc_get_access_token(
    collection_path: str = "client_credentials_token",
):
    """
    Retrieves client credentials access token from the DB if it's not expired yet or it exists. Else,
    request a new one and store it in DB. If the request(s) to retrieve a new token fails, raise an Exception.
    """
    token = await store.get_first_doc_in_collection(collection_path)

    if token and not is_access_token_expired(token):
        return token

    token = None

    max_retries = 2
    num_retries = 0
    while not token and max_retries > num_retries:
        try:
            token = await cc_handler(
                BATTLENET_OAUTH_TOKEN_URI,
                BATTLENET_CLIENT_ID,
                BATTLENET_CLIENT_SECRET,
            )
        except Exception:
            num_retries += 1
            await asyncio.sleep(1)

    if not token:
        raise Exception("client_credentials token not retrieved")

    token["expires_at"] = get_expiration_date(token["expires_in"])

    await store.store_cc_access_token(collection_name=token["sub"], token=token)

    return token


# Timezone might be affecting the time calculations for checking expiration dates.
# It would be better to use the computer clock instead.


def is_access_token_expired(token: dict) -> bool:
    return token["expires_at"] <= datetime.now().timestamp()


def get_expiration_date(seconds: int) -> float:
    return (datetime.now() + timedelta(seconds=seconds)).timestamp()
