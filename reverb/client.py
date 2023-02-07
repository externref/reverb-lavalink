from __future__ import annotations

import typing

import aiohttp
import attrs
import hikari

from reverb.gateway import GatewayHandler


@attrs.define(kw_only=True, slots=True)
class LavalinkClient:
    host: str
    port: int
    password: str = "youshallnotpass"
    application_id: int
    bot: hikari.UndefinedOr[hikari.GatewayBot]
    _gateway: hikari.UndefinedOr[GatewayHandler] = attrs.field(init=False, default=hikari.UNDEFINED)
    _client_session: hikari.UndefinedOr[aiohttp.ClientSession] = attrs.field(init=False, default=hikari.UNDEFINED)

    @property
    def client_session(self) -> aiohttp.ClientSession:
        assert isinstance(
            self._client_session, aiohttp.ClientSession
        ), "LavalinkClient class shall be initialised using the `build` classmethod,"
        return self._client_session

    @property
    def gateway(self) -> GatewayHandler:
        assert isinstance(
            self._gateway, GatewayHandler
        ), "you need to login using .start() using before accessing the gateway"
        return self._gateway

    @classmethod
    async def build(
        cls,
        *,
        host: str,
        port: typing.SupportsInt,
        password: str = "youshallnotpass",
        application_id: int,
        bot: hikari.UndefinedOr[hikari.GatewayBot] = hikari.UNDEFINED,
        client_session: hikari.UndefinedOr[aiohttp.ClientSession] = hikari.UNDEFINED,
    ) -> LavalinkClient:
        inst = cls(
            host=host if host.startswith("http") else f"http://{host}",
            port=int(port),
            password=password,
            application_id=application_id,
            bot=bot,
        )

        inst._client_session = (
            client_session if isinstance(client_session, aiohttp.ClientSession) else aiohttp.ClientSession()
        )
        inst._gateway = GatewayHandler(client=inst, client_session=inst.client_session)
        await inst.gateway.connect()
        return inst
