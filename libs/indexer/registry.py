from libs.common.enums import FileType
from libs.common.models import DocumentChunk, IndexedChunk
from libs.indexer.base import BaseIndexingStrategy


class IndexerPriorityConflictError(Exception):
    """Raised at startup when two registered strategies share the same priority
    for the same FileType. Indicates a misconfiguration that must be resolved
    before any chunks are indexed.
    """


class NoIndexingStrategyFoundError(Exception):
    """Raised at runtime when no registered strategy survives MIME filtering
    and can_handle inspection. Under normal operation this should never occur
    — it signals that BatchIndexer was omitted from the registered strategy list.
    """


class IndexerRegistry:
    """Dispatches a list of DocumentChunks to the highest-priority matching
    indexing strategy.

    Accepts a list of strategies as a constructor argument.

    Startup validation:
        Raises IndexerPriorityConflictError if any two strategies share the
        same get_priority() value for the same FileType.

    Dispatch flow:
        1. Filter candidates to those whose supported_mime_types includes
           the chunks' FileType
        2. Call can_handle(chunks) on each candidate
        3. Sort surviving candidates by get_priority() descending, dispatch
           to the winner
    """

    def __init__(self, strategies: list[BaseIndexingStrategy]) -> None:
        self._strategies = strategies
        self._validate_priorities()

    def _validate_priorities(self) -> None:
        seen: dict[tuple[FileType, int], type[BaseIndexingStrategy]] = {}
        for strategy in self._strategies:
            priority = strategy.get_priority()
            for mime_type in strategy.supported_mime_types:
                key = (mime_type, priority)
                if key in seen:
                    raise IndexerPriorityConflictError(
                        f"Priority conflict: {type(strategy).__name__} and "
                        f"{seen[key].__name__} both declare priority {priority} "
                        f"for {mime_type!r}."
                    )
                seen[key] = type(strategy)

    def index(self, chunks: list[DocumentChunk]) -> list[IndexedChunk]:
        if not chunks:
            return []

        mime_type = chunks[0].mime_type

        candidates = [
            s for s in self._strategies
            if mime_type in s.supported_mime_types
        ]

        survivors = [s for s in candidates if s.can_handle(chunks)]

        if not survivors:
            raise NoIndexingStrategyFoundError(
                f"No indexing strategy found for mime_type={mime_type!r}. "
                "Ensure BatchIndexer is registered."
            )

        winner = max(survivors, key=lambda s: s.get_priority())
        return winner.index(chunks)