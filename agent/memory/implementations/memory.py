from uuid import UUID

from common.models import Message
from agent.memory.base import Memory


class InMemoryMemory(Memory):
    """In-memory memory store for testing and local development.

    Stores messages in a Python dict keyed by session_id.
    Not thread-safe.
    """

    def __init__(self) -> None:
        self._store: dict[str, list[Message]] = {}

    def add(self, message: Message, session_id: UUID) -> None:
        key = str(session_id)
        if key not in self._store:
            self._store[key] = []
        self._store[key].append(message)

    def get(self, session_id: UUID) -> list[Message]:
        return list(self._store.get(str(session_id), []))

    def clear(self, session_id: UUID) -> None:
        self._store.pop(str(session_id), None)