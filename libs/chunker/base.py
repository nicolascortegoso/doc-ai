from abc import ABC, abstractmethod
from typing import ClassVar

from libs.common.enums import FileType
from libs.common.models import DocumentChunk, ParsedDocument


class BaseChunkingStrategy(ABC):
    """Abstract base for all chunking strategies.

    Priority contract:
        get_priority() must return an integer in the range [1, 100].
        Higher values take precedence. SlidingWindowChunkingStrategy always
        declares 1 as it is the default last resort.
    """

    @property
    @abstractmethod
    def supported_mime_types(self) -> ClassVar[list[FileType]]:
        """Declares which FileType values this strategy handles.

        Used by the registry for startup conflict detection and MIME filtering.
        """

    @abstractmethod
    def can_handle(self, document: ParsedDocument) -> bool:
        """Inspect the document to decide suitability.

        Called only after MIME filtering. Returns True if this strategy
        can process the given document.
        """

    @abstractmethod
    def get_priority(self) -> int:
        """Returns an integer priority in the range [1, 100].

        Higher value wins when multiple strategies match.
        SlidingWindowChunkingStrategy always returns 1.
        """

    @abstractmethod
    def chunk(self, document: ParsedDocument) -> list[DocumentChunk]:
        """Produce a list of DocumentChunk from the document.

        Returns an empty list if the document has no content.
        """