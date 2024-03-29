from typing import Any

from fastapi import Request


def https_url_for(request: Request, name: str, **path_params: Any) -> str:
    """
    Replace HTTP with HTTPS in the URL generated by `request.url_for` if it exists and return it.
    Otherwise, return the URL as is.
    https://stackoverflow.com/a/70557220
    """
    http_url = str(request.url_for(name, **path_params))
    return http_url.replace("http", "https", 1) if "https" not in http_url else http_url
