# pyright: reportOptionalMemberAccess=false


from authlib.integrations.starlette_client import OAuthError
from fastapi import Request, Response
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from isabot.api.discord import register
from isabot.battlenet.account import *
from isabot.battlenet.oauth import oauth
from isabot.battlenet.store import (
    store_access_token,
    store_bnet_userinfo,
    store_wow_accounts,
)
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
    try:
        # technically not a dictionary since it's
        # a class 'authlib.oauth2.rfc6749.wrappers.OAuth2Token', but
        # it can be accessed like a dictionary
        token: dict = await oauth.battlenet.authorize_access_token(request)
    except OAuthError as error:
        print("error", error.error)
        return Response("Internal server error.", 500)
    except Exception as error:
        print("error", error)
        return Response("Internal server error.", 500)

    # Get access token in a DB, request the necessary
    # information for the user using the token, and store all
    # of the in a DB
    try:
        store_access_token("authorization_flow_tokens", token)
        # token_literal = token.get("access_token", "")

        # Request the information first before storing them in the DB
        # userinfo = await account_user_info(token_literal)
        # profile_summary = await account_profile_summary(token_literal)
        # wow_accounts = profile_summary.get("wow_accounts", [])
        # wow_chars = await account_characters(wow_accounts)

        # user_ref = store_bnet_userinfo(userinfo)
        # store_wow_accounts(user_ref.id, {"characters": wow_chars})

    except Exception as error:
        print("error", error)
        return Response("Internal server error.", 500)
    return Response("Success! You may return to Discord.")


def get_discord_invite_url(app_id: str) -> str:
    return f"https://discord.com/api/oauth2/authorize?client_id={app_id}&scope=applications.commands"
