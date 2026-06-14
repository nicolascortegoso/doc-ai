import pytest

from common.enums import FileType, Layout
from common.models import DocumentProfile, PageProfile
from libs.parser.base import BasePageExtractionStrategy
from libs.parser.implementations.default import DefaultPageExtractionStrategy
from libs.parser.registry import (
    NoStrategyFoundError,
    ParserPriorityConflictError,
    ParserRegistry,
)


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


def _make_profile(pages: list[PageProfile] | None = None) -> DocumentProfile:
    pages = pages or [_make_page_profile()]
    return DocumentProfile(
        mime_type=FileType.PDF,
        page_count=len(pages),
        pages=pages,
    )


class FakePdfStrategy(BasePageExtractionStrategy):
    supported_mime_types = [FileType.PDF]

    def __init__(self, priority: int = 50, can_handle_result: bool = True, content: str = "extracted"):
        self._priority = priority
        self._can_handle_result = can_handle_result
        self._content = content

    def can_handle(self, page_profile: PageProfile) -> bool:
        return self._can_handle_result

    def get_priority(self) -> int:
        return self._priority

    def extract(self, file_bytes: bytes, page_profile: PageProfile) -> str:
        return self._content


class FakeHighPriorityPdfStrategy(BasePageExtractionStrategy):
    supported_mime_types = [FileType.PDF]

    def can_handle(self, page_profile: PageProfile) -> bool:
        return True

    def get_priority(self) -> int:
        return 80

    def extract(self, file_bytes: bytes, page_profile: PageProfile) -> str:
        return "high priority content"


class TestParserRegistryStartupValidation:
    def test_raises_on_priority_conflict_same_mime(self):
        s1 = FakePdfStrategy(priority=50)
        s2 = FakePdfStrategy(priority=50)
        with pytest.raises(ParserPriorityConflictError) as exc_info:
            ParserRegistry(strategies=[s1, s2])
        assert "50" in str(exc_info.value)

    def test_no_conflict_different_priorities(self):
        s1 = FakePdfStrategy(priority=50)
        s2 = FakePdfStrategy(priority=60)
        ParserRegistry(strategies=[s1, s2])

    def test_no_conflict_different_mime_same_priority(self):
        default = DefaultPageExtractionStrategy()
        pdf = FakePdfStrategy(priority=1)
        with pytest.raises(ParserPriorityConflictError):
            ParserRegistry(strategies=[default, pdf])

    def test_empty_registry_is_valid(self):
        ParserRegistry(strategies=[])


class TestParserRegistryDispatch:
    def test_returns_parsed_document_with_correct_mime(self):
        registry = ParserRegistry(strategies=[DefaultPageExtractionStrategy()])
        result = registry.parse(b"", _make_profile())
        assert result.mime_type == FileType.PDF

    def test_returns_parsed_document_with_correct_page_count(self):
        registry = ParserRegistry(strategies=[DefaultPageExtractionStrategy()])
        result = registry.parse(b"", _make_profile())
        assert result.page_count == 1

    def test_dispatches_to_higher_priority_strategy(self):
        low = FakePdfStrategy(priority=50, content="low")
        high = FakeHighPriorityPdfStrategy()
        registry = ParserRegistry(strategies=[DefaultPageExtractionStrategy(), low, high])
        result = registry.parse(b"", _make_profile())
        assert result.pages[0].content == "high priority content"

    def test_skips_strategy_when_can_handle_returns_false(self):
        refuses = FakePdfStrategy(priority=50, can_handle_result=False, content="refused")
        accepts = FakePdfStrategy(priority=40, can_handle_result=True, content="accepted")
        registry = ParserRegistry(strategies=[DefaultPageExtractionStrategy(), refuses, accepts])
        result = registry.parse(b"", _make_profile())
        assert result.pages[0].content == "accepted"

    def test_falls_back_to_default_when_all_specific_strategies_refuse(self):
        refuses = FakePdfStrategy(priority=50, can_handle_result=False)
        registry = ParserRegistry(strategies=[DefaultPageExtractionStrategy(), refuses])
        result = registry.parse(b"", _make_profile())
        assert result.pages[0].content == ""
        assert result.pages[0].strategy == "DefaultPageExtractionStrategy"

    def test_raises_no_strategy_found_when_default_omitted(self):
        refuses = FakePdfStrategy(priority=50, can_handle_result=False)
        registry = ParserRegistry(strategies=[refuses])
        with pytest.raises(NoStrategyFoundError):
            registry.parse(b"", _make_profile())

    def test_strategy_name_recorded_on_parsed_page(self):
        registry = ParserRegistry(strategies=[DefaultPageExtractionStrategy()])
        result = registry.parse(b"", _make_profile())
        assert result.pages[0].strategy == "DefaultPageExtractionStrategy"

    def test_page_number_preserved_on_parsed_page(self):
        registry = ParserRegistry(strategies=[DefaultPageExtractionStrategy()])
        result = registry.parse(b"", _make_profile())
        assert result.pages[0].page_number == 1

    def test_multipage_document_produces_one_parsed_page_per_profile_page(self):
        pages = [_make_page_profile(i) for i in range(1, 4)]
        registry = ParserRegistry(strategies=[DefaultPageExtractionStrategy()])
        result = registry.parse(b"", _make_profile(pages))
        assert len(result.pages) == 3
        assert [p.page_number for p in result.pages] == [1, 2, 3]