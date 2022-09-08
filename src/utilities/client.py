import asyncio
import re

import aiohttp
from async_timeout import timeout

from .. import __version__
from ..errors import APIException

URL_REGEX = re.compile(
    r"^(?:http|ftp)s?://"  # http:// or https://
    r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)"
    r"+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"
    r"localhost|"
    r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"
    r"(?::\d+)?"
    r"(?:/?|[/?]\S+)$",
    re.IGNORECASE,
)


class Client:
    """An aiohttp client to fetch data"""

    session: aiohttp.ClientSession | None = None

    @classmethod
    async def init(cls) -> None:
        session = aiohttp.ClientSession(headers={"User-Agent": f"Imagenery API / {__version__}"})

        cls.session = session

    @classmethod
    async def fetch_image(cls, url: str) -> bytes:
        if cls.session is None:
            await cls.init()

        assert cls.session is not None

        if re.match(URL_REGEX, url) is not None:
            try:
                async with timeout(10):
                    async with cls.session.get(url) as response:
                        if response.ok:
                            return await response.read()
                        else:
                            raise APIException(
                                detail="Server Couldn't Fetch The Provided Resource",
                                status_code=400,
                            )
            except asyncio.TimeoutError:
                raise APIException("Unable To Fetch Image Within Timeout", status_code=400)
        else:
            raise APIException(detail="Malformed Image URL", status_code=400)
