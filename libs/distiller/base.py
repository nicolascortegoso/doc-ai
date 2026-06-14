from abc import ABC, abstractmethod
from typing import ClassVar
from uuid import UUID

from common.enums import FileType
from common.models import GlossaryEntry, ParsedDocument


class BaseDistillerStrategy(ABC):
    """Abstract base for all distiller strategies.

    Priority contract:
        get_priority() must return an integer in the range [1, 100].
        Higher values take precedence. GlossaryDistillerStrategy always
        declares 1, making it the last resort when no higher-priority
        strategy matches.
    """

    @property
    @abstractmethod
    def supported_mime_types(self) -> ClassVar[list[FileType]]:
        """Declares which FileType values this strategy handles."""

    @abstractmethod
    def can_handle(self, document: ParsedDocument) -> bool:
        """Inspect the document to decide suitability."""

    @abstractmethod
    def get_priority(self) -> int:
        """Returns an integer priority in the range [1, 100]."""

    @abstractmethod
    def distill(self, document: ParsedDocument, document_id: UUID) -> list[GlossaryEntry]:
        """Produce a list of GlossaryEntry from the document."""