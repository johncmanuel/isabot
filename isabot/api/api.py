from fastapi import APIRouter, Request, Response

from env import DISCORD_PUBLIC_KEY
from isabot.discord import verify

router = APIRouter()


@router.post("/")
async def create_discord_app(req: Request, res: Response):
    pass


@router.post("/webhook")
async def manual_webhook():
    pass


@router.post("/webhook/:token")
async def automated_webhook():
    pass


@router.post("/register")
async def register_cmds():
    pass
