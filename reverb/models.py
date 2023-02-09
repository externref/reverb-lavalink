from __future__ import annotations

import typing

import attrs

from reverb.enums import EventType, ExceptionSeverity, TrackEndReason


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

    @classmethod
    def create(cls, payload: dict[str, typing.Any]) -> Version:
        return cls(
            sem_ver=payload["semVer"],
            minor=payload["minor"],
            major=payload["major"],
            patch=payload["patch"],
            pre_release=payload.get("preRelease"),
        )


@attrs.define(kw_only=True, slots=True, frozen=True, repr=True)
class Git:
    branch: str
    commit: str
    commit_timestamp: int

    @classmethod
    def create(cls, payload: dict[str, typing.Any]) -> Git:
        return cls(branch=payload["branch"], commit=payload["commit"], commit_timestamp=payload["commitTime"])


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

    @classmethod
    def create(cls, payload: dict[str, typing.Any]) -> LavalinkServerInfo:
        return cls(
            version=Version.create(payload["version"]),
            git=Git.create(payload["git"]),
            build_timestamp=payload["buildTime"],
            jvm=payload["jvm"],
            lavaplayer=payload["javaplayer"],
            source_managers=payload["sourceManagers"],
            filters=payload["filters"],
            plugins=list(map(lambda data: Plugin(**data), payload["plugins"])),
        )
