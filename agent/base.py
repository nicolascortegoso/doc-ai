from abc import ABC, abstractmethod
from uuid import UUID

from common.models import AgentResponse


class Agent(ABC):
    """Abstract base for all agent implementations.

    Designed to accommodate both simple QA systems and complex multi-turn
    reasoning agents. The TAO cycle, memory management, and tool invocation
    are implementation details.
    """

    @abstractmethod
    def chat(self, message: str, session_id: UUID) -> AgentResponse:
        """Process a message and return a response. Never raises."""