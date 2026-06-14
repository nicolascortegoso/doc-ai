from abc import ABC, abstractmethod
from uuid import UUID

from common.models import Message


class Memory(ABC):
    @abstractmethod
    def add(self, message: Message, session_id: UUID) -> None:
        """Add a message to the session history."""

    @abstractmethod
    def get(self, session_id: UUID) -> list[Message]:
        """Retrieve all messages for a session. Returns empty list if not found."""

    @abstractmethod
    def clear(self, session_id: UUID) -> None:
        """Clear all messages for a session. No-op if not found."""