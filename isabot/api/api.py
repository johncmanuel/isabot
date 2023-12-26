# pyright: reportOptionalMemberAccess=false

from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from env import DISCORD_APP_ID, DISCORD_CHANNEL_ID, DISCORD_PUBLIC_KEY
from isabot.api.handlers import get_discord_invite_url, handle_auth, handle_discord_app
from isabot.battlenet.oauth import bnet_redirect_authorization

router = APIRouter()


@router.post("/")
async def root(request: Request):
    """Handle interactions here"""
    interaction_res = await handle_discord_app(
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
    return RedirectResponse(get_discord_invite_url(DISCORD_APP_ID))


@router.get("/login")
async def login(request: Request):
    return await bnet_redirect_authorization(request, request.url_for("auth"))


@router.get("/auth")
async def auth(request: Request):
    return await handle_auth(request)


@router.get("/test")
async def test(request: Request):
    return {"message": "success"}
