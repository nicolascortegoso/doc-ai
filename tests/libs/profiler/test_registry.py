import pytest

from libs.profiler.base import BaseDocumentProfiler
from common.enums import FileType
from common.models import DocumentProfile
from libs.profiler.registry import (
    NoProfilerFoundError,
    ProfilerPriorityConflictError,
    ProfilerRegistry,
)
from libs.profiler.implementations.default import DefaultProfiler


# ---------------------------------------------------------------------------
# Fakes
# ---------------------------------------------------------------------------

class FakePdfProfiler(BaseDocumentProfiler):
    supported_mime_types = [FileType.PDF]

    def __init__(self, priority: int = 50, can_handle_result: bool = True):
        self._priority = priority
        self._can_handle_result = can_handle_result

    def can_handle(self, file_bytes: bytes) -> bool:
        return self._can_handle_result

    def get_priority(self) -> int:
        return self._priority

    def profile(self, file_bytes: bytes) -> DocumentProfile:
        return DocumentProfile(mime_type=FileType.PDF, page_count=3, pages=[])


class FakeHighPriorityPdfProfiler(BaseDocumentProfiler):
    supported_mime_types = [FileType.PDF]

    def can_handle(self, file_bytes: bytes) -> bool:
        return True

    def get_priority(self) -> int:
        return 80

    def profile(self, file_bytes: bytes) -> DocumentProfile:
        return DocumentProfile(mime_type=FileType.PDF, page_count=99, pages=[])


# Minimal PDF bytes for magic detection
PDF_BYTES = b"%PDF-1.4\n%%EOF"


# ---------------------------------------------------------------------------
# Startup: priority conflict detection
# ---------------------------------------------------------------------------

class TestRegistryStartupValidation:
    def test_raises_on_priority_conflict_same_mime(self):
        p1 = FakePdfProfiler(priority=50)
        p2 = FakePdfProfiler(priority=50)
        with pytest.raises(ProfilerPriorityConflictError) as exc_info:
            ProfilerRegistry(profilers=[p1, p2])
        assert "50" in str(exc_info.value)
        assert "PDF" in str(exc_info.value) or "pdf" in str(exc_info.value).lower()

    def test_no_conflict_different_priorities(self):
        p1 = FakePdfProfiler(priority=50)
        p2 = FakePdfProfiler(priority=60)
        # Should not raise
        ProfilerRegistry(profilers=[p1, p2])

    def test_no_conflict_different_mime_same_priority(self):
        # DefaultProfiler (priority=1) + a profiler for PDF only at priority=1
        # DefaultProfiler covers all types including PDF — this should raise
        default = DefaultProfiler()
        pdf = FakePdfProfiler(priority=1)
        with pytest.raises(ProfilerPriorityConflictError):
            ProfilerRegistry(profilers=[default, pdf])

    def test_empty_registry_is_valid(self):
        # No profilers — valid at startup, will raise at dispatch
        ProfilerRegistry(profilers=[])


# ---------------------------------------------------------------------------
# Dispatch: MIME filtering + can_handle + priority resolution
# ---------------------------------------------------------------------------

class TestRegistryDispatch:
    def test_dispatches_to_default_profiler_for_unknown(self):
        registry = ProfilerRegistry(profilers=[DefaultProfiler()])
        result = registry.profile(b"\x00\x01garbage")
        assert result.mime_type == FileType.UNKNOWN
        assert result.page_count == 0

    def test_dispatches_to_default_profiler_for_pdf_when_only_default_registered(self):
        registry = ProfilerRegistry(profilers=[DefaultProfiler()])
        result = registry.profile(PDF_BYTES)
        # DefaultProfiler returns UNKNOWN regardless of actual MIME
        assert result.mime_type == FileType.UNKNOWN

    def test_dispatches_to_higher_priority_profiler(self):
        low = FakePdfProfiler(priority=50)
        high = FakeHighPriorityPdfProfiler()  # priority=80
        registry = ProfilerRegistry(profilers=[DefaultProfiler(), low, high])
        result = registry.profile(PDF_BYTES)
        assert result.page_count == 99  # high priority profiler result

    def test_skips_profiler_when_can_handle_returns_false(self):
        refuses = FakePdfProfiler(priority=50, can_handle_result=False)
        accepts = FakePdfProfiler(priority=40, can_handle_result=True)
        registry = ProfilerRegistry(profilers=[DefaultProfiler(), refuses, accepts])
        result = registry.profile(PDF_BYTES)
        assert result.page_count == 3  # accepts profiler result

    def test_falls_back_to_default_when_all_specific_profilers_refuse(self):
        refuses = FakePdfProfiler(priority=50, can_handle_result=False)
        registry = ProfilerRegistry(profilers=[DefaultProfiler(), refuses])
        result = registry.profile(PDF_BYTES)
        assert result.mime_type == FileType.UNKNOWN  # DefaultProfiler took over

    def test_raises_no_profiler_found_when_default_omitted(self):
        pdf_profiler = FakePdfProfiler(priority=50, can_handle_result=False)
        registry = ProfilerRegistry(profilers=[pdf_profiler])
        with pytest.raises(NoProfilerFoundError):
            registry.profile(PDF_BYTES)

    def test_raises_no_profiler_found_for_unknown_mime_without_default(self):
        pdf_profiler = FakePdfProfiler(priority=50)
        registry = ProfilerRegistry(profilers=[pdf_profiler])
        with pytest.raises(NoProfilerFoundError):
            registry.profile(b"\x00\x01garbage")
