from typing import ClassVar

from libs.profiler.base import BaseDocumentProfiler
from libs.profiler.enums import FileType
from libs.profiler.models import DocumentProfile


class DefaultProfiler(BaseDocumentProfiler):
    """Baseline profiler that matches every file type.

    Always registered explicitly by the consuming project. Declares all
    FileType values (including UNKNOWN) in supported_mime_types, always
    returns True from can_handle, and always declares priority 1 — ensuring
    it is the last resort when no higher-priority profiler matches.

    Does not require a LanguageDetector — no text is extracted.
    """

    supported_mime_types: ClassVar[list[FileType]] = list(FileType)

    def can_handle(self, file_bytes: bytes) -> bool:
        return True

    def get_priority(self) -> int:
        return 1

    def profile(self, file_bytes: bytes) -> DocumentProfile:
        return DocumentProfile(
            mime_type=FileType.UNKNOWN,
            page_count=0,
            pages=[],
        )
