from isabot.utils.client import http_client


async def run_webhook(url: str, data: dict):
    """https://discord.com/developers/docs/resources/webhook#execute-webhook"""
    return await http_client.post(
        url=url,
        headers={
            "Content-Type": "application/json",
        },
        json=data,
    )
