from libs.common.enums import FileType
from libs.common.models import DocumentChunk, ParsedDocument
from libs.chunker.base import BaseChunkingStrategy


class ChunkerPriorityConflictError(Exception):
    """Raised at startup when two registered strategies share the same priority
    for the same FileType. Indicates a misconfiguration that must be resolved
    before any documents are chunked.
    """


class NoChunkingStrategyFoundError(Exception):
    """Raised at runtime when no registered strategy survives MIME filtering
    and can_handle inspection. Under normal operation this should never occur
    — it signals that SlidingWindowChunkingStrategy was omitted from the
    registered strategy list.
    """


class ChunkerRegistry:
    """Dispatches a ParsedDocument to the highest-priority matching chunking strategy.

    Accepts a list of strategies as a constructor argument.

    Startup validation:
        Raises ChunkerPriorityConflictError if any two strategies share the
        same get_priority() value for the same FileType.

    Dispatch flow:
        1. Filter candidates to those whose supported_mime_types includes
           the document's FileType
        2. Call can_handle(document) on each candidate
        3. Sort surviving candidates by get_priority() descending, dispatch
           to the winner
    """

    def __init__(self, strategies: list[BaseChunkingStrategy]) -> None:
        self._strategies = strategies
        self._validate_priorities()

    def _validate_priorities(self) -> None:
        seen: dict[tuple[FileType, int], type[BaseChunkingStrategy]] = {}
        for strategy in self._strategies:
            priority = strategy.get_priority()
            for mime_type in strategy.supported_mime_types:
                key = (mime_type, priority)
                if key in seen:
                    raise ChunkerPriorityConflictError(
                        f"Priority conflict: {type(strategy).__name__} and "
                        f"{seen[key].__name__} both declare priority {priority} "
                        f"for {mime_type!r}."
                    )
                seen[key] = type(strategy)

    def chunk(self, document: ParsedDocument) -> list[DocumentChunk]:
        candidates = [
            s for s in self._strategies
            if document.mime_type in s.supported_mime_types
        ]

        survivors = [s for s in candidates if s.can_handle(document)]

        if not survivors:
            raise NoChunkingStrategyFoundError(
                f"No chunking strategy found for mime_type={document.mime_type!r}. "
                "Ensure SlidingWindowChunkingStrategy is registered."
            )

        winner = max(survivors, key=lambda s: s.get_priority())
        return winner.chunk(document)