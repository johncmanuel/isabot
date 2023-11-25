from fastapi import Request

from env import DISCORD_PUBLIC_KEY
from isabot.discord import verify


async def handle_discord_app(req: Request):
    if not DISCORD_PUBLIC_KEY:
        raise Exception("Public key for discord not given")
    v = await verify.verify_request(req, DISCORD_PUBLIC_KEY)
    body, error = v["body"], v["error"]
    if error:
        return error
