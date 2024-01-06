# pyright: reportOptionalMemberAccess=false

from fastapi import APIRouter, BackgroundTasks, Request
from fastapi.responses import RedirectResponse

import isabot.api.handlers as handlers
import isabot.api.leaderboards.leaderboard as leaderboard
import isabot.api.leaderboards.update as update
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


@router.get("/webhook")
async def manual_webhook(background_tasks: BackgroundTasks):
    # t = (await oauth.cc_get_access_token())["access_token"]
    # l = leaderboard.Leaderboard(t)
    # b = await l.get_normal_bg_stats()
    # m = await l.get_mounts()
    # g = await l.get_users()
    # entry = l.create_entry(g, m, b)
    # await l.upload_entry(entry)

    # return {"details": "updating the database now..."}
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


@router.get("/health")
async def test():
    """https://byjos.dev/cloud-run-hot-service/"""
    return {"hi": "welcome"}


@router.get("/update")
async def update_leaderboard(request: Request, background_tasks: BackgroundTasks):
    """https://stackoverflow.com/questions/53181297/verify-http-request-from-google-cloud-scheduler"""
    return await handlers.handle_update_leaderboard(request, background_tasks)
