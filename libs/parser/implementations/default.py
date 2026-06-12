from typing import ClassVar

from libs.common.enums import FileType
from libs.common.models import PageProfile
from libs.parser.base import BasePageExtractionStrategy


class DefaultPageExtractionStrategy(BasePageExtractionStrategy):
    """Baseline strategy that matches every file type and every page.

    Always registered explicitly by the consuming project. Declares all
    FileType values (including UNKNOWN) in supported_mime_types, always
    returns True from can_handle, and always declares priority 1 — ensuring
    it is the last resort when no higher-priority strategy matches.

    Returns an empty string for every page — no content is extracted.
    """

    supported_mime_types: ClassVar[list[FileType]] = list(FileType)

    def can_handle(self, page_profile: PageProfile) -> bool:
        return True

    def get_priority(self) -> int:
        return 1

    def extract(self, file_bytes: bytes, page_profile: PageProfile) -> str:
        return ""