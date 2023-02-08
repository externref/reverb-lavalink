import enum


class OPTypes(enum.Enum):
    READY = "ready"
    PLAYER_UPDATE = "playerUpdate"
    STATS = "stats"
    EVENT = "event"


class EventType(enum.Enum):
    TRACK_START = "TrackStartEvent"
    TRACK_END = "TrackEndEvent"
    TRACK_STUCK_EVENT = "TrackStuckEvent"
    TRACK_EXCEPTION_EVENT = "TrackExceptionEvent"
    WEBSOCKET_CLOSED_EVENT = "WebsocketClosedEvent"


class ExceptionSeverity(enum.Enum):
    COMMON = "COMMON"
    SUSPICIOUS = "SUSPICIOUS"
    FATAL = "FATAL"


class TrackEndReason(enum.Enum):
    FINISHED = "FINISHED"
    LOAD_FAILED = "LOAD_FAILED"
    STOPPED = "STOPPED"
    REPLACED = "REPLACED"
    CLEANUP = "CLEANUP"
