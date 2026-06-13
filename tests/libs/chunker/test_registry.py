import pytest

from libs.common.enums import FileType
from libs.common.models import DocumentChunk, ParsedDocument, ParsedPage, SourceReference
from libs.chunker.base import BaseChunkingStrategy
from libs.chunker.implementations.sliding_window import SlidingWindowChunkingStrategy
from libs.chunker.registry import (
    ChunkerPriorityConflictError,
    ChunkerRegistry,
    NoChunkingStrategyFoundError,
)


def _make_document(content: str = "Some content.", mime_type: FileType = FileType.PDF) -> ParsedDocument:
    return ParsedDocument(
        mime_type=mime_type,
        page_count=1,
        pages=[ParsedPage(page_number=1, content=content, strategy="PlainPdfExtractionStrategy")],
    )


class FakeStrategy(BaseChunkingStrategy):
    supported_mime_types = [FileType.PDF]

    def __init__(self, priority: int = 50, can_handle_result: bool = True):
        self._priority = priority
        self._can_handle_result = can_handle_result

    def can_handle(self, document: ParsedDocument) -> bool:
        return self._can_handle_result

    def get_priority(self) -> int:
        return self._priority

    def chunk(self, document: ParsedDocument) -> list[DocumentChunk]:
        return [DocumentChunk(
            content="fake chunk",
            source_reference=SourceReference(page_start=1, page_end=1),
            mime_type=document.mime_type,
            strategy=type(self).__name__,
        )]


class FakeHighPriorityStrategy(BaseChunkingStrategy):
    supported_mime_types = [FileType.PDF]

    def can_handle(self, document: ParsedDocument) -> bool:
        return True

    def get_priority(self) -> int:
        return 80

    def chunk(self, document: ParsedDocument) -> list[DocumentChunk]:
        return [DocumentChunk(
            content="high priority chunk",
            source_reference=SourceReference(page_start=1, page_end=1),
            mime_type=document.mime_type,
            strategy=type(self).__name__,
        )]


class TestChunkerRegistryStartupValidation:
    def test_raises_on_priority_conflict_same_mime(self):
        s1 = FakeStrategy(priority=50)
        s2 = FakeStrategy(priority=50)
        with pytest.raises(ChunkerPriorityConflictError) as exc_info:
            ChunkerRegistry(strategies=[s1, s2])
        assert "50" in str(exc_info.value)

    def test_no_conflict_different_priorities(self):
        s1 = FakeStrategy(priority=50)
        s2 = FakeStrategy(priority=60)
        ChunkerRegistry(strategies=[s1, s2])

    def test_conflict_between_sliding_window_and_same_priority(self):
        sliding = SlidingWindowChunkingStrategy()
        fake = FakeStrategy(priority=1)
        with pytest.raises(ChunkerPriorityConflictError):
            ChunkerRegistry(strategies=[sliding, fake])

    def test_empty_registry_is_valid(self):
        ChunkerRegistry(strategies=[])


class TestChunkerRegistryDispatch:
    def test_dispatches_to_sliding_window(self):
        registry = ChunkerRegistry(strategies=[SlidingWindowChunkingStrategy()])
        result = registry.chunk(_make_document("Hello world."))
        assert len(result) >= 1

    def test_dispatches_to_higher_priority_strategy(self):
        low = FakeStrategy(priority=50)
        high = FakeHighPriorityStrategy()
        registry = ChunkerRegistry(strategies=[SlidingWindowChunkingStrategy(), low, high])
        result = registry.chunk(_make_document())
        assert result[0].content == "high priority chunk"

    def test_skips_strategy_when_can_handle_returns_false(self):
        refuses = FakeStrategy(priority=50, can_handle_result=False)
        registry = ChunkerRegistry(strategies=[SlidingWindowChunkingStrategy(), refuses])
        result = registry.chunk(_make_document("Hello world."))
        assert result[0].strategy == "SlidingWindowChunkingStrategy"

    def test_raises_no_strategy_found_when_no_match(self):
        refuses = FakeStrategy(priority=50, can_handle_result=False)
        registry = ChunkerRegistry(strategies=[refuses])
        with pytest.raises(NoChunkingStrategyFoundError):
            registry.chunk(_make_document())

    def test_raises_no_strategy_found_for_unknown_mime_without_sliding_window(self):
        fake = FakeStrategy(priority=50)
        registry = ChunkerRegistry(strategies=[fake])
        with pytest.raises(NoChunkingStrategyFoundError):
            registry.chunk(_make_document(mime_type=FileType.UNKNOWN))