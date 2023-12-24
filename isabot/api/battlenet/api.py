# Ongoing issue with the authlib's typings
# https://github.com/lepture/authlib/issues/527
# It's probably best to turn off type checkers to avoid errors
# pyright: reportOptionalMemberAccess=false

from authlib.integrations.starlette_client import OAuthError
from fastapi import APIRouter, Request, Response
from starlette.responses import HTMLResponse

from env import BATTLENET_CLIENT_ID, BATTLENET_CLIENT_SECRET
from isabot.battlenet.account import *
from isabot.battlenet.constants import BATTLENET_OAUTH_TOKEN_URI
from isabot.battlenet.oauth import cc_get_access_token, oauth

router = APIRouter()


@router.get("/login")
async def login(request: Request):
    redirect_uri = request.url_for("auth")
    return await oauth.battlenet.authorize_redirect(request, redirect_uri)


@router.get("/auth")
async def auth(request: Request):
    try:
        token = await oauth.battlenet.authorize_access_token(request)
    except OAuthError as error:
        return HTMLResponse(f"<h1>OAuthError: {error.error}</h1>")
    except Exception as error:
        return HTMLResponse(f"<h1>Exception: {error}</h1>")
    print(token)
    return Response("Success! You may return to Discord.")


# @router.get("/test")
# async def test(request: Request):
#     x = await account_mounts_collection()
#     return x
