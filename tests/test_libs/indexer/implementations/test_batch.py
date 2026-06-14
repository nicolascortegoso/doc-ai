from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from common.enums import FileType
from common.models import DocumentChunk, IndexedChunk, SourceReference
from libs.indexer.embedder.base import Embedder
from libs.indexer.embedder.implementations.random import RandomEmbedder
from libs.indexer.implementations.batch import BatchIndexer


def _make_chunk(content: str = "test content", mime_type: FileType = FileType.PDF) -> DocumentChunk:
    return DocumentChunk(
        content=content,
        source_reference=SourceReference(page_start=1, page_end=1),
        mime_type=mime_type,
        strategy="PlainPdfExtractionStrategy",
    )


def _make_chunks(n: int) -> list[DocumentChunk]:
    return [_make_chunk(content=f"chunk {i}") for i in range(n)]


@pytest.fixture
def indexer() -> BatchIndexer:
    return BatchIndexer()


class TestBatchIndexerMetadata:
    def test_supported_mime_types_covers_all_file_types(self, indexer):
        for file_type in FileType:
            assert file_type in indexer.supported_mime_types

    def test_get_priority_returns_1(self, indexer):
        assert indexer.get_priority() == 1

    def test_can_handle_always_returns_true(self, indexer):
        assert indexer.can_handle(_make_chunks(3)) is True


class TestBatchIndexerConstruction:
    def test_default_batch_size_is_32(self, indexer):
        assert indexer._batch_size == 32

    def test_custom_batch_size(self):
        assert BatchIndexer(batch_size=16)._batch_size == 16

    def test_raises_on_zero_batch_size(self):
        with pytest.raises(ValueError):
            BatchIndexer(batch_size=0)

    def test_default_embedder_is_random(self, indexer):
        assert isinstance(indexer._embedder, RandomEmbedder)

    def test_custom_embedder_is_used(self):
        mock_embedder = MagicMock(spec=Embedder)
        indexer = BatchIndexer(embedder=mock_embedder)
        assert indexer._embedder is mock_embedder


class TestBatchIndexerIndex:
    def test_empty_chunks_returns_empty_list(self, indexer):
        assert indexer.index([]) == []

    def test_returns_one_indexed_chunk_per_input(self, indexer):
        chunks = _make_chunks(5)
        result = indexer.index(chunks)
        assert len(result) == 5

    def test_chunk_preserved_in_indexed_chunk(self, indexer):
        chunk = _make_chunk(content="specific content")
        result = indexer.index([chunk])
        assert result[0].chunk is chunk

    def test_embedding_has_correct_dimension(self, indexer):
        result = indexer.index([_make_chunk()])
        assert len(result[0].embedding) == indexer._embedder.dimension

    def test_embed_batch_called_per_batch(self):
        mock_embedder = MagicMock(spec=Embedder)
        mock_embedder.embed_batch.return_value = [[0.1, 0.2]] * 3
        mock_embedder.dimension = 2
        indexer = BatchIndexer(batch_size=3, embedder=mock_embedder)
        indexer.index(_make_chunks(6))
        assert mock_embedder.embed_batch.call_count == 2

    def test_last_batch_smaller_than_batch_size(self):
        mock_embedder = MagicMock(spec=Embedder)
        mock_embedder.embed_batch.side_effect = lambda texts: [[0.1]] * len(texts)
        mock_embedder.dimension = 1
        indexer = BatchIndexer(batch_size=4, embedder=mock_embedder)
        result = indexer.index(_make_chunks(5))
        assert len(result) == 5

    def test_embed_batch_receives_chunk_content(self):
        mock_embedder = MagicMock(spec=Embedder)
        mock_embedder.embed_batch.return_value = [[0.1, 0.2]]
        mock_embedder.dimension = 2
        indexer = BatchIndexer(embedder=mock_embedder)
        chunk = _make_chunk(content="hello world")
        indexer.index([chunk])
        call_texts = mock_embedder.embed_batch.call_args[0][0]
        assert "hello world" in call_texts