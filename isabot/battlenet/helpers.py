from typing import Any, Union

from isabot.battlenet.constants import (
    BATTLENET_LOCALE,
    BATTLENET_NAMESPACES,
    BATTLENET_URL,
)
from isabot.utils.client import http_client


def get_bnet_authorization_header(token: str) -> str:
    return token if token.startswith("Bearer ") else f"Bearer {token}"


def get_namespace(namespace_type: str):
    return BATTLENET_NAMESPACES.get(namespace_type.lower(), None)


async def get_bnet_endpt(
    url: str,
    token: str,
    namespace: str = "static",
    base_url: str = BATTLENET_URL,
) -> Union[Any, None]:
    """
    Use GET to fetch a protected Battle Net endpoint. Note that `url` will
    append the base url for you, so pass the relative path

    `await get_bnet_endpt(url="/profile/user/wow", ...)`
    """
    try:
        r = await http_client.get(
            url=f"{base_url}{url}",
            headers={
                "Authorization": get_bnet_authorization_header(token),
                "Battlenet-Namespace": get_namespace(namespace),
            },
            params={"locale": BATTLENET_LOCALE},
        )
        return await r.json()
    except Exception as err:
        print("exception:", err)
        return None
