from json import dumps
from urllib.parse import ParseResult, parse_qsl, unquote, urlencode, urlparse

from aiohttp import ClientSession

from isabot.battlenet.constants import BATTLENET_NAMESPACES


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


def get_namespace(region: str):
    return BATTLENET_NAMESPACES.get(region, None)


async def get_bnet_endpt(url: str, token: str, namespace: str, params: dict[str, str]):
    url = add_query_params(url, params)
    async with ClientSession() as session:
        async with session.get(
            url=url,
            headers={
                "Content-Type": "application/json",
                "Authorization": get_bnet_authorization_header(token),
                "Battlenet-Namespace": namespace,
            },
        ) as response:
            if not response.ok:
                raise Exception(f"Failed to fetch endpoint: {url}")
            return await response.json()
