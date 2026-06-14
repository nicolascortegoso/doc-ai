import pytest

from common.enums import FileType
from common.models import DocumentChunk, IndexedChunk, SourceReference
from libs.indexer.base import BaseIndexingStrategy
from libs.indexer.implementations.batch import BatchIndexer
from libs.indexer.registry import (
    IndexerPriorityConflictError,
    IndexerRegistry,
    NoIndexingStrategyFoundError,
)


def _make_chunk(mime_type: FileType = FileType.PDF) -> DocumentChunk:
    return DocumentChunk(
        content="test content",
        source_reference=SourceReference(page_start=1, page_end=1),
        mime_type=mime_type,
        strategy="PlainPdfExtractionStrategy",
    )


class FakeStrategy(BaseIndexingStrategy):
    supported_mime_types = [FileType.PDF]

    def __init__(self, priority: int = 50, can_handle_result: bool = True):
        self._priority = priority
        self._can_handle_result = can_handle_result

    def can_handle(self, chunks: list[DocumentChunk]) -> bool:
        return self._can_handle_result

    def get_priority(self) -> int:
        return self._priority

    def index(self, chunks: list[DocumentChunk]) -> list[IndexedChunk]:
        return [IndexedChunk(chunk=c, embedding=[0.0]) for c in chunks]


class FakeHighPriorityStrategy(BaseIndexingStrategy):
    supported_mime_types = [FileType.PDF]

    def can_handle(self, chunks: list[DocumentChunk]) -> bool:
        return True

    def get_priority(self) -> int:
        return 80

    def index(self, chunks: list[DocumentChunk]) -> list[IndexedChunk]:
        return [IndexedChunk(chunk=c, embedding=[1.0]) for c in chunks]


class TestIndexerRegistryStartupValidation:
    def test_raises_on_priority_conflict_same_mime(self):
        s1 = FakeStrategy(priority=50)
        s2 = FakeStrategy(priority=50)
        with pytest.raises(IndexerPriorityConflictError) as exc_info:
            IndexerRegistry(strategies=[s1, s2])
        assert "50" in str(exc_info.value)

    def test_no_conflict_different_priorities(self):
        s1 = FakeStrategy(priority=50)
        s2 = FakeStrategy(priority=60)
        IndexerRegistry(strategies=[s1, s2])

    def test_conflict_between_batch_indexer_and_same_priority(self):
        batch = BatchIndexer()
        fake = FakeStrategy(priority=1)
        with pytest.raises(IndexerPriorityConflictError):
            IndexerRegistry(strategies=[batch, fake])

    def test_empty_registry_is_valid(self):
        IndexerRegistry(strategies=[])


class TestIndexerRegistryDispatch:
    def test_empty_chunks_returns_empty_list(self):
        registry = IndexerRegistry(strategies=[BatchIndexer()])
        assert registry.index([]) == []

    def test_dispatches_to_batch_indexer(self):
        registry = IndexerRegistry(strategies=[BatchIndexer()])
        result = registry.index([_make_chunk()])
        assert len(result) == 1

    def test_dispatches_to_higher_priority_strategy(self):
        low = FakeStrategy(priority=50)
        high = FakeHighPriorityStrategy()
        registry = IndexerRegistry(strategies=[BatchIndexer(), low, high])
        result = registry.index([_make_chunk()])
        assert result[0].embedding == [1.0]

    def test_skips_strategy_when_can_handle_returns_false(self):
        refuses = FakeStrategy(priority=50, can_handle_result=False)
        registry = IndexerRegistry(strategies=[BatchIndexer(), refuses])
        result = registry.index([_make_chunk()])
        assert len(result) == 1

    def test_raises_no_strategy_found_when_no_match(self):
        refuses = FakeStrategy(priority=50, can_handle_result=False)
        registry = IndexerRegistry(strategies=[refuses])
        with pytest.raises(NoIndexingStrategyFoundError):
            registry.index([_make_chunk()])

    def test_raises_no_strategy_found_for_unknown_mime(self):
        fake = FakeStrategy(priority=50)
        registry = IndexerRegistry(strategies=[fake])
        with pytest.raises(NoIndexingStrategyFoundError):
            registry.index([_make_chunk(mime_type=FileType.UNKNOWN)])