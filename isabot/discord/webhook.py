from aiohttp import ClientSession


async def run_webhook(url: str, data: dict):
    """https://discord.com/developers/docs/resources/webhook#execute-webhook"""
    async with ClientSession() as session:
        async with session.post(
            url=url,
            headers={
                "Content-Type": "application/json",
            },
            json=data,
        ) as r:
            return r
