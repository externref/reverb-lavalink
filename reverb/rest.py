from __future__ import annotations

import logging
import typing

import attrs
import multidict

if typing.TYPE_CHECKING:
    from reverb.client import LavalinkClient


@attrs.define
class Route:
    url: str
    client: LavalinkClient
    method: str = attrs.field(kw_only=True, default="GET")
    version: int = attrs.field(kw_only=True, default=3)
    data: dict[str, typing.Any] = attrs.field(kw_only=True, default={})

    @property
    def request_url(self) -> str:
        endpoint = "version" if self.url == "version" else f"v{self.version}/{self.url}"
        return f"{self.client.host}:{self.client.port}/{endpoint}"


@attrs.define(kw_only=True)
class RESTClient:
    client: LavalinkClient

    async def request(self, route: Route, json: bool = True) -> typing.Any:
        headers: dict[str, multidict.istr] = {"Authorization": multidict.istr(self.client.password)}
        res = await self.client.client_session.request(
            route.method, route.request_url, headers=headers, json=route.data
        )
        try:
            res.raise_for_status()
        except Exception as e:
            logging.error(e)
        return await res.json() if json is True else await res.content.read()

    async def get_version(self) -> str:
        data: bytes = await self.request(Route("version", self.client), json=False)
        return data.decode("utf-8")
