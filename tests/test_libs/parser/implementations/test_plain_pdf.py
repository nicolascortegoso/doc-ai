from __future__ import annotations

import io
from unittest.mock import MagicMock

import fitz
import pytest

from common.enums import FileType, Layout
from common.models import PageProfile
from libs.parser.implementations.plain_pdf import PlainPdfExtractionStrategy
from libs.parser.postprocessor.base import Postprocessor
from libs.parser.postprocessor.implementations.passthrough import PassthroughPostprocessor


def _make_page_profile(
    page_number: int = 1,
    has_text: bool = True,
    is_scanned: bool = False,
) -> PageProfile:
    return PageProfile(
        page_number=page_number,
        has_text=has_text,
        has_images=False,
        has_tables=False,
        is_scanned=is_scanned,
        layout=Layout.SINGLE_COLUMN,
        language="en",
    )


def _make_pdf(pages: list[str]) -> bytes:
    """Build a PDF with one page per string in the list."""
    doc = fitz.open()
    for text in pages:
        page = doc.new_page()
        if text:
            page.insert_text((50, 50), text)
    buf = io.BytesIO()
    doc.save(buf)
    doc.close()
    return buf.getvalue()


@pytest.fixture
def strategy() -> PlainPdfExtractionStrategy:
    return PlainPdfExtractionStrategy()


@pytest.fixture
def single_page_pdf() -> bytes:
    return _make_pdf(["Hello world, this is a test document."])


@pytest.fixture
def multipage_pdf() -> bytes:
    return _make_pdf(["Page one content.", "Page two content.", "Page three content."])


class TestPlainPdfStrategyMetadata:
    def test_supported_mime_types_contains_only_pdf(self, strategy):
        assert strategy.supported_mime_types == [FileType.PDF]

    def test_get_priority_returns_50(self, strategy):
        assert strategy.get_priority() == 50


class TestPlainPdfStrategyCanHandle:
    def test_returns_true_for_text_page(self, strategy):
        assert strategy.can_handle(_make_page_profile(has_text=True, is_scanned=False)) is True

    def test_returns_false_for_scanned_page(self, strategy):
        assert strategy.can_handle(_make_page_profile(has_text=False, is_scanned=True)) is False

    def test_returns_false_for_page_with_no_text(self, strategy):
        assert strategy.can_handle(_make_page_profile(has_text=False, is_scanned=False)) is False

    def test_returns_false_for_scanned_page_with_text_flag(self, strategy):
        assert strategy.can_handle(_make_page_profile(has_text=True, is_scanned=True)) is False


class TestPlainPdfStrategyExtract:
    def test_returns_non_empty_string_for_text_page(self, strategy, single_page_pdf):
        result = strategy.extract(single_page_pdf, _make_page_profile(1))
        assert isinstance(result, str)
        assert len(result) > 0

    def test_returns_correct_text_content(self, strategy, single_page_pdf):
        result = strategy.extract(single_page_pdf, _make_page_profile(1))
        assert "Hello world" in result

    def test_extracts_correct_page_in_multipage_pdf(self, strategy, multipage_pdf):
        result_p1 = strategy.extract(multipage_pdf, _make_page_profile(1))
        result_p2 = strategy.extract(multipage_pdf, _make_page_profile(2))
        result_p3 = strategy.extract(multipage_pdf, _make_page_profile(3))
        assert "Page one" in result_p1
        assert "Page two" in result_p2
        assert "Page three" in result_p3

    def test_does_not_mix_page_content(self, strategy, multipage_pdf):
        result_p1 = strategy.extract(multipage_pdf, _make_page_profile(1))
        assert "Page two" not in result_p1
        assert "Page three" not in result_p1


class TestPlainPdfStrategyPostprocessor:
    def test_uses_passthrough_postprocessor_by_default(self, single_page_pdf):
        strategy = PlainPdfExtractionStrategy()
        result = strategy.extract(single_page_pdf, _make_page_profile(1))
        assert isinstance(result, str)

    def test_process_called_with_extracted_text(self, single_page_pdf):
        mock_postprocessor = MagicMock(spec=Postprocessor)
        mock_postprocessor.process.return_value = "processed text"
        strategy = PlainPdfExtractionStrategy(postprocessor=mock_postprocessor)
        result = strategy.extract(single_page_pdf, _make_page_profile(1))
        mock_postprocessor.process.assert_called_once()
        assert result == "processed text"

    def test_custom_postprocessor_output_is_returned(self, single_page_pdf):
        mock_postprocessor = MagicMock(spec=Postprocessor)
        mock_postprocessor.process.return_value = "## Transformed"
        strategy = PlainPdfExtractionStrategy(postprocessor=mock_postprocessor)
        result = strategy.extract(single_page_pdf, _make_page_profile(1))
        assert result == "## Transformed"