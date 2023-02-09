from __future__ import annotations

import typing

import aiohttp
import attrs
import hikari

from reverb.gateway import GatewayHandler
from reverb.rest import RESTClient

if typing.TYPE_CHECKING:
    from reverb import models


@attrs.define(kw_only=True, slots=True)
class LavalinkClient:
    """The main client class.
    This object contains all the methods and properties related to lavalink usage.

    !!! note
        This class should be initialised using the `.build()` classmethod and not directly.

    ??? example
        ```py
        from __future__ import annotations

        import logging
        import os

        import hikari
        import reverb

        TOKEN = os.environ["DEV_TOKEN"]
        HOST = "127.0.0.0"
        PORT = 2333
        PASSWORD = "youshallnotpass"
        BOT_ID = 964195658468835358

        bot = hikari.GatewayBot(TOKEN, logs="DEBUG")
        lavalink: reverb.LavalinkClient


        @bot.listen()
        async def setup_lavalink(_: hikari.StartingEvent) -> None:
            global lavalink
            lavalink = await reverb.LavalinkClient.build(
                host=HOST, port=PORT, password=PASSWORD, application_id=BOT_ID, bot=bot
            )


        @bot.listen()
        async def lavalink_ready(event: reverb.LavalinkReadyEvent) -> None:
            logging.info(
                "connected to lavalink! Lavalink version: %s,  Session ID: %s", lavalink.server_version, event.data.session_id
            )


        bot.run()
        ```
    """

    host: str
    """Host of the Lavalink server."""
    port: int
    """Port of the lavalink server."""
    password: str = "youshallnotpass"
    """Password for connecting to the server."""
    application_id: int
    """ID of your bot application."""
    bot: hikari.UndefinedOr[hikari.GatewayBot]
    """Your hikari bot's instance, this is needed to dispatch the lavalink events."""
    _server_version: str | None = attrs.field(init=False, default=None)
    _rest: hikari.UndefinedOr[RESTClient] = attrs.field(init=False, default=hikari.UNDEFINED)
    _gateway: hikari.UndefinedOr[GatewayHandler] = attrs.field(init=False, default=hikari.UNDEFINED)
    _client_session: hikari.UndefinedOr[aiohttp.ClientSession] = attrs.field(init=False, default=hikari.UNDEFINED)

    @property
    def client_session(self) -> aiohttp.ClientSession:
        """The aiohttp ClientSession object was initiated with."""
        assert isinstance(
            self._client_session, aiohttp.ClientSession
        ), "LavalinkClient class shall be initialised using the `build` classmethod,"
        return self._client_session

    @property
    def gateway(self) -> GatewayHandler:
        """Gateway handler for the client."""
        assert isinstance(self._gateway, GatewayHandler)
        return self._gateway

    @property
    def rest(self) -> RESTClient:
        """
        Returns
        -------
            reverb.rest.RESTClient
            Rest handler for the client."""
        assert isinstance(
            self._rest, RESTClient
        ), "LavalinkClient class shall be initialised using the `build` classmethod,"
        return self._rest

    @property
    def server_version(self) -> str:
        """
        Returns
        -------
            str
            The version of lavalink server
        """
        assert isinstance(self._server_version, str)
        return self._server_version

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
        """Initialises a LavalinkClient class.

        Parameters
        ----------
        host: str
            The lavalink host address.
        port: int
            Port to connect to.
        password: str
            The password to be used while connecting to the server.
        application_id: int
            ID of the bot application being used.
        bot: hikari.UndefinedOr[hikari.GatewayBot]
            The hikari bot instance.
        client_session: aiohttp.ClientSession
            The custom clientsession class to use, if any.

        Returns
        -------
            reverb.client.LavalinkClient
            The lavalink client that was initialised.

        """
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
        inst._rest = RESTClient(client=inst)
        await inst.gateway.connect()
        inst._server_version = await inst.rest.get_version()
        return inst

    def get_info(self) -> typing.Awaitable[models.LavalinkServerInfo]:
        return self.rest.get_info()

    def get_version(self) -> typing.Awaitable[str]:
        return self.rest.get_version()

    def get_stats(self) -> typing.Awaitable[models.StatsOP]:
        return self.rest.get_stats()
