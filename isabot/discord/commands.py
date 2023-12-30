from aiohttp import ClientSession

from env import DISCORD_APP_ID, DISCORD_TOKEN
from isabot.discord.constants import DISCORD_API_URL


def get_register_command_url(app_id: str, base: str = DISCORD_API_URL) -> str:
    return f"{base}/applications/{app_id}/commands"


def get_global_app_cmd_url(app_id: str, cmd_id: str, base: str = DISCORD_API_URL):
    return f"{get_register_command_url(app_id, base)}{cmd_id}"


def get_bot_authorization_header(token: str) -> str:
    return token if token.startswith("Bot ") else f"Bot {token}"


"""TODO: create a session wrapper to reduce code duplication for aiohttp's client session"""


async def register_slash_command(
    data: dict, token: str = DISCORD_TOKEN, app_id: str = DISCORD_APP_ID
) -> None:
    """https://discord.com/developers/docs/interactions/application-commands#registering-a-command"""
    async with ClientSession() as session:
        async with session.post(
            url=get_register_command_url(app_id),
            headers={
                "Content-Type": "application/json",
                "Authorization": get_bot_authorization_header(token),
            },
            # json=data.model_dump(),
            json=data,
        ) as response:
            if not response.ok:
                raise Exception(
                    f"Failed to register command: {response.status} {await response.text()}"
                )
            print("Registering slash command...", response.status)
            return await response.json()


async def get_existing_commands(
    app_id: str = DISCORD_APP_ID, token: str = DISCORD_TOKEN
):
    """https://discord.com/developers/docs/interactions/application-commands#get-global-application-commands"""
    async with ClientSession() as session:
        async with session.get(
            url=get_register_command_url(app_id),
            headers={
                "Authorization": get_bot_authorization_header(token),
                "Content-Type": "application/json",
            },
        ) as response:
            if not response.ok:
                raise Exception(
                    f"Failed to fetch global commands: {response.status} {await response.text()}"
                )
            return await response.json()


async def bulk_overwrite_commands(
    commands: list[dict],
    app_id: str = DISCORD_APP_ID,
    token: str = DISCORD_TOKEN,
) -> None:
    """https://discord.com/developers/docs/interactions/application-commands#bulk-overwrite-global-application-commands"""
    async with ClientSession() as session:
        async with session.put(
            url=get_register_command_url(app_id),
            headers={
                "Authorization": get_bot_authorization_header(token),
                "Content-Type": "application/json",
            },
            json=commands,
        ) as response:
            if not response.ok:
                raise Exception(
                    f"Failed to bulk overwrite commands: {response.status} {await response.text()}"
                )
            print("Overwriting commands...")
