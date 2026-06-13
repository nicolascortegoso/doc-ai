from abc import ABC, abstractmethod
from typing import ClassVar

from libs.common.enums import FileType
from libs.common.models import PageProfile


class BasePageExtractionStrategy(ABC):
    """Abstract base for all page extraction strategies.

    Priority contract:
        get_priority() must return an integer in the range [1, 100].
        Higher values take precedence. DefaultPageExtractionStrategy always
        declares 1, making it the last resort when no higher-priority
        strategy matches.
    """

    @property
    @abstractmethod
    def supported_mime_types(self) -> ClassVar[list[FileType]]:
        """Declares which FileType values this strategy handles.

        Used by the registry for startup conflict detection and MIME filtering.
        """

    @abstractmethod
    def can_handle(self, page_profile: PageProfile) -> bool:
        """Inspect the page profile to decide suitability.

        Called only after MIME filtering. Returns True if this strategy
        can process the given page (e.g. page has extractable text,
        is not scanned, etc.).
        """

    @abstractmethod
    def get_priority(self) -> int:
        """Returns an integer priority in the range [1, 100].

        Higher value wins when multiple strategies match. DefaultPageExtractionStrategy
        always returns 1 to ensure it is the last resort.
        """

    @abstractmethod
    def extract(self, file_bytes: bytes, page_profile: PageProfile) -> str:
        """Extract text content from the given page.

        Returns the extracted text for the page. May return an empty
        string if no content can be extracted.
        """