import asyncio
from typing import Any, Optional

import aiohttp


class HttpClient:
    """
    Create a reuseable session, which is a very must need according to
    the aiohttp docs:
    https://docs.aiohttp.org/en/stable/client_quickstart.html#make-a-request

    Reference used when creating this class:
    https://github.com/tiangolo/fastapi/issues/236#issuecomment-716548461
    """

    session: Optional[aiohttp.ClientSession] = None

    async def start(self) -> None:
        self.session = aiohttp.ClientSession()

    async def stop(self) -> None:
        if self.session:
            await self.session.close()
            self.session = None

    def __call__(self) -> aiohttp.ClientSession:
        assert self.session is not None
        return self.session

    async def _request(
        self,
        url: str,
        method: str,
        max_retry_attempts: int = 3,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Perform an async HTTP request to a given endpoint. This will perform a limited amount of
        retries if errors occur. After multiple, failed retries, raise an Exception. Though, this does
        not retry for 404 errors.
        """
        attempts = 0
        while attempts < max_retry_attempts:
            res = await getattr(self.session, method.lower())(url, *args, **kwargs)
            if res.ok:
                return res
            attempts += 1
            if res.status == 404:
                # Don't retry for 404 errors
                raise Exception("Not found")
            print(
                f"failed to perform {method} request for:",
                url,
                "|",
                res.status,
                "| retrying...",
            )
            await asyncio.sleep(1.0)
        raise Exception("Couldn't make request to endpoint:", url)

    async def get(
        self, url: str, max_retry_attempts: int = 3, *args: Any, **kwargs: Any
    ) -> Any:
        """Perform a GET request."""
        return await self._request(url, "GET", max_retry_attempts, *args, **kwargs)

    async def post(
        self, url: str, max_retry_attempts: int = 3, *args: Any, **kwargs: Any
    ) -> Any:
        """Perform a POST request."""
        return await self._request(url, "POST", max_retry_attempts, *args, **kwargs)


http_client = HttpClient()
