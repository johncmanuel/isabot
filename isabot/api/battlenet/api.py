# Ongoing issue with the authlib's typings
# https://github.com/lepture/authlib/issues/527
# It's probably best to turn off type checkers to avoid errors
# pyright: reportOptionalMemberAccess=false

from authlib.integrations.starlette_client import OAuthError
from fastapi import APIRouter, Request, Response
from starlette.responses import HTMLResponse

from isabot.battlenet.auth import oauth

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
    return Response("Success!")
