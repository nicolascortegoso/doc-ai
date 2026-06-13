from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from libs.common.enums import FileType
from libs.common.models import ParsedDocument, ParsedPage
from libs.chunker.implementations.sliding_window import SlidingWindowChunkingStrategy
from libs.splitter.base import Splitter
from libs.splitter.implementations.character import CharacterSplitter


def _make_document(
    pages: list[tuple[int, str]],
    mime_type: FileType = FileType.PDF,
) -> ParsedDocument:
    parsed_pages = [
        ParsedPage(page_number=n, content=content, strategy="PlainPdfExtractionStrategy")
        for n, content in pages
    ]
    return ParsedDocument(
        mime_type=mime_type,
        page_count=len(parsed_pages),
        pages=parsed_pages,
    )


def _make_single_page(content: str, mime_type: FileType = FileType.PDF) -> ParsedDocument:
    return _make_document([(1, content)], mime_type=mime_type)


class TestSlidingWindowMetadata:
    def test_supported_mime_types_covers_all_file_types(self):
        strategy = SlidingWindowChunkingStrategy()
        for file_type in FileType:
            assert file_type in strategy.supported_mime_types

    def test_get_priority_returns_1(self):
        assert SlidingWindowChunkingStrategy().get_priority() == 1

    def test_can_handle_always_returns_true(self):
        strategy = SlidingWindowChunkingStrategy()
        assert strategy.can_handle(_make_single_page("content")) is True


class TestSlidingWindowConstruction:
    def test_default_window_size_is_1000(self):
        assert SlidingWindowChunkingStrategy()._window_size == 1000

    def test_default_overlap_ratio_is_0_2(self):
        assert SlidingWindowChunkingStrategy()._overlap_ratio == 0.2

    def test_default_splitter_is_character(self):
        strategy = SlidingWindowChunkingStrategy()
        assert isinstance(strategy._splitter, CharacterSplitter)

    def test_raises_on_overlap_ratio_of_1(self):
        with pytest.raises(ValueError):
            SlidingWindowChunkingStrategy(overlap_ratio=1.0)

    def test_raises_on_negative_overlap_ratio(self):
        with pytest.raises(ValueError):
            SlidingWindowChunkingStrategy(overlap_ratio=-0.1)

    def test_raises_on_zero_window_size(self):
        with pytest.raises(ValueError):
            SlidingWindowChunkingStrategy(window_size=0)

    def test_custom_splitter_is_used(self):
        mock_splitter = MagicMock(spec=Splitter)
        strategy = SlidingWindowChunkingStrategy(splitter=mock_splitter)
        assert strategy._splitter is mock_splitter


class TestSlidingWindowEdgeCases:
    def test_empty_document_returns_empty_list(self):
        strategy = SlidingWindowChunkingStrategy()
        assert strategy.chunk(_make_single_page("")) == []

    def test_all_empty_pages_returns_empty_list(self):
        strategy = SlidingWindowChunkingStrategy()
        doc = _make_document([(1, ""), (2, ""), (3, "")])
        assert strategy.chunk(doc) == []

    def test_document_shorter_than_window_produces_single_chunk(self):
        strategy = SlidingWindowChunkingStrategy(window_size=1000)
        result = strategy.chunk(_make_single_page("Short content."))
        assert len(result) == 1

    def test_single_chunk_contains_full_content(self):
        strategy = SlidingWindowChunkingStrategy(window_size=1000)
        result = strategy.chunk(_make_single_page("Short content."))
        assert "Short content." in result[0].content


class TestSlidingWindowChunking:
    def test_produces_multiple_chunks_for_long_content(self):
        strategy = SlidingWindowChunkingStrategy(window_size=10, overlap_ratio=0.0)
        result = strategy.chunk(_make_single_page("a" * 100))
        assert len(result) > 1

    def test_chunk_content_length_does_not_exceed_window_size(self):
        strategy = SlidingWindowChunkingStrategy(window_size=50, overlap_ratio=0.0)
        result = strategy.chunk(_make_single_page("x" * 200))
        for chunk in result:
            assert len(chunk.content) <= 50

    def test_overlap_repeats_content_between_consecutive_chunks(self):
        strategy = SlidingWindowChunkingStrategy(window_size=10, overlap_ratio=0.5)
        content = "abcdefghijklmnopqrstuvwxyz"
        result = strategy.chunk(_make_single_page(content))
        assert len(result) >= 2
        overlap = result[0].content[-5:]
        assert result[1].content.startswith(overlap)

    def test_no_overlap_chunks_cover_full_content(self):
        strategy = SlidingWindowChunkingStrategy(window_size=10, overlap_ratio=0.0)
        content = "abcdefghijklmnopqrst"
        result = strategy.chunk(_make_single_page(content))
        combined = "".join(c.content for c in result)
        assert "abcdefghij" in combined
        assert "klmnopqrst" in combined

    def test_strategy_name_recorded_on_chunks(self):
        strategy = SlidingWindowChunkingStrategy()
        result = strategy.chunk(_make_single_page("Some content."))
        for chunk in result:
            assert chunk.strategy == "SlidingWindowChunkingStrategy"

    def test_mime_type_propagated_to_chunks(self):
        strategy = SlidingWindowChunkingStrategy()
        result = strategy.chunk(_make_single_page("Some content.", mime_type=FileType.PDF))
        for chunk in result:
            assert chunk.mime_type == FileType.PDF


class TestSlidingWindowSplitter:
    def test_find_split_called_per_window(self):
        mock_splitter = MagicMock(spec=Splitter)
        mock_splitter.find_split.side_effect = lambda text, pos: pos
        strategy = SlidingWindowChunkingStrategy(
            window_size=10,
            overlap_ratio=0.0,
            splitter=mock_splitter,
        )
        strategy.chunk(_make_single_page("a" * 50))
        assert mock_splitter.find_split.call_count >= 1

    def test_custom_splitter_adjusts_cut_point(self):
        class ShortSplitter(Splitter):
            def find_split(self, text: str, position: int) -> int:
                return max(0, position - 2)

        strategy = SlidingWindowChunkingStrategy(
            window_size=10,
            overlap_ratio=0.0,
            splitter=ShortSplitter(),
        )
        result = strategy.chunk(_make_single_page("a" * 50))
        for chunk in result:
            assert len(chunk.content) <= 10


class TestSlidingWindowPageResolution:
    def test_single_page_chunk_has_correct_reference(self):
        strategy = SlidingWindowChunkingStrategy(window_size=1000)
        result = strategy.chunk(_make_single_page("Content on page one."))
        assert result[0].source_reference.page_start == 1
        assert result[0].source_reference.page_end == 1

    def test_chunk_within_page_2_has_correct_reference(self):
        strategy = SlidingWindowChunkingStrategy(window_size=1000)
        doc = _make_document([(1, "Page one."), (2, "Page two content here.")])
        result = strategy.chunk(doc)
        assert result[-1].source_reference.page_end == 2

    def test_chunk_spanning_two_pages_has_correct_start_and_end(self):
        page1_content = "A" * 20
        page2_content = "B" * 20
        strategy = SlidingWindowChunkingStrategy(window_size=30, overlap_ratio=0.0)
        doc = _make_document([(1, page1_content), (2, page2_content)])
        result = strategy.chunk(doc)
        spanning = [
            c for c in result
            if c.source_reference.page_start != c.source_reference.page_end
        ]
        assert len(spanning) >= 1
        assert spanning[0].source_reference.page_start == 1
        assert spanning[0].source_reference.page_end == 2

    def test_page_numbers_are_sequential_across_chunks(self):
        strategy = SlidingWindowChunkingStrategy(window_size=10, overlap_ratio=0.0)
        doc = _make_document([(1, "A" * 10), (2, "B" * 10), (3, "C" * 10)])
        result = strategy.chunk(doc)
        assert result[0].source_reference.page_start == 1
        assert result[-1].source_reference.page_end == 3