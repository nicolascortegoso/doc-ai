from abc import ABC, abstractmethod
from typing import ClassVar

from libs.common.enums import FileType
from libs.common.models import DocumentChunk, IndexedChunk


class BaseIndexingStrategy(ABC):
    """Abstract base for all indexing strategies.

    Priority contract:
        get_priority() must return an integer in the range [1, 100].
        Higher values take precedence. BatchIndexer always declares 1,
        making it the last resort when no higher-priority strategy matches.
    """

    @property
    @abstractmethod
    def supported_mime_types(self) -> ClassVar[list[FileType]]:
        """Declares which FileType values this strategy handles.

        Used by the registry for startup conflict detection and MIME filtering.
        """

    @abstractmethod
    def can_handle(self, chunks: list[DocumentChunk]) -> bool:
        """Inspect the chunks to decide suitability.

        Called only after MIME filtering. Returns True if this strategy
        can process the given chunks.
        """

    @abstractmethod
    def get_priority(self) -> int:
        """Returns an integer priority in the range [1, 100].

        Higher value wins when multiple strategies match.
        BatchIndexer always returns 1.
        """

    @abstractmethod
    def index(self, chunks: list[DocumentChunk]) -> list[IndexedChunk]:
        """Produce a list of IndexedChunk from the given chunks.

        Returns an empty list if chunks is empty.
        """