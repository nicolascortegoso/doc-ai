import pytest

from libs.common.enums import FileType
from libs.common.models import ParsedDocument, ParsedPage


def _make_parsed_page(page_number: int, content: str = "") -> ParsedPage:
    return ParsedPage(
        page_number=page_number,
        content=content,
        strategy="DefaultPageExtractionStrategy",
    )


class TestMarkdownDocument:
    def test_to_markdown_single_page_with_content(self):
        doc = ParsedDocument(
            mime_type=FileType.PDF,
            page_count=1,
            pages=[_make_parsed_page(1, "# Hello\n\nSome text.")],
        )
        assert doc.to_markdown() == "<!-- page 1 -->\n# Hello\n\nSome text."

    def test_to_markdown_multiple_pages(self):
        doc = ParsedDocument(
            mime_type=FileType.PDF,
            page_count=3,
            pages=[
                _make_parsed_page(1, "Page one."),
                _make_parsed_page(2, "Page two."),
                _make_parsed_page(3, "Page three."),
            ],
        )
        result = doc.to_markdown()
        assert "<!-- page 1 -->\nPage one." in result
        assert "<!-- page 2 -->\nPage two." in result
        assert "<!-- page 3 -->\nPage three." in result

    def test_to_markdown_pages_joined_by_double_newline(self):
        doc = ParsedDocument(
            mime_type=FileType.PDF,
            page_count=2,
            pages=[
                _make_parsed_page(1, "First."),
                _make_parsed_page(2, "Second."),
            ],
        )
        assert doc.to_markdown() == "<!-- page 1 -->\nFirst.\n\n<!-- page 2 -->\nSecond."

    def test_to_markdown_empty_page_still_emits_delimiter(self):
        doc = ParsedDocument(
            mime_type=FileType.PDF,
            page_count=2,
            pages=[
                _make_parsed_page(1, "Some content."),
                _make_parsed_page(2, ""),
            ],
        )
        result = doc.to_markdown()
        assert "<!-- page 2 -->" in result

    def test_to_markdown_all_empty_pages_still_emit_delimiters(self):
        doc = ParsedDocument(
            mime_type=FileType.PDF,
            page_count=2,
            pages=[_make_parsed_page(1, ""), _make_parsed_page(2, "")],
        )
        result = doc.to_markdown()
        assert "<!-- page 1 -->" in result
        assert "<!-- page 2 -->" in result

    def test_to_markdown_empty_pages_list(self):
        doc = ParsedDocument(mime_type=FileType.PDF, page_count=0, pages=[])
        assert doc.to_markdown() == ""