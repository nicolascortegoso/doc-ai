from typing import ClassVar

import fitz  # PyMuPDF

from libs.common.enums import FileType
from libs.common.models import PageProfile
from libs.parser.base import BasePageExtractionStrategy
from libs.text.base import TextCleaner
from libs.text.implementations.passthrough import PassthroughTextCleaner


class PlainPdfExtractionStrategy(BasePageExtractionStrategy):
    """Extracts plain text from text-based PDF pages using PyMuPDF.

    Handles only pages that have extractable text and are not scanned.
    Text is passed through an injected TextCleaner before being returned.
    """

    supported_mime_types: ClassVar[list[FileType]] = [FileType.PDF]

    def __init__(self, text_cleaner: TextCleaner = None) -> None:
        self._text_cleaner = text_cleaner or PassthroughTextCleaner()

    def can_handle(self, page_profile: PageProfile) -> bool:
        return page_profile.has_text and not page_profile.is_scanned

    def get_priority(self) -> int:
        return 50

    def extract(self, file_bytes: bytes, page_profile: PageProfile) -> str:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        try:
            page = doc[page_profile.page_number - 1]
            text = page.get_text("text")
            return self._text_cleaner.clean(text)
        finally:
            doc.close()