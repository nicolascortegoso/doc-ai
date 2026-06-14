import pytest

from common.enums import FileType, Layout
from common.models import PageProfile
from libs.parser.implementations.default import DefaultPageExtractionStrategy


@pytest.fixture
def strategy() -> DefaultPageExtractionStrategy:
    return DefaultPageExtractionStrategy()


@pytest.fixture
def page_profile() -> PageProfile:
    return PageProfile(
        page_number=1,
        has_text=True,
        has_images=False,
        has_tables=False,
        is_scanned=False,
        layout=Layout.SINGLE_COLUMN,
        language="en",
    )


class TestDefaultPageExtractionStrategy:
    def test_supported_mime_types_covers_all_file_types(self, strategy):
        for file_type in FileType:
            assert file_type in strategy.supported_mime_types

    def test_supported_mime_types_includes_unknown(self, strategy):
        assert FileType.UNKNOWN in strategy.supported_mime_types

    def test_can_handle_always_returns_true(self, strategy, page_profile):
        assert strategy.can_handle(page_profile) is True

    def test_can_handle_returns_true_for_scanned_page(self, strategy):
        scanned = PageProfile(
            page_number=1,
            has_text=False,
            has_images=True,
            has_tables=False,
            is_scanned=True,
            layout=Layout.UNKNOWN,
            language=None,
        )
        assert strategy.can_handle(scanned) is True

    def test_get_priority_returns_1(self, strategy):
        assert strategy.get_priority() == 1

    def test_extract_returns_empty_string(self, strategy, page_profile):
        assert strategy.extract(b"any bytes", page_profile) == ""

    def test_extract_returns_empty_string_for_any_input(self, strategy, page_profile):
        assert strategy.extract(b"", page_profile) == ""
        assert strategy.extract(b"\x00\x01\x02", page_profile) == ""