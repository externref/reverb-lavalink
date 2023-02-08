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


@attrs.define(kw_only=True, slots=True, frozen=True, repr=True)
class Version:
    sem_ver: str
    minor: int
    major: int
    patch: int
    pre_release: str | None


@attrs.define(kw_only=True, slots=True, frozen=True, repr=True)
class Git:
    branch: str
    commit: str
    commit_timestamp: int


@attrs.define(kw_only=True, slots=True, frozen=True, repr=True)
class Plugin:
    name: str
    version: str


@attrs.define(kw_only=True, slots=True, frozen=True, repr=True)
class LavalinkServerInfo:
    version: Version
    git: Git
    build_timestamp: int
    jvm: str
    lavaplayer: str
    source_managers: list[str]
    filters: list[str]
    plugins: list[Plugin]
