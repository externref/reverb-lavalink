from __future__ import annotations

import typing

import attrs
import hikari

if typing.TYPE_CHECKING:
    from reverb.gateway import (
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


@attrs.define(kw_only=True, frozen=True)
class ReverbEvent(hikari.Event):
    app: hikari.GatewayBot  # type: ignore


@attrs.define(kw_only=True, frozen=True)
class LavalinkReadyEvent(ReverbEvent):
    data: ReadyOP


@attrs.define(kw_only=True, frozen=True)
class StatsEvent(ReverbEvent):
    data: StatsOP


@attrs.define(kw_only=True, frozen=True)
class PlayerUpdateEvent(ReverbEvent):
    data: PlayerUpdateOP


@attrs.define(kw_only=True, frozen=True)
class _EventOPEvent(ReverbEvent):
    data: _EventOP


@attrs.define(kw_only=True, frozen=True)
class TrackStartEvent(_EventOPEvent):
    data: TrackStartEventOP


@attrs.define(kw_only=True, frozen=True)
class TrackStuckEvent(_EventOPEvent):
    data: TrackStuckEventOP


@attrs.define(kw_only=True, frozen=True)
class DiscordWebsocketClosedEvent(_EventOPEvent):
    data: DiscordWebsocketClosedEventOP


@attrs.define(kw_only=True, frozen=True)
class TrackEndEvent(_EventOPEvent):
    data: TrackEndEventOP


@attrs.define(kw_only=True, frozen=True)
class TrackExceptionEvent(_EventOPEvent):
    data: TrackExceptionEventOP
