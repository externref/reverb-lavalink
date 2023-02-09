"""
A Lavalink library for the discord API wrapper, hikari.
"""

from __future__ import annotations

from .client import LavalinkClient
from .enums import ExceptionSeverity, TrackEndReason
from .events import (
    DiscordWebsocketClosedEvent,
    LavalinkReadyEvent,
    PlayerUpdateEvent,
    ReverbEvent,
    StatsEvent,
    TrackEndEvent,
    TrackExceptionEvent,
    TrackStartEvent,
    TrackStuckEvent,
)

__all__: tuple[str, ...] = (
    # client.py
    "LavalinkClient",
    # events.py
    "LavalinkReadyEvent",
    "ReverbEvent",
    "PlayerUpdateEvent",
    "StatsEvent",
    "TrackStartEvent",
    "TrackStuckEvent",
    "TrackEndEvent",
    "TrackExceptionEvent",
    "DiscordWebsocketClosedEvent",
    # enums.py
    "ExceptionSeverity",
    "TrackEndReason",
)

__version__ = "0.0.1a"
