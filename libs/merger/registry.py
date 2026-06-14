from common.enums import FileType
from common.models import DocumentChunk, DocumentTree
from libs.merger.base import BaseMergingStrategy


class MergerPriorityConflictError(Exception):
    """Raised at startup when two registered strategies share the same priority
    for the same FileType. Indicates a misconfiguration that must be resolved
    before any documents are merged.
    """


class NoMergingStrategyFoundError(Exception):
    """Raised at runtime when no registered strategy survives MIME filtering
    and can_handle inspection. Under normal operation this should never occur
    — it signals that BottomUpMergingStrategy was omitted from the registered
    strategy list.
    """


class MergerRegistry:
    """Dispatches a list of DocumentChunks to the highest-priority matching
    merging strategy.

    Accepts a list of strategies as a constructor argument.

    Startup validation:
        Raises MergerPriorityConflictError if any two strategies share the
        same get_priority() value for the same FileType.

    Dispatch flow:
        1. Filter candidates to those whose supported_mime_types includes
           the chunks' FileType
        2. Call can_handle(chunks) on each candidate
        3. Sort surviving candidates by get_priority() descending, dispatch
           to the winner
    """

    def __init__(self, strategies: list[BaseMergingStrategy]) -> None:
        self._strategies = strategies
        self._validate_priorities()

    def _validate_priorities(self) -> None:
        seen: dict[tuple[FileType, int], type[BaseMergingStrategy]] = {}
        for strategy in self._strategies:
            priority = strategy.get_priority()
            for mime_type in strategy.supported_mime_types:
                key = (mime_type, priority)
                if key in seen:
                    raise MergerPriorityConflictError(
                        f"Priority conflict: {type(strategy).__name__} and "
                        f"{seen[key].__name__} both declare priority {priority} "
                        f"for {mime_type!r}."
                    )
                seen[key] = type(strategy)

    def merge(self, chunks: list[DocumentChunk]) -> DocumentTree:
        if not chunks:
            raise NoMergingStrategyFoundError("No chunks provided.")

        mime_type = chunks[0].mime_type

        candidates = [
            s for s in self._strategies
            if mime_type in s.supported_mime_types
        ]

        survivors = [s for s in candidates if s.can_handle(chunks)]

        if not survivors:
            raise NoMergingStrategyFoundError(
                f"No merging strategy found for mime_type={mime_type!r}. "
                "Ensure BottomUpMergingStrategy is registered."
            )

        winner = max(survivors, key=lambda s: s.get_priority())
        return winner.merge(chunks)