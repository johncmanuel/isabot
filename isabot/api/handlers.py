import json

from fastapi import Request, Response

from isabot.api.discord import register
from isabot.discord import verify
from isabot.discord.discord_types import (
    APIInteractionResponseType,
    APIInteractionType,
    ApplicationCommandOptionType,
)


async def handle_register_cmd():
    return {
        "type": APIInteractionResponseType.ChannelMessageWithSource,
        "data": {"content": "it works"},
    }


async def handle_discord_app(
    req: Request, discord_public_key: str, discord_channel_id: str
) -> Response:
    """
    Handle incoming requests from Discord
    https://discord.com/developers/docs/interactions/receiving-and-responding#interaction-object
    """
    v = await verify.verify_request(req, discord_public_key)
    body, error = v["body"], v["error"]

    if error:
        return error

    interactionType: APIInteractionType = body["type"]

    if interactionType == APIInteractionType.Ping:
        return Response(
            content=json.dumps({"type": APIInteractionResponseType.Pong}, default=str),
            media_type="application/json",
        )

    # if interactionType != APIInteractionType.ApplicationCommand:
    #     return Response("Invalid request.", 400)
    # if body["channel_id"] != discord_channel_id:
    #     return Response("Invalid request.", 400)
    # if not body["member"]:
    #     return Response("Invalid request.", 400)
    # if not body["member"]["user"]:
    #     return Response("Invalid request.", 400)
    # if not body["data"]["options"] or len(body["data"]["options"]) == 0:
    #     return Response("Internal server error.", 500)

    # o = body["data"]["options"][0]
    # name, cmd_type = o["name"], o["type"]

    # if cmd_type != ApplicationCommandOptionType.SubCommand:
    #     return Response("Invalid request.", 400)

    # if name == register.REGISTER_NAME:
    #     register_res = handle_register_cmd()
    #     return Response(register_res)

    return Response("Invalid request.", 400)
