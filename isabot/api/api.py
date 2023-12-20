from fastapi import APIRouter, Request, Response
from fastapi.responses import RedirectResponse

from env import DISCORD_APP_ID, DISCORD_CHANNEL_ID, DISCORD_PUBLIC_KEY
from isabot.api.discord import invite
from isabot.api.handlers import handle_discord_app

router = APIRouter()


@router.post("/")
async def root(req: Request, res: Response):
    """Handle interactions here"""
    interaction_res = await handle_discord_app(
        req, DISCORD_PUBLIC_KEY, DISCORD_CHANNEL_ID
    )
    return interaction_res


@router.post("/webhook")
async def manual_webhook():
    pass


@router.post("/webhook/:token")
async def automated_webhook():
    pass


@router.post("/register")
async def register_cmds():
    pass


@router.get("/hi")
async def hi():
    return {"message": "hi there"}


@router.get("/invite")
async def inv():
    return RedirectResponse(invite.get_invite_url(DISCORD_APP_ID))
