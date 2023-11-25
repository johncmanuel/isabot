from aiohttp import ClientSession


async def run_webhook(url: str, data: dict):
    async with ClientSession() as session:
        async with session.post(
            url=url,
            headers={
                "Content-Type": "application/json",
            },
            body=data,
        ) as r:
            return r
