from __future__ import annotations

import typing

import attrs
import hikari

if typing.TYPE_CHECKING:
    from reverb.gateway import PlayerUpdateOP, ReadyOP, StatsOP


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
