import pytest
from uuid import uuid4

from common.enums import FileType
from common.models import GlossaryEntry, ParsedDocument, ParsedPage
from libs.distiller.base import BaseDistillerStrategy
from libs.distiller.implementations.glossary import GlossaryDistillerStrategy
from libs.distiller.registry import (
    DistillerPriorityConflictError,
    DistillerRegistry,
    NoDistillerStrategyFoundError,
)


def _make_document(content: str = "some content") -> ParsedDocument:
    return ParsedDocument(
        mime_type=FileType.PDF,
        page_count=1,
        pages=[ParsedPage(page_number=1, content=content, strategy="PlainPdfExtractionStrategy")],
    )


class FakeStrategy(BaseDistillerStrategy):
    supported_mime_types = [FileType.PDF]

    def __init__(self, priority: int = 50, can_handle_result: bool = True):
        self._priority = priority
        self._can_handle_result = can_handle_result

    def can_handle(self, document: ParsedDocument) -> bool:
        return self._can_handle_result

    def get_priority(self) -> int:
        return self._priority

    def distill(self, document: ParsedDocument, document_id) -> list[GlossaryEntry]:
        return []


class TestDistillerRegistryStartupValidation:
    def test_raises_on_priority_conflict(self):
        s1 = FakeStrategy(priority=50)
        s2 = FakeStrategy(priority=50)
        with pytest.raises(DistillerPriorityConflictError):
            DistillerRegistry(strategies=[s1, s2])

    def test_no_conflict_different_priorities(self):
        s1 = FakeStrategy(priority=50)
        s2 = FakeStrategy(priority=60)
        DistillerRegistry(strategies=[s1, s2])

    def test_empty_registry_is_valid(self):
        DistillerRegistry(strategies=[])


class TestDistillerRegistryDispatch:
    def test_empty_document_returns_empty_list(self):
        registry = DistillerRegistry(strategies=[GlossaryDistillerStrategy()])
        doc = ParsedDocument(mime_type=FileType.PDF, page_count=0, pages=[])
        assert registry.distill(doc, uuid4()) == []

    def test_dispatches_to_glossary_strategy(self):
        registry = DistillerRegistry(strategies=[GlossaryDistillerStrategy()])
        result = registry.distill(_make_document(), uuid4())
        assert isinstance(result, list)

    def test_raises_when_no_strategy_matches(self):
        refuses = FakeStrategy(priority=50, can_handle_result=False)
        registry = DistillerRegistry(strategies=[refuses])
        with pytest.raises(NoDistillerStrategyFoundError):
            registry.distill(_make_document(), uuid4())