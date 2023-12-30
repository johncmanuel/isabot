# pyright: reportOptionalMemberAccess=false

from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

import isabot.api.handlers as handlers
import isabot.battlenet.oauth as oauth
from env import DISCORD_APP_ID, DISCORD_CHANNEL_ID, DISCORD_PUBLIC_KEY

router = APIRouter()


@router.post("/")
async def root(request: Request):
    """Handle interactions here"""
    interaction_res = await handlers.handle_discord_app(
        request, DISCORD_PUBLIC_KEY, DISCORD_CHANNEL_ID, str(request.url_for("login"))
    )
    return interaction_res


@router.post("/webhook")
async def manual_webhook():
    pass


@router.post("/webhook/:token")
async def automated_webhook():
    pass


@router.get("/invite")
async def inv():
    return RedirectResponse(handlers.get_discord_invite_url(DISCORD_APP_ID))


@router.get("/login")
async def login(request: Request):
    return await oauth.bnet_redirect_authorization(request, request.url_for("auth"))


@router.get("/logout")
async def logout(request: Request):
    return await handlers.handle_logout(request)


@router.get("/auth")
async def auth(request: Request):
    return await handlers.handle_auth(request)


@router.get("/test")
async def test(request: Request):
    return {"message": "success"}
