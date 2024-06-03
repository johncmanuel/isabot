# pyright: reportOptionalMemberAccess=false

# TODO: clean up imports using __init__.py files
import asyncio
import traceback
from datetime import datetime

from authlib.integrations.starlette_client import OAuthError
from fastapi import BackgroundTasks, Request, Response
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

import isabot.battlenet.endpoints as endpoints
import isabot.battlenet.oauth as auth
import isabot.battlenet.store as store
import isabot.utils.dictionary as dictionary
from env import CURRENT_ENV, GOOGLE_SERVICE_ACCOUNT

# import isabot.api.leaderboards.update as update
from isabot.api.background_tasks import update_db_and_upload_entry
from isabot.api.discord import register
from isabot.api.discord.base import BASE
from isabot.battlenet.constants import GUILD_REALM
from isabot.discord.discord_types import (
    APIInteractionResponseFlags,
    APIInteractionResponseType,
    APIInteractionType,
    ApplicationCommandOptionType,
)
from isabot.discord.verify import verify_request
from isabot.utils.client import http_client

# import isabot.discord.commands as commands


def _JSONResponse(data: dict) -> JSONResponse:
    return JSONResponse(content=jsonable_encoder(data))


async def handle_register_cmd(login_url: str) -> JSONResponse:
    return _JSONResponse(
        {
            "type": APIInteractionResponseType.ChannelMessageWithSource,
            "data": {
                "content": f"Click the link to register: {login_url}",
                "flags": APIInteractionResponseFlags.Ephemeral,
            },
        }
    )


async def handle_setup() -> None:
    # TODO: Register commands only if new commands were added or current commands
    # were updated

    # existing_commands = await commands.get_existing_commands()
    # registered_commands = [BASE]
    # await commands.register_slash_command(BASE)

    # print(existing_commands)
    # await commands.bulk_overwrite_commands(
    #     DISCORD_APP_ID, DISCORD_TOKEN, registered_commands
    # )
    # print("Print additional setup logs here")
    pass


async def handle_discord_app(
    request: Request, discord_public_key: str, url: str
) -> Response:
    """
    Handle incoming requests from Discord
    https://discord.com/developers/docs/interactions/receiving-and-responding#interaction-object
    """
    v = await verify_request(request, discord_public_key)
    body, error = v["body"], v["error"]

    if error:
        return error

    interactionType: APIInteractionType = body["type"]

    if interactionType == APIInteractionType.Ping:
        return _JSONResponse({"type": APIInteractionResponseType.Pong})

    if interactionType != APIInteractionType.ApplicationCommand:
        return Response("Invalid request.", 400)
    if not body["member"]:
        return Response("Invalid request.", 400)
    if not body["member"]["user"]:
        return Response("Invalid request.", 400)
    if not body["data"]["options"] or len(body["data"]["options"]) == 0:
        return Response("Invalid request.", 400)

    o = body["data"]["options"][0]
    name, cmd_type = o["name"], o["type"]

    if cmd_type != ApplicationCommandOptionType.SubCommand:
        return Response("Invalid request.", 400)

    if name == register.REGISTER_NAME:
        register_res = await handle_register_cmd(url)
        return register_res

    return Response("Invalid request.", 400)


async def handle_auth(request: Request) -> Response:
    """
    Handles authentication after the user has entered their credentials
    via Battle Net OAuth.
    """
    user = request.session.get("user")
    if user:
        return Response(
            f"You're already logged in! Log out at {request.url_for('logout')}"
        )

    try:
        # technically not a dictionary since it's
        # a class 'authlib.oauth2.rfc6749.wrappers.OAuth2Token', but
        # it can be accessed like a dictionary
        token: dict = await auth.oauth.battlenet.authorize_access_token(request)
    except OAuthError as error:
        print("error", error.error)
        return Response("Internal server error.", 500)
    except Exception as error:
        print("error", error)
        return Response("Internal server error.", 500)

    af_token = token.get("access_token")
    if not af_token:
        print("error, couldn't fetch authorization_flow token")
        return Response("Internal server error", 500)

    userinfo = await endpoints.account_user_info(af_token)
    if not userinfo:
        print("error, couldn't fetch user info for account")
        return Response("Internal server error", 500)

    return await handle_bnet_wow_data(request, af_token=token, userinfo=userinfo)


async def handle_bnet_wow_data(
    request: Request, af_token: dict, userinfo: dict
) -> Response:
    """
    Get access token in a DB, request the necessary
    information for the user using the token, and store them in a DB.

    Note that using the user's access token obtained via OAuth authorization
    code flow will only be utilized once. Once stored in DB, the token
    will be reused for the leaderboards until it's expired. This will
    require the user to login again in order to refresh it.

    Thus, the data fetching cannot be entirely automated which is not desired.
    In order to work around this, the data can be automatically
    updated by individually querying each character in the leaderboard
    using client credentials and different endpoints via cron jobs.
    """
    try:
        af_access_token = af_token["access_token"]

        cc_token = await auth.cc_get_access_token()  # type: ignore
        cc_access_token = cc_token["access_token"]

        user_id = userinfo["sub"]

        # Request the information first before storing them in the DB
        profile_summary = await endpoints.account_profile_summary(af_access_token)
        if not profile_summary:
            raise

        guild_roster = await guild.get_guild_roster(cc_access_token)  # type: ignore
        guild_members = []
        if guild_roster:
            guild_members = guild_roster.get("members", [])

        # Get characters that are only in the guild. Characters in the guild will be used
        # for calculating PvP data. The rest of the characters will be stored
        # in the database and be used for updating other data (i.e. number of mounts).
        wow_chars = await endpoints.account_characters(
            profile_summary.get("wow_accounts", {})
        )
        wow_chars_in_guild_realm = {
            k: v
            for k, v in wow_chars.items()
            if dictionary.safe_nested_get(v, "realm", "slug", default="N/A")
            in GUILD_REALM
        }
        wow_chars_in_guild = endpoints.get_characters_in_guild(
            wow_chars_in_guild_realm, guild_members
        )

        # Get mounts and PvP data
        normal_bg_data, account_mounts = await asyncio.gather(
            endpoints.get_normal_bg_data_from_chars(
                wow_chars_in_guild, cc_access_token, user_id
            ),
            endpoints.account_mounts_collection(af_access_token),
            # pvp.pvp_bracket_data(wow_chars_in_guild, cc_access_token, user_id),
        )

        len_mounts = 0
        if account_mounts:
            len_mounts = len(account_mounts.get("mounts", []))

        # Store all data in DB
        await asyncio.gather(
            store.store_bnet_userinfo(userinfo),
            store.store_access_token("authorization_flow_tokens", af_token),
            store.store_wow_chars(user_id, wow_chars),
            store.store_len_mounts(user_id, len_mounts),
            store.store_pvp_data(user_id, normal_bg_data),
        )

        # Store session
        request.session["user"] = dict(userinfo)

    except Exception as error:
        print("error", error)
        print(traceback.format_exc())

        # Reset login state after error
        request.session.pop("user", None)

        return Response("Internal server error.", 500)
    return Response("Success! You may return to Discord.")


async def handle_logout(request: Request):
    """Remove the user's session"""
    popped_user: dict = request.session.pop("user", None)
    # deleted_token = store.delete_access_token(popped_user["sub"])
    # if not popped_user and deleted_token:
    if not popped_user:
        return Response("You're not logged in, get outta here!")
    return Response("Successfully logged out!")


async def handle_update_leaderboard(
    request: Request, background_tasks: BackgroundTasks
):
    """
    Updates relevant data on the DB. Verifies if the request is from Google Cloud Scheduler.
    https://stackoverflow.com/questions/53181297/verify-http-request-from-google-cloud-scheduler
    """
    # Verify the request if the application is in production
    if CURRENT_ENV == "production":
        try:
            await verify_update_request(request)
        except Exception:
            return Response("Invalid request", 400)

    try:
        cc_access_token = await auth.cc_get_access_token()
        if not cc_access_token:
            raise
    except Exception:
        return Response("Internal server error.", 500)

    cc_access_token = cc_access_token.get("access_token")
    if not cc_access_token:
        return Response("Internal server error.", 500)

    background_tasks.add_task(
        update_db_and_upload_entry, cc_access_token, str(request.url_for("auth"))
    )

    return Response("Received", 202)


async def verify_update_request(request: Request):
    """Verify if the request is from Google Cloud Scheduler"""
    try:
        id_token = request.headers.get("Authorization").replace("Bearer", "").strip()
    except Exception:
        raise Exception

    decoded = await decode_id_token(id_token)

    if not decoded:
        raise Exception

    if not is_valid_token(decoded):
        raise Exception


async def decode_id_token(id_token: str):
    """Decodes the ID token issued by Google Cloud Scheduler"""
    try:
        r = await http_client.get(
            url=f"https://oauth2.googleapis.com/tokeninfo?id_token={id_token}"
        )
        return await r.json()
    except Exception:
        return None


def is_valid_token(token: dict, expected_email: str = GOOGLE_SERVICE_ACCOUNT):
    expired, email = token.get("exp"), token.get("email")
    if not expired:
        return False
    if int(expired) < datetime.now().timestamp():
        return False
    if not email:
        return False
    if expected_email != email:
        return False
    return True


def get_discord_invite_url(app_id: str) -> str:
    return f"https://discord.com/api/oauth2/authorize?client_id={app_id}&scope=applications.commands"
