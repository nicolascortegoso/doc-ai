from typing import ClassVar

import fitz  # PyMuPDF

from libs.language.base import LanguageDetector
from libs.profiler.base import BaseDocumentProfiler
from libs.common.enums import FileType, Layout
from libs.common.models import DocumentProfile, PageProfile


class PdfProfiler(BaseDocumentProfiler):
    """PDF-specific profiler using PyMuPDF.

    Detects per-page structural metadata: text, images, tables, scanned pages,
    column layout, and language.

    Requires a LanguageDetector injected at construction time.
    """

    supported_mime_types: ClassVar[list[FileType]] = [FileType.PDF]

    def __init__(self, language_detector: LanguageDetector) -> None:
        self._language_detector = language_detector

    def can_handle(self, file_bytes: bytes) -> bool:
        """Returns False for encrypted PDFs, True otherwise."""
        try:
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            encrypted = doc.is_encrypted
            doc.close()
            return not encrypted
        except Exception:
            return False

    def get_priority(self) -> int:
        return 50

    def profile(self, file_bytes: bytes) -> DocumentProfile:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        try:
            pages = [self._profile_page(page) for page in doc]
            return DocumentProfile(
                mime_type=FileType.PDF,
                page_count=doc.page_count,
                pages=pages,
            )
        finally:
            doc.close()

    def _profile_page(self, page: fitz.Page) -> PageProfile:
        text = page.get_text().strip()
        has_text = bool(text)
        has_images = bool(page.get_images())
        has_tables = bool(page.find_tables().tables)
        is_scanned = not has_text and has_images

        layout = Layout.SINGLE_COLUMN if has_text else Layout.UNKNOWN
        language = self._language_detector.detect(text) if has_text else None

        return PageProfile(
            page_number=page.number + 1,
            has_text=has_text,
            has_images=has_images,
            has_tables=has_tables,
            is_scanned=is_scanned,
            layout=layout,
            language=language,
        )