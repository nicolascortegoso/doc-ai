from __future__ import annotations

import io
from unittest.mock import MagicMock

import fitz
import pytest

from libs.language.base import LanguageDetector
from libs.language.implementations.dummy import DummyLanguageDetector
from libs.profiler.enums import FileType, Layout
from libs.profiler.implementations.pdf import PdfProfiler


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_text_pdf(text: str = "Hello world, this is a test document.") -> bytes:
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), text)
    buf = io.BytesIO()
    doc.save(buf)
    doc.close()
    return buf.getvalue()


def _make_image_pdf() -> bytes:
    """Single page with an image and no text — simulates a scanned page."""
    doc = fitz.open()
    page = doc.new_page()
    pix = fitz.Pixmap(fitz.csRGB, fitz.IRect(0, 0, 10, 10))
    pix.set_rect(fitz.IRect(0, 0, 10, 10), (255, 0, 0))
    page.insert_image(fitz.Rect(50, 50, 150, 150), pixmap=pix)
    buf = io.BytesIO()
    doc.save(buf)
    doc.close()
    return buf.getvalue()


def _make_encrypted_pdf() -> bytes:
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "secret")
    buf = io.BytesIO()
    doc.save(buf, encryption=fitz.PDF_ENCRYPT_AES_256, user_pw="pass")
    doc.close()
    return buf.getvalue()


def _make_multipage_pdf() -> bytes:
    doc = fitz.open()
    # Page 1: text
    p1 = doc.new_page()
    p1.insert_text((50, 50), "Page one text content.")
    # Page 2: image only
    p2 = doc.new_page()
    pix = fitz.Pixmap(fitz.csRGB, fitz.IRect(0, 0, 10, 10))
    pix.set_rect(fitz.IRect(0, 0, 10, 10), (0, 255, 0))
    p2.insert_image(fitz.Rect(50, 50, 150, 150), pixmap=pix)
    buf = io.BytesIO()
    doc.save(buf)
    doc.close()
    return buf.getvalue()


@pytest.fixture
def profiler() -> PdfProfiler:
    return PdfProfiler(language_detector=DummyLanguageDetector())


# ---------------------------------------------------------------------------
# Metadata
# ---------------------------------------------------------------------------

class TestPdfProfilerMetadata:
    def test_supported_mime_types_contains_only_pdf(self, profiler):
        assert profiler.supported_mime_types == [FileType.PDF]

    def test_get_priority_returns_50(self, profiler):
        assert profiler.get_priority() == 50


# ---------------------------------------------------------------------------
# can_handle
# ---------------------------------------------------------------------------

class TestPdfProfilerCanHandle:
    def test_returns_true_for_normal_pdf(self, profiler):
        assert profiler.can_handle(_make_text_pdf()) is True

    def test_returns_false_for_encrypted_pdf(self, profiler):
        assert profiler.can_handle(_make_encrypted_pdf()) is False

    def test_returns_false_for_garbage_bytes(self, profiler):
        assert profiler.can_handle(b"\x00\x01\x02garbage") is False


# ---------------------------------------------------------------------------
# profile — document level
# ---------------------------------------------------------------------------

class TestPdfProfilerDocumentLevel:
    def test_mime_type_is_pdf(self, profiler):
        result = profiler.profile(_make_text_pdf())
        assert result.mime_type == FileType.PDF

    def test_page_count_single_page(self, profiler):
        result = profiler.profile(_make_text_pdf())
        assert result.page_count == 1

    def test_page_count_multipage(self, profiler):
        result = profiler.profile(_make_multipage_pdf())
        assert result.page_count == 2

    def test_pages_length_matches_page_count(self, profiler):
        result = profiler.profile(_make_multipage_pdf())
        assert len(result.pages) == result.page_count

    def test_page_numbers_are_1_based(self, profiler):
        result = profiler.profile(_make_multipage_pdf())
        assert result.pages[0].page_number == 1
        assert result.pages[1].page_number == 2


# ---------------------------------------------------------------------------
# profile — page with text
# ---------------------------------------------------------------------------

class TestPdfProfilerTextPage:
    def test_has_text_true(self, profiler):
        result = profiler.profile(_make_text_pdf())
        assert result.pages[0].has_text is True

    def test_is_scanned_false(self, profiler):
        result = profiler.profile(_make_text_pdf())
        assert result.pages[0].is_scanned is False

    def test_layout_is_single_column(self, profiler):
        result = profiler.profile(_make_text_pdf())
        assert result.pages[0].layout == Layout.SINGLE_COLUMN

    def test_language_is_set(self, profiler):
        result = profiler.profile(_make_text_pdf())
        assert result.pages[0].language == "en"


# ---------------------------------------------------------------------------
# profile — scanned page (image only, no text)
# ---------------------------------------------------------------------------

class TestPdfProfilerScannedPage:
    def test_has_text_false(self, profiler):
        result = profiler.profile(_make_image_pdf())
        assert result.pages[0].has_text is False

    def test_has_images_true(self, profiler):
        result = profiler.profile(_make_image_pdf())
        assert result.pages[0].has_images is True

    def test_is_scanned_true(self, profiler):
        result = profiler.profile(_make_image_pdf())
        assert result.pages[0].is_scanned is True

    def test_layout_is_unknown(self, profiler):
        result = profiler.profile(_make_image_pdf())
        assert result.pages[0].layout == Layout.UNKNOWN

    def test_language_is_none(self, profiler):
        result = profiler.profile(_make_image_pdf())
        assert result.pages[0].language is None


# ---------------------------------------------------------------------------
# language detector interaction
# ---------------------------------------------------------------------------

class TestPdfProfilerLanguageDetector:
    def test_detect_called_with_page_text(self):
        mock_detector = MagicMock(spec=LanguageDetector)
        mock_detector.detect.return_value = "fr"
        profiler = PdfProfiler(language_detector=mock_detector)

        result = profiler.profile(_make_text_pdf("Bonjour le monde"))

        mock_detector.detect.assert_called_once()
        call_arg = mock_detector.detect.call_args[0][0]
        assert "Bonjour" in call_arg
        assert result.pages[0].language == "fr"

    def test_detect_not_called_for_image_only_page(self):
        mock_detector = MagicMock(spec=LanguageDetector)
        profiler = PdfProfiler(language_detector=mock_detector)

        profiler.profile(_make_image_pdf())

        mock_detector.detect.assert_not_called()