from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from common.enums import FileType
from common.models import DocumentChunk, SourceReference, TreeNode
from libs.merger.implementations.bottom_up import BottomUpMergingStrategy
from libs.merger.reducer.base import Reducer
from libs.merger.reducer.implementations.truncating import TruncatingReducer
from libs.merger.reducer.models import ReducerInput


def _make_chunk(
    content: str = "chunk content",
    page: int = 1,
    mime_type: FileType = FileType.PDF,
) -> DocumentChunk:
    return DocumentChunk(
        content=content,
        source_reference=SourceReference(page_start=page, page_end=page),
        mime_type=mime_type,
        strategy="PlainPdfExtractionStrategy",
    )


def _make_chunks(n: int, mime_type: FileType = FileType.PDF) -> list[DocumentChunk]:
    return [_make_chunk(content=f"chunk {i}", page=i, mime_type=mime_type) for i in range(1, n + 1)]


class TestBottomUpMetadata:
    def test_supported_mime_types_covers_all_file_types(self):
        strategy = BottomUpMergingStrategy()
        for file_type in FileType:
            assert file_type in strategy.supported_mime_types

    def test_get_priority_returns_1(self):
        assert BottomUpMergingStrategy().get_priority() == 1

    def test_can_handle_always_returns_true(self):
        strategy = BottomUpMergingStrategy()
        assert strategy.can_handle(_make_chunks(3)) is True


class TestBottomUpConstruction:
    def test_default_branching_factor_is_4(self):
        assert BottomUpMergingStrategy()._branching_factor == 4

    def test_custom_branching_factor(self):
        assert BottomUpMergingStrategy(branching_factor=2)._branching_factor == 2

    def test_raises_on_branching_factor_less_than_2(self):
        with pytest.raises(ValueError):
            BottomUpMergingStrategy(branching_factor=1)

    def test_default_reducer_is_truncating(self):
        strategy = BottomUpMergingStrategy()
        assert isinstance(strategy._reducer, TruncatingReducer)

    def test_custom_reducer_is_used(self):
        mock_reducer = MagicMock(spec=Reducer)
        strategy = BottomUpMergingStrategy(reducer=mock_reducer)
        assert strategy._reducer is mock_reducer


class TestBottomUpTreeStructure:
    def test_single_chunk_produces_leaf_root(self):
        strategy = BottomUpMergingStrategy()
        result = strategy.merge([_make_chunk()])
        assert result.root.level == 0
        assert result.root.chunk is not None
        assert result.root.children == []

    def test_single_chunk_root_content_matches_chunk(self):
        strategy = BottomUpMergingStrategy()
        chunk = _make_chunk(content="hello world")
        result = strategy.merge([chunk])
        assert result.root.content == "hello world"

    def test_multiple_chunks_produces_root_at_level_1(self):
        strategy = BottomUpMergingStrategy(branching_factor=4)
        result = strategy.merge(_make_chunks(4))
        assert result.root.level == 1

    def test_many_chunks_produces_multilevel_tree(self):
        strategy = BottomUpMergingStrategy(branching_factor=2)
        result = strategy.merge(_make_chunks(8))
        assert result.root.level == 3

    def test_leaf_nodes_carry_chunks(self):
        strategy = BottomUpMergingStrategy(branching_factor=4)
        chunks = _make_chunks(4)
        result = strategy.merge(chunks)
        leaves = result.root.children
        for leaf in leaves:
            assert leaf.chunk is not None
            assert leaf.level == 0

    def test_internal_nodes_have_no_chunk(self):
        strategy = BottomUpMergingStrategy(branching_factor=2)
        result = strategy.merge(_make_chunks(4))
        assert result.root.chunk is None
        for child in result.root.children:
            assert child.chunk is None

    def test_mime_type_propagated_to_tree(self):
        strategy = BottomUpMergingStrategy()
        result = strategy.merge(_make_chunks(2, mime_type=FileType.PDF))
        assert result.mime_type == FileType.PDF

    def test_last_batch_smaller_than_branching_factor(self):
        strategy = BottomUpMergingStrategy(branching_factor=4)
        result = strategy.merge(_make_chunks(5))
        assert result.root.level == 2
        assert len(result.root.children) == 2


class TestBottomUpSourceReference:
    def test_leaf_source_reference_matches_chunk(self):
        strategy = BottomUpMergingStrategy()
        chunk = _make_chunk(page=3)
        result = strategy.merge([chunk])
        assert result.root.source_reference.page_start == 3
        assert result.root.source_reference.page_end == 3

    def test_internal_node_spans_children(self):
        strategy = BottomUpMergingStrategy(branching_factor=4)
        chunks = [_make_chunk(page=i) for i in range(1, 5)]
        result = strategy.merge(chunks)
        assert result.root.source_reference.page_start == 1
        assert result.root.source_reference.page_end == 4


class TestBottomUpReducer:
    def test_reducer_called_at_each_merge_level(self):
        mock_reducer = MagicMock(spec=Reducer)
        mock_reducer.reduce.return_value = "reduced"
        strategy = BottomUpMergingStrategy(branching_factor=2, reducer=mock_reducer)
        strategy.merge(_make_chunks(4))
        assert mock_reducer.reduce.call_count == 3

    def test_reducer_receives_texts_from_chunks(self):
        mock_reducer = MagicMock(spec=Reducer)
        mock_reducer.reduce.return_value = "reduced"
        strategy = BottomUpMergingStrategy(branching_factor=2, reducer=mock_reducer)
        chunks = [_make_chunk(content="text A"), _make_chunk(content="text B")]
        strategy.merge(chunks)
        call_input: ReducerInput = mock_reducer.reduce.call_args[0][0]
        assert "text A" in call_input.texts
        assert "text B" in call_input.texts

    def test_reducer_output_used_as_parent_content(self):
        mock_reducer = MagicMock(spec=Reducer)
        mock_reducer.reduce.return_value = "synthesized content"
        strategy = BottomUpMergingStrategy(branching_factor=2, reducer=mock_reducer)
        result = strategy.merge(_make_chunks(2))
        assert result.root.content == "synthesized content"