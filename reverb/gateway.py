from __future__ import annotations

import asyncio
import json
import logging
import typing

import aiohttp
import attrs
import hikari
import multidict

from reverb.enums import EventType, ExceptionSeverity, OPTypes, TrackEndReason
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
from reverb.models import CPU, FrameStats, Memory, PlayerState

if typing.TYPE_CHECKING:
    from reverb.client import LavalinkClient


@attrs.define(kw_only=True, frozen=True, slots=True, repr=True)
class ReadyOP:
    resumed: bool
    session_id: str

    @property
    def op(self) -> str:
        return "ready"

    @classmethod
    def create(cls, payload: dict[str, typing.Any]) -> ReadyOP:
        return cls(resumed=payload["resumed"], session_id=payload["sessionId"])


@attrs.define(kw_only=True, slots=True, frozen=True, repr=True)
class PlayerUpdateOP:
    guild_id: int = attrs.field(converter=int)
    state: PlayerState

    @property
    def op(self) -> str:
        return "playerUpdate"

    @classmethod
    def create(cls, payload: dict[str, typing.Any]) -> PlayerUpdateOP:
        return cls(guild_id=payload["guildId"], state=PlayerState(**payload["state"]))


@attrs.define(kw_only=True, slots=True, frozen=True, repr=True)
class StatsOP:
    players: int
    playing_players: int
    uptime: int
    memory: Memory
    cpu: CPU
    frame_stats: FrameStats | None

    @property
    def op(self) -> str:
        return "stats"

    @classmethod
    def create(cls, payload: dict[str, typing.Any]) -> StatsOP:
        cpu = CPU(
            cores=payload["cpu"]["cores"],
            system_load=payload["cpu"]["systemLoad"],
            lavalink_load=payload["cpu"]["lavalinkLoad"],
        )
        return cls(
            players=payload["players"],
            playing_players=payload["playingPlayers"],
            uptime=payload["uptime"],
            memory=Memory(**payload["memory"]),
            cpu=cpu,
            frame_stats=FrameStats(**payload["frameStats"]) if payload.get("frameStats") else None,
        )


@attrs.define(kw_only=True, slots=True, frozen=True, repr=True)
class _EventOP:
    guild_id: int
    type: EventType

    @classmethod
    def create(cls, payload: dict[str, typing.Any]) -> typing.Any:
        ...


@attrs.define(kw_only=True, slots=True, frozen=True, repr=True)
class TrackStartEventOP(_EventOP):
    encoded_track: str

    @classmethod
    def create(cls, payload: dict[str, typing.Any]) -> TrackStartEventOP:
        return cls(guild_id=int(payload["guildId"]), type=EventType.TRACK_START, encoded_track=payload["encodedTrack"])


@attrs.define(kw_only=True, slots=True, frozen=True, repr=True)
class TrackEndEventOP(_EventOP):
    encoded_track: str
    reason: TrackEndReason

    @classmethod
    def create(cls, payload: dict[str, typing.Any]) -> TrackEndEventOP:
        return cls(
            guild_id=int(payload["guildId"]),
            type=EventType.TRACK_END,
            encoded_track=payload["encodedTrack"],
            reason=TrackEndReason(payload["reason"]),
        )


@attrs.define(kw_only=True)
class TrackException:
    message: str | None
    cause: str
    severity: ExceptionSeverity

    @classmethod
    def create(cls, payload: dict[str, typing.Any]) -> TrackException:
        return cls(
            message=payload.get("message"), cause=payload["cause"], severity=ExceptionSeverity(payload["severity"])
        )


@attrs.define(kw_only=True, slots=True, frozen=True, repr=True)
class TrackExceptionEventOP(_EventOP):
    encoded_track: str
    exception: TrackException

    @classmethod
    def create(cls, payload: dict[str, typing.Any]) -> TrackExceptionEventOP:
        return cls(
            guild_id=payload["guildId"],
            type=EventType.TRACK_EXCEPTION_EVENT,
            encoded_track=payload["encodedTrack"],
            exception=TrackException.create(payload["exception"]),
        )


@attrs.define(kw_only=True, slots=True, frozen=True, repr=True)
class TrackStuckEventOP(_EventOP):
    encoded_track: str
    threshold_ms: int

    @classmethod
    def create(cls, payload: dict[str, typing.Any]) -> TrackStuckEventOP:
        return cls(
            guild_id=payload["guildId"],
            type=EventType.TRACK_STUCK_EVENT,
            encoded_track=payload["encodedTrack"],
            threshold_ms=payload["thresholdMs"],
        )


@attrs.define(kw_only=True, slots=True, frozen=True, repr=True)
class DiscordWebsocketClosedEventOP(_EventOP):
    code: int
    reason: str
    by_remote: bool

    @classmethod
    def create(cls, payload: dict[str, typing.Any]) -> DiscordWebsocketClosedEventOP:
        return cls(
            guild_id=payload["guildId"],
            type=EventType.WEBSOCKET_CLOSED_EVENT,
            code=payload["code"],
            reason=payload["reason"],
            by_remote=payload["byRmote"],
        )


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
