from isabot.utils.client import http_client


async def run_webhook(url: str, data: dict):
    """
    Execute a webhook in Discord.
    https://discord.com/developers/docs/resources/webhook#execute-webhook

    TODO: Create type for webhook data in discord_types.py
    """
    return await http_client.post(
        url=url,
        headers={
            "Content-Type": "application/json",
        },
        json=data,
    )
