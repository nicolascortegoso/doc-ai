from uuid import UUID

from common.enums import FileType
from common.models import GlossaryEntry, ParsedDocument
from libs.distiller.base import BaseDistillerStrategy


class DistillerPriorityConflictError(Exception):
    """Raised at startup when two registered strategies share the same priority
    for the same FileType.
    """


class NoDistillerStrategyFoundError(Exception):
    """Raised at runtime when no registered strategy survives MIME filtering
    and can_handle inspection.
    """


class DistillerRegistry:
    def __init__(self, strategies: list[BaseDistillerStrategy]) -> None:
        self._strategies = strategies
        self._validate_priorities()

    def _validate_priorities(self) -> None:
        seen: dict[tuple[FileType, int], type[BaseDistillerStrategy]] = {}
        for strategy in self._strategies:
            priority = strategy.get_priority()
            for mime_type in strategy.supported_mime_types:
                key = (mime_type, priority)
                if key in seen:
                    raise DistillerPriorityConflictError(
                        f"Priority conflict: {type(strategy).__name__} and "
                        f"{seen[key].__name__} both declare priority {priority} "
                        f"for {mime_type!r}."
                    )
                seen[key] = type(strategy)

    def distill(
        self, document: ParsedDocument, document_id: UUID
    ) -> list[GlossaryEntry]:
        if not document.pages:
            return []

        mime_type = document.mime_type

        candidates = [
            s for s in self._strategies
            if mime_type in s.supported_mime_types
        ]

        survivors = [s for s in candidates if s.can_handle(document)]

        if not survivors:
            raise NoDistillerStrategyFoundError(
                f"No distiller strategy found for mime_type={mime_type!r}. "
                "Ensure GlossaryDistillerStrategy is registered."
            )

        winner = max(survivors, key=lambda s: s.get_priority())
        return winner.distill(document, document_id)