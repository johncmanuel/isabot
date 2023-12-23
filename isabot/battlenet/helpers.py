import urllib.parse as urlparse
from urllib.parse import urlencode

from aiohttp import ClientSession

from isabot.battlenet.constants import BATTLENET_NAMESPACES


def add_query_params(url: str, params: dict[str, str]):
    """https://stackoverflow.com/questions/2506379/add-params-to-given-url-in-python"""
    pass


def get_bnet_authorization_header(token: str) -> str:
    return token if token.startswith("Bearer ") else f"Bearer {token}"


def get_namespace(region: str):
    return BATTLENET_NAMESPACES.get(region, None)


async def get_bnet_endpt(url: str, token: str, namespace: str, locale: str):
    async with ClientSession() as session:
        async with session.get(
            url=f"{url}?locale={locale}",
            headers={
                "Content-Type": "application/json",
                "Authorization": get_bnet_authorization_header(token),
                "Battlenet-Namespace": namespace,
            },
        ) as response:
            if not response.ok:
                raise Exception(f"Failed to fetch endpoint: {url}")
            return await response.json()
