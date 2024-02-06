from isabot.raider_io.constants import RAIDER_IO_URL
from isabot.utils.client import http_client

"""
Reference for calculating mythic plus scores:
https://support.raider.io/kb/frequently-asked-questions
"""


async def get_raider_io_endpt(
    url: str,
    base_url: str = RAIDER_IO_URL,
    **params,
):
    """
    Make a GET request to the Raider IO API.

    Example "url" values:
    - "/characters/profile"
    - "/periods"
    - "/guilds/profile"

    Supply additional query parameters using kwargs.
    """
    try:
        r = await http_client.get(
            url=f"{base_url}{url}",
            params=params,
            headers={"Accept": "application/json"},
        )
        return await r.json()
    except Exception as err:
        print("exception:", err)
        return None
