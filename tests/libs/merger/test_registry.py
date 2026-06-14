import pytest

from common.enums import FileType
from common.models import DocumentChunk, DocumentTree, SourceReference, TreeNode
from libs.merger.base import BaseMergingStrategy
from libs.merger.implementations.bottom_up import BottomUpMergingStrategy
from libs.merger.registry import (
    MergerPriorityConflictError,
    MergerRegistry,
    NoMergingStrategyFoundError,
)


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


class FakeStrategy(BaseMergingStrategy):
    supported_mime_types = [FileType.PDF]

    def __init__(self, priority: int = 50, can_handle_result: bool = True):
        self._priority = priority
        self._can_handle_result = can_handle_result

    def can_handle(self, chunks: list[DocumentChunk]) -> bool:
        return self._can_handle_result

    def get_priority(self) -> int:
        return self._priority

    def merge(self, chunks: list[DocumentChunk]) -> DocumentTree:
        node = TreeNode(content="fake", level=0, chunk=chunks[0])
        return DocumentTree(root=node, mime_type=chunks[0].mime_type)


class FakeHighPriorityStrategy(BaseMergingStrategy):
    supported_mime_types = [FileType.PDF]

    def can_handle(self, chunks: list[DocumentChunk]) -> bool:
        return True

    def get_priority(self) -> int:
        return 80

    def merge(self, chunks: list[DocumentChunk]) -> DocumentTree:
        node = TreeNode(content="high priority", level=0, chunk=chunks[0])
        return DocumentTree(root=node, mime_type=chunks[0].mime_type)


class TestMergerRegistryStartupValidation:
    def test_raises_on_priority_conflict_same_mime(self):
        s1 = FakeStrategy(priority=50)
        s2 = FakeStrategy(priority=50)
        with pytest.raises(MergerPriorityConflictError) as exc_info:
            MergerRegistry(strategies=[s1, s2])
        assert "50" in str(exc_info.value)

    def test_no_conflict_different_priorities(self):
        s1 = FakeStrategy(priority=50)
        s2 = FakeStrategy(priority=60)
        MergerRegistry(strategies=[s1, s2])

    def test_conflict_between_bottom_up_and_same_priority(self):
        bottom_up = BottomUpMergingStrategy()
        fake = FakeStrategy(priority=1)
        with pytest.raises(MergerPriorityConflictError):
            MergerRegistry(strategies=[bottom_up, fake])

    def test_empty_registry_is_valid(self):
        MergerRegistry(strategies=[])


class TestMergerRegistryDispatch:
    def test_dispatches_to_bottom_up(self):
        registry = MergerRegistry(strategies=[BottomUpMergingStrategy()])
        result = registry.merge([_make_chunk()])
        assert isinstance(result, DocumentTree)

    def test_dispatches_to_higher_priority_strategy(self):
        low = FakeStrategy(priority=50)
        high = FakeHighPriorityStrategy()
        registry = MergerRegistry(strategies=[BottomUpMergingStrategy(), low, high])
        result = registry.merge([_make_chunk()])
        assert result.root.content == "high priority"

    def test_skips_strategy_when_can_handle_returns_false(self):
        refuses = FakeStrategy(priority=50, can_handle_result=False)
        registry = MergerRegistry(strategies=[BottomUpMergingStrategy(), refuses])
        result = registry.merge([_make_chunk()])
        assert isinstance(result, DocumentTree)

    def test_raises_no_strategy_found_when_no_match(self):
        refuses = FakeStrategy(priority=50, can_handle_result=False)
        registry = MergerRegistry(strategies=[refuses])
        with pytest.raises(NoMergingStrategyFoundError):
            registry.merge([_make_chunk()])

    def test_raises_no_strategy_found_for_unknown_mime_without_bottom_up(self):
        fake = FakeStrategy(priority=50)
        registry = MergerRegistry(strategies=[fake])
        with pytest.raises(NoMergingStrategyFoundError):
            registry.merge([_make_chunk(mime_type=FileType.UNKNOWN)])

    def test_raises_when_no_chunks_provided(self):
        registry = MergerRegistry(strategies=[BottomUpMergingStrategy()])
        with pytest.raises(NoMergingStrategyFoundError):
            registry.merge([])