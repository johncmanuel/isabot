# pyright: reportOptionalMemberAccess=false


import asyncio
import traceback
from datetime import datetime, timezone

from aiohttp import ClientSession
from authlib.integrations.starlette_client import OAuthError
from fastapi import BackgroundTasks, Request, Response
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

import isabot.battlenet.account as account
import isabot.battlenet.guild as guild
import isabot.battlenet.oauth as auth
import isabot.battlenet.pvp as pvp
import isabot.battlenet.store as store
import isabot.discord.commands as commands
import isabot.utils.concurrency as concurrency
import isabot.utils.dictionary as dictionary
from env import GOOGLE_SERVICE_ACCOUNT
from isabot.api.discord import register
from isabot.api.discord.base import BASE
from isabot.battlenet.constants import GUILD_REALM
from isabot.discord import verify
from isabot.discord.discord_types import (
    APIInteractionResponseFlags,
    APIInteractionResponseType,
    APIInteractionType,
    ApplicationCommandOptionType,
)


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
    print("Print additional setup logs here")


async def handle_discord_app(
    request: Request, discord_public_key: str, discord_channel_id: str, url
) -> Response:
    """
    Handle incoming requests from Discord
    https://discord.com/developers/docs/interactions/receiving-and-responding#interaction-object
    """
    v = await verify.verify_request(request, discord_public_key)
    body, error = v["body"], v["error"]

    if error:
        return error

    interactionType: APIInteractionType = body["type"]

    if interactionType == APIInteractionType.Ping:
        return _JSONResponse({"type": APIInteractionResponseType.Pong})

    if interactionType != APIInteractionType.ApplicationCommand:
        return Response("Invalid request.", 400)
    if body["channel_id"] != discord_channel_id:
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
        return Response("Internal server error", 500)

    userinfo = await account.account_user_info(af_token)
    if not userinfo:
        return Response("Internal server error", 500)

    request.session["user"] = dict(userinfo)

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

        guild_members = (await guild.get_guild_roster(cc_access_token)).get(
            "members", []
        )

        # Request the information first before storing them in the DB
        profile_summary = await account.account_profile_summary(af_access_token)

        # Get characters that are only in the guild. Characters in the guild will be used
        # for calculating PvP data. The rest of the characters will be stored
        # in the database and be used for updating other data (i.e. number of mounts).
        wow_chars = await account.account_characters(
            profile_summary.get("wow_accounts", {})
        )
        wow_chars_in_guild_realm = {
            k: v
            for k, v in wow_chars.items()
            if dictionary.safe_nested_get(v, "realm", "slug", default="N/A")
            in GUILD_REALM
        }
        wow_chars_in_guild = get_characters_in_guild(
            wow_chars_in_guild_realm, guild_members
        )

        # Get mounts and PvP data
        normal_bg_data, account_mounts = await asyncio.gather(
            pvp.get_normal_bg_data_from_chars(
                wow_chars_in_guild, cc_access_token, user_id
            ),
            account.account_mounts_collection(af_access_token),
            # pvp.pvp_bracket_data(wow_chars_in_guild, cc_access_token, user_id),
        )

        len_mounts = len(account_mounts.get("mounts", []))

        # Store all data in DB
        concurrency.batch_parallel_run(
            [
                lambda: store.store_bnet_userinfo(userinfo),
                lambda: store.store_access_token("authorization_flow_tokens", af_token),
                lambda: store.store_wow_chars(user_id, wow_chars),
                lambda: store.store_len_mounts(user_id, len_mounts),
                lambda: store.store_pvp_data(user_id, normal_bg_data),
            ]
        )

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
    """https://stackoverflow.com/questions/53181297/verify-http-request-from-google-cloud-scheduler

    Will be testing Google Cloud services
    """
    try:
        id_token = request.headers.get("Authorization").replace("Bearer", "").strip()
    except Exception:
        return Response("Invalid request", 400)

    decoded = await decode_id_token(id_token)
    if not decoded:
        return Response("Invalid request", 400)

    if not is_valid_token(decoded):
        return Response("Invalid request", 400)

    # Update and send leaderboard data to Discord
    # background_tasks.add_task()

    return Response("Updating leaderboard now...", 202)


async def decode_id_token(id_token: str):
    async with ClientSession() as session:
        async with session.get(
            url=f"https://oauth2.googleapis.com/tokeninfo?id_token={id_token}"
        ) as response:
            if not response.ok:
                return None
            return await response.json()


def is_valid_token(token: dict, expected_email: str = GOOGLE_SERVICE_ACCOUNT):
    expired = token.get("exp")
    email = token.get("email")
    if not expired:
        return False
    if int(expired) < datetime.now(timezone.utc).timestamp():
        return False
    if not email:
        return False
    if expected_email != email:
        return False
    return True


def get_discord_invite_url(app_id: str) -> str:
    return f"https://discord.com/api/oauth2/authorize?client_id={app_id}&scope=applications.commands"


def get_characters_in_guild(characters: dict, guild_roster: list[dict]):
    return {
        k: v
        for k, v in characters.items()
        if k
        in map(
            lambda x: str(
                dictionary.safe_nested_get(x, "character", "id", default="N/A")
            ),
            guild_roster,
        )
    }
