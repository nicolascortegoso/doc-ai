from typing import ClassVar

from libs.common.enums import FileType
from libs.common.models import DocumentProfile
from libs.profiler.base import BaseDocumentProfiler


class DefaultProfiler(BaseDocumentProfiler):
    """Baseline profiler that matches every file type.

    Always registered explicitly by the consuming project. Declares all
    FileType values (including UNKNOWN) in supported_mime_types, always
    returns True from can_handle, and always declares priority 1 — ensuring
    it is the last resort when no higher-priority profiler matches.

    Does not require a Detector — no text or MIME detection is performed.
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