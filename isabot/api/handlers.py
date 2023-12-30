# pyright: reportOptionalMemberAccess=false


import traceback

from authlib.integrations.starlette_client import OAuthError
from fastapi import Request, Response
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

import isabot.battlenet.account as account
import isabot.battlenet.guild as guild
import isabot.battlenet.oauth as auth
import isabot.battlenet.pvp as pvp
import isabot.battlenet.store as store
import isabot.discord.commands as commands
from isabot.api.discord import register
from isabot.api.discord.base import BASE
from isabot.battlenet.constants import GUILD_NAME, GUILD_REALM
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

        cc_token = await auth.cc_get_access_token()
        cc_access_token = cc_token["access_token"]

        user_id = userinfo["sub"]

        g = await guild.get_guild_roster(
            cc_access_token, GUILD_NAME, GUILD_REALM[0], "profile"
        )
        guild_members = g["members"]

        # Request the information first before storing them in the DB
        profile_summary = await account.account_profile_summary(af_access_token)

        # Get characters that are only in the guild
        wow_accounts = profile_summary.get("wow_accounts", [])
        wow_chars = await account.account_characters(
            wow_accounts, characters_in_guild=True
        )
        wow_chars_in_guild = get_characters_in_guild(wow_chars, guild_members)

        # Get mounts and PvP data
        pvp_data = await get_pvp_data_from_chars(
            wow_chars_in_guild, cc_access_token, user_id
        )
        account_mounts = await account.account_mounts_collection(af_access_token)
        len_mounts = len(account_mounts["mounts"])

        # return _JSONResponse(pvp_data)

        # Store all data in DB
        store.store_bnet_userinfo(userinfo)
        store.store_access_token("authorization_flow_tokens", af_token)
        store.store_wow_accounts(user_id, {"characters": wow_chars_in_guild})
        store.store_len_mounts(user_id, len_mounts)
        store.store_pvp_data(user_id, pvp_data)
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


def get_discord_invite_url(app_id: str) -> str:
    return f"https://discord.com/api/oauth2/authorize?client_id={app_id}&scope=applications.commands"


def get_characters_in_guild(
    characters: list[dict], guild_roster: list[dict]
) -> list[dict]:
    return [
        c for c in characters for g in guild_roster if c["id"] == g["character"]["id"]
    ]


async def get_pvp_data_from_chars(
    wow_chars_in_guild: list[dict], cc_access_token: str, user_id: str
) -> dict[str, int]:
    """Get total wins and loses from each character's battleground statistics"""
    account_pvp_data = {"user_id": user_id, "total_won": 0, "total_lost": 0}
    for char in wow_chars_in_guild:
        char_pvp_stats = {"char_total_won": 0, "char_total_lost": 0}
        char_pvp_data = await pvp.get_pvp_summary(
            char["name"], cc_access_token, char["realm"]["slug"]
        )
        for battleground in char_pvp_data.get("pvp_map_statistics", []):
            match_stats = battleground.get("match_statistics")
            if not match_stats:
                continue
            won, lost = match_stats.get("won"), match_stats.get("lost")
            char_pvp_stats["char_total_won"] += won
            char_pvp_stats["char_total_lost"] += lost
        account_pvp_data["total_won"] += char_pvp_stats.get("char_total_won", 0)
        account_pvp_data["total_lost"] += char_pvp_stats.get("char_total_lost", 0)
    return account_pvp_data
