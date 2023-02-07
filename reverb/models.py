from __future__ import annotations

import attrs


@attrs.define(kw_only=True, slots=True, frozen=True, repr=True)
class PlayerState:
    time: int
    position: int | None
    connected: bool
    ping: int


@attrs.define(kw_only=True, slots=True, frozen=True, repr=True)
class Memory:
    used: int
    free: int
    allocated: int
    reservable: int


@attrs.define(kw_only=True, slots=True, frozen=True, repr=True)
class CPU:
    cores: int
    system_load: float
    lavalink_load: float


@attrs.define(kw_only=True, slots=True, frozen=True, repr=True)
class FrameStats:
    sent: int
    nulled: int
    deficit: int
