from dataclasses import dataclass, field
from uuid import uuid4
from app.core.stages import Stage, STAGE_LABELS


@dataclass
class SessionState:
    session_id: str
    stage: Stage
    interest: str | None = None
    mastery: dict[str, int] = field(default_factory=dict)
    messages: list[dict[str, str]] = field(default_factory=list)


class MemoryStore:
    def __init__(self) -> None:
        self.sessions: dict[str, SessionState] = {}

    def create_session(self, stage: Stage, interest: str | None = None) -> SessionState:
        session = SessionState(session_id=str(uuid4()), stage=stage, interest=interest)
        session.mastery = {
            "classification": 30,
            "features": 20,
            "train-test": 10,
            "simple-classifier": 0,
        }
        self.sessions[session.session_id] = session
        return session

    def get_session(self, session_id: str) -> SessionState | None:
        return self.sessions.get(session_id)

    def require_session(self, session_id: str) -> SessionState:
        session = self.get_session(session_id)
        if session is None:
            raise KeyError(f"unknown session_id: {session_id}")
        return session

    def stage_label(self, stage: Stage) -> str:
        return STAGE_LABELS[stage]


store = MemoryStore()
