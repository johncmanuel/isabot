# pyright: reportOptionalMemberAccess=false

from fastapi import APIRouter, BackgroundTasks, HTTPException, Request
from fastapi.responses import RedirectResponse
from google.cloud.firestore import AsyncQuery

import isabot.api.handlers as handlers
import isabot.battlenet.oauth as oauth
import isabot.battlenet.store as store
from env import DISCORD_APP_ID, DISCORD_PUBLIC_KEY

# from isabot.raider_io.mythic import get_character_info, get_overall_mythic_plus_score
from isabot.utils.url import https_url_for

router = APIRouter()


@router.post("/")
async def root(request: Request):
    """Handle interactions here"""
    interaction_res = await handlers.handle_discord_app(
        request, DISCORD_PUBLIC_KEY, str(request.url_for("login"))
    )
    return interaction_res


@router.get("/entries")
async def entries_all():
    """Return all entries of the leaderboard."""
    return await store.get_multiple_data("leaderboard")


@router.get("/entries/recent")
async def entries_latest():
    """Return the current entry of the leaderboard."""
    return await store.get_most_recent_doc(
        "leaderboard", "date_created", AsyncQuery.DESCENDING
    )


@router.get("/invite")
async def inv():
    """Redirects users to the Discord invite URL for the bot."""
    return RedirectResponse(handlers.get_discord_invite_url(DISCORD_APP_ID))


@router.get("/login")
async def login(request: Request):
    return await oauth.bnet_redirect_authorization(
        request, https_url_for(request, "auth")
    )


@router.get("/logout")
async def logout(request: Request):
    return await handlers.handle_logout(request)


@router.get("/auth")
async def auth(request: Request):
    return await handlers.handle_auth(request)


@router.get("/health")
async def health():
    """https://byjos.dev/cloud-run-hot-service/"""
    return {"hi": "welcome"}


@router.get("/update")
async def update_leaderboard(request: Request, background_tasks: BackgroundTasks):
    return await handlers.handle_update_leaderboard(request, background_tasks)


# @router.get("/test")
# async def testing():
#     k = await get_character_info(
#         "heektor", "shandris", "us", fields="mythic_plus_scores_by_season:current, gear"
#     )
#     s = get_overall_mythic_plus_score(k)  # type: ignore

#     print(s)
#     return {"test": "lol"}
