from fastapi import APIRouter, Request, Response

from env import DISCORD_PUBLIC_KEY
from isabot.discord.verify import verify_request

router = APIRouter()


@router.post("/setup")
async def setup(req: Request, res: Response):
    if not DISCORD_PUBLIC_KEY:
        return
    v = await verify_request(req, DISCORD_PUBLIC_KEY)
    body, error = v["body"], v["error"]
    if error:
        return error
    return body
