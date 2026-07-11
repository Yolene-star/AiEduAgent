from dataclasses import dataclass, field
from pathlib import Path
import json
import os
import sqlite3
from uuid import uuid4
from app.core.stages import Stage, STAGE_LABELS


@dataclass
class SessionState:
    session_id: str
    stage: Stage
    interest: str | None = None
    mastery: dict[str, int] = field(default_factory=dict)
    messages: list[dict[str, str]] = field(default_factory=list)


class SQLiteStore:
    def __init__(self, db_path: str | Path | None = None) -> None:
        configured_path = os.getenv("SQLITE_DB_PATH")
        self.db_path = Path(db_path or configured_path or Path(__file__).resolve().parents[2] / "aieduagent.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self.connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    stage TEXT NOT NULL,
                    interest TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS mastery (
                    session_id TEXT NOT NULL,
                    knowledge_point_id TEXT NOT NULL,
                    score INTEGER NOT NULL,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (session_id, knowledge_point_id),
                    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
                );

                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
                );

                CREATE TABLE IF NOT EXISTS quiz_attempts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    question_id TEXT NOT NULL,
                    answer TEXT,
                    correct INTEGER NOT NULL,
                    mastery_after INTEGER NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
                );
                """
            )

    def create_session(self, stage: Stage, interest: str | None = None) -> SessionState:
        session = SessionState(session_id=str(uuid4()), stage=stage, interest=interest)
        session.mastery = {
            "classification": 30,
            "features": 20,
            "train-test": 10,
            "simple-classifier": 0,
        }
        with self.connect() as conn:
            conn.execute(
                "INSERT INTO sessions (session_id, stage, interest) VALUES (?, ?, ?)",
                (session.session_id, stage.value, interest),
            )
            conn.executemany(
                """
                INSERT INTO mastery (session_id, knowledge_point_id, score)
                VALUES (?, ?, ?)
                """,
                [(session.session_id, point_id, score) for point_id, score in session.mastery.items()],
            )
        return session

    def get_session(self, session_id: str) -> SessionState | None:
        with self.connect() as conn:
            row = conn.execute(
                "SELECT session_id, stage, interest FROM sessions WHERE session_id = ?",
                (session_id,),
            ).fetchone()
            if row is None:
                return None
            mastery_rows = conn.execute(
                "SELECT knowledge_point_id, score FROM mastery WHERE session_id = ?",
                (session_id,),
            ).fetchall()
            message_rows = conn.execute(
                "SELECT role, content FROM messages WHERE session_id = ? ORDER BY id ASC",
                (session_id,),
            ).fetchall()
        return SessionState(
            session_id=str(row["session_id"]),
            stage=Stage(str(row["stage"])),
            interest=row["interest"],
            mastery={str(item["knowledge_point_id"]): int(item["score"]) for item in mastery_rows},
            messages=[{"role": str(item["role"]), "content": str(item["content"])} for item in message_rows],
        )

    def require_session(self, session_id: str) -> SessionState:
        session = self.get_session(session_id)
        if session is None:
            raise KeyError(f"unknown session_id: {session_id}")
        return session

    def set_mastery(self, session_id: str, knowledge_point_id: str, score: int) -> None:
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO mastery (session_id, knowledge_point_id, score, updated_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(session_id, knowledge_point_id)
                DO UPDATE SET score = excluded.score, updated_at = CURRENT_TIMESTAMP
                """,
                (session_id, knowledge_point_id, score),
            )

    def add_message(self, session_id: str, role: str, content: str) -> None:
        with self.connect() as conn:
            conn.execute(
                "INSERT INTO messages (session_id, role, content) VALUES (?, ?, ?)",
                (session_id, role, content),
            )

    def record_quiz_attempt(
        self,
        session_id: str,
        question_id: str,
        answer: str | None,
        correct: bool,
        mastery_after: int,
    ) -> None:
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO quiz_attempts (session_id, question_id, answer, correct, mastery_after)
                VALUES (?, ?, ?, ?, ?)
                """,
                (session_id, question_id, answer, int(correct), mastery_after),
            )

    def list_sessions(self) -> list[SessionState]:
        with self.connect() as conn:
            rows = conn.execute("SELECT session_id FROM sessions ORDER BY created_at ASC").fetchall()
        return [self.require_session(str(row["session_id"])) for row in rows]

    def export_debug_snapshot(self) -> str:
        sessions = self.list_sessions()
        return json.dumps(
            [
                {
                    "session_id": session.session_id,
                    "stage": session.stage.value,
                    "interest": session.interest,
                    "mastery": session.mastery,
                    "messages": session.messages,
                }
                for session in sessions
            ],
            ensure_ascii=False,
        )

    def stage_label(self, stage: Stage) -> str:
        return STAGE_LABELS[stage]


store = SQLiteStore()
