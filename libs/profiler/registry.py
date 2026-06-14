from common.enums import FileType
from common.models import DocumentProfile
from libs.profiler.detector.base import Detector
from libs.profiler.detector.implementations.default import DefaultDetector
from libs.profiler.base import BaseDocumentProfiler


class ProfilerPriorityConflictError(Exception):
    """Raised at startup when two registered profilers share the same priority for
    the same FileType. Indicates a misconfiguration that must be resolved before
    any documents are processed.
    """


class NoProfilerFoundError(Exception):
    """Raised at runtime when no registered profiler survives MIME filtering and
    can_handle inspection. Under normal operation this should never occur — it
    signals that DefaultProfiler was omitted from the registered profiler list.
    """


class ProfilerRegistry:
    """Dispatches raw file bytes to the highest-priority matching profiler.

    Accepts a list of profilers and a Detector as constructor arguments.
    Detector wiring is handled by the consuming project.

    Startup validation:
        Raises ProfilerPriorityConflictError if any two profilers share the
        same get_priority() value for the same FileType.

    Dispatch flow:
        1. Detect MIME via detector.detect_mime(file_bytes) → FileType
        2. Filter candidates to those whose supported_mime_types includes the FileType
        3. Call can_handle on each candidate
        4. Sort surviving candidates by get_priority() descending, dispatch to winner
    """

    def __init__(
        self,
        profilers: list[BaseDocumentProfiler],
        detector: Detector = None,
    ) -> None:
        self._profilers = profilers
        self._detector = detector or DefaultDetector()
        self._validate_priorities()

    def _validate_priorities(self) -> None:
        seen: dict[tuple[FileType, int], type[BaseDocumentProfiler]] = {}
        for profiler in self._profilers:
            priority = profiler.get_priority()
            for mime_type in profiler.supported_mime_types:
                key = (mime_type, priority)
                if key in seen:
                    raise ProfilerPriorityConflictError(
                        f"Priority conflict: {type(profiler).__name__} and "
                        f"{seen[key].__name__} both declare priority {priority} "
                        f"for {mime_type!r}."
                    )
                seen[key] = type(profiler)

    def profile(self, file_bytes: bytes) -> DocumentProfile:
        mime_type = self._detector.detect_mime(file_bytes)

        candidates = [
            p for p in self._profilers
            if mime_type in p.supported_mime_types
        ]

        survivors = [p for p in candidates if p.can_handle(file_bytes)]

        if not survivors:
            raise NoProfilerFoundError(
                f"No profiler found for MIME type {mime_type!r}. "
                "Ensure DefaultProfiler is registered."
            )

        winner = max(survivors, key=lambda p: p.get_priority())
        return winner.profile(file_bytes)