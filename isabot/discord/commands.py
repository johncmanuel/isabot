from aiohttp import ClientSession

from isabot.discord.constants import DISCORD_API_URL


def get_register_command_url(app_id: str, base: str = DISCORD_API_URL) -> str:
    return f"{base}/applications/{app_id}/commands"


def get_bot_authorization_header(token: str) -> str:
    return token if token.startswith("Bot ") else f"Bot {token}"


async def register_slash_command(data: dict, token: str, app_id: str) -> None:
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
                print("something went wrong", await response.text())
                raise Exception(
                    f"Failed to register command: {response.status} {response.text}"
                )
            print(response.status, await response.json())