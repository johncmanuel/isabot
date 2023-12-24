from json import dumps
from urllib.parse import ParseResult, parse_qsl, unquote, urlencode, urlparse

from aiohttp import ClientSession

from isabot.battlenet.constants import (
    BATTLENET_LOCALE,
    BATTLENET_NAMESPACES,
    BATTLENET_URL,
)


def add_query_params(url: str, params: dict[str, str]) -> str:
    """https://stackoverflow.com/a/25580545"""

    parsed_url = urlparse(unquote(url))

    # Converting and updating URL arguments
    parsed_get_args = dict(parse_qsl(parsed_url.query))
    parsed_get_args.update(params)

    # Ensure that boolean and dictionary values are json-friendly
    parsed_get_args.update(
        {k: dumps(v) for k, v in parsed_get_args.items() if isinstance(v, (bool, dict))}
    )

    # Converting URL argument to proper query string
    encoded_get_args = urlencode(parsed_get_args, doseq=True)

    return ParseResult(
        parsed_url.scheme,
        parsed_url.netloc,
        parsed_url.path,
        parsed_url.params,
        encoded_get_args,
        parsed_url.fragment,
    ).geturl()


def get_bnet_authorization_header(token: str) -> str:
    return token if token.startswith("Bearer ") else f"Bearer {token}"


def get_namespace(namespace_type: str):
    return BATTLENET_NAMESPACES.get(namespace_type.lower(), None)


async def get_bnet_endpt(
    url: str,
    token: str,
    namespace: str = "static",
    base_url: str = BATTLENET_URL,
):
    """
    Gets data from a protected endpoint. Note that `url` will
    append the base url for you, so pass the relative path

    `await get_bnet_endpt(url="/profile/user/wow", ...)`
    """
    url = add_query_params(f"{base_url}{url}", {"locale": BATTLENET_LOCALE})
    async with ClientSession() as session:
        async with session.get(
            url=url,
            headers={
                "Authorization": get_bnet_authorization_header(token),
                "Battlenet-Namespace": get_namespace(namespace),
            },
        ) as response:
            if not response.ok:
                raise Exception(
                    f"Failed to fetch endpoint: {url} | {await response.text()}"
                )
            return await response.json()
