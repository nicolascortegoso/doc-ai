from abc import ABC, abstractmethod


class Tool(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Unique name identifying the tool."""

    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable description — used by the agent to decide when to invoke it."""

    @abstractmethod
    def invoke(self, input: str) -> str:
        """Execute the tool with the given input. Never raises."""