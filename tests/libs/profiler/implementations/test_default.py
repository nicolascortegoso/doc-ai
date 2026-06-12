import pytest

from libs.profiler.enums import FileType
from libs.profiler.implementations.default import DefaultProfiler


class TestDefaultProfiler:
    def setup_method(self):
        self.profiler = DefaultProfiler()

    # supported_mime_types
    def test_supported_mime_types_covers_all_file_types(self):
        for file_type in FileType:
            assert file_type in self.profiler.supported_mime_types

    def test_supported_mime_types_includes_unknown(self):
        assert FileType.UNKNOWN in self.profiler.supported_mime_types

    # can_handle
    def test_can_handle_returns_true_for_any_bytes(self):
        assert self.profiler.can_handle(b"") is True
        assert self.profiler.can_handle(b"\x00\x01\x02") is True
        assert self.profiler.can_handle(b"%PDF-1.4") is True

    # get_priority
    def test_get_priority_returns_1(self):
        assert self.profiler.get_priority() == 1

    # profile
    def test_profile_returns_unknown_mime(self):
        result = self.profiler.profile(b"anything")
        assert result.mime_type == FileType.UNKNOWN

    def test_profile_returns_zero_page_count(self):
        result = self.profiler.profile(b"anything")
        assert result.page_count == 0

    def test_profile_returns_empty_pages(self):
        result = self.profiler.profile(b"anything")
        assert result.pages == []

    def test_profile_result_is_consistent_across_calls(self):
        r1 = self.profiler.profile(b"pdf bytes")
        r2 = self.profiler.profile(b"different bytes")
        assert r1.mime_type == r2.mime_type
        assert r1.page_count == r2.page_count
        assert r1.pages == r2.pages
