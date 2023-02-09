from __future__ import annotations

import asyncio
import json
import logging
import typing

import aiohttp
import attrs
import hikari
import multidict

from reverb.enums import OPTypes
from reverb.events import (
    DiscordWebsocketClosedEvent,
    LavalinkReadyEvent,
    PlayerUpdateEvent,
    StatsEvent,
    TrackEndEvent,
    TrackExceptionEvent,
    TrackStartEvent,
    TrackStuckEvent,
    _EventOPEvent,
)
from reverb.models import (
    DiscordWebsocketClosedEventOP,
    PlayerUpdateOP,
    ReadyOP,
    StatsOP,
    TrackEndEventOP,
    TrackExceptionEventOP,
    TrackStartEventOP,
    TrackStuckEventOP,
    _EventOP,
)

if typing.TYPE_CHECKING:
    from reverb.client import LavalinkClient


TYPE_TO_EVENT_MAP: dict[str, type[_EventOP]] = {
    "TrackStartEvent": TrackStartEventOP,
    "TrackExceptionEvent": TrackExceptionEventOP,
    "TrackStuckEvent": TrackStartEventOP,
    "TrackEndEvent": TrackEndEventOP,
    "WebSocketClosedEvent": DiscordWebsocketClosedEventOP,
}

OP_TO_REVERB_EVENT_MAP: dict[type[_EventOP], type[_EventOPEvent]] = {
    TrackStartEventOP: TrackStartEvent,
    TrackExceptionEventOP: TrackExceptionEvent,
    TrackStuckEventOP: TrackStuckEvent,
    DiscordWebsocketClosedEventOP: DiscordWebsocketClosedEvent,
    TrackEndEventOP: TrackEndEvent,
}


@attrs.define(kw_only=True, slots=True)
class GatewayHandler:
    client: LavalinkClient
    client_session: aiohttp.ClientSession
    _websocket: hikari.UndefinedOr[aiohttp.ClientWebSocketResponse] = attrs.field(init=False, default=hikari.UNDEFINED)

    @property
    def gw_headers(self) -> dict[str, multidict.istr]:
        return {
            "Authorization": multidict.istr(self.client.password),
            "User-Id": multidict.istr(self.client.application_id),
            "Client-Name": multidict.istr("reverb/0.0.1a"),
        }

    @property
    def websocket(self) -> aiohttp.ClientWebSocketResponse:
        assert isinstance(
            self._websocket, aiohttp.ClientWebSocketResponse
        ), "gateway not connected to the lavalink server yet"
        return self._websocket

    async def process_events(self, payload: dict[str, typing.Any]) -> None:
        op = OPTypes(payload["op"])
        logging.debug("Recieved %s event from server", op)

        if not isinstance((bot := self.client.bot), hikari.GatewayBot):
            return
        if op is OPTypes.READY:
            bot.dispatch(LavalinkReadyEvent(app=bot, data=ReadyOP.create(payload)))
        elif op is OPTypes.PLAYER_UPDATE:
            bot.dispatch(PlayerUpdateEvent(app=bot, data=PlayerUpdateOP.create(payload)))
        elif op is OPTypes.STATS:
            bot.dispatch(StatsEvent(app=bot, data=StatsOP.create(payload)))
        elif op is OPTypes.EVENT:
            event_op_class = TYPE_TO_EVENT_MAP[payload["event"]]
            bot.dispatch(OP_TO_REVERB_EVENT_MAP[event_op_class](app=bot, data=event_op_class.create(payload)))

    async def _start_listening(self) -> None:
        async for message in self.websocket:
            if message.type is aiohttp.WSMsgType.TEXT:  # type: ignore
                await self.process_events(json.loads(message.data))  # type: ignore

    async def connect(self) -> None:
        self._websocket = await self.client_session.ws_connect(  # type: ignore
            f"{self.client.host}:{self.client.port}/v3/websocket", headers=self.gw_headers
        )
        asyncio.create_task(self._start_listening())
