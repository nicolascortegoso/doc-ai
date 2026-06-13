from libs.common.enums import FileType
from libs.common.models import DocumentProfile, ParsedDocument, ParsedPage
from libs.parser.base import BasePageExtractionStrategy


class ParserPriorityConflictError(Exception):
    """Raised at startup when two registered strategies share the same priority
    for the same FileType. Indicates a misconfiguration that must be resolved
    before any documents are parsed.
    """


class NoStrategyFoundError(Exception):
    """Raised at runtime when no registered strategy survives MIME filtering
    and can_handle inspection for a given page. Under normal operation this
    should never occur — it signals that DefaultPageExtractionStrategy was
    omitted from the registered strategy list.
    """


class ParserRegistry:
    """Dispatches each page to the highest-priority matching extraction strategy.

    Accepts a list of strategies as a constructor argument.

    Startup validation:
        Raises ParserPriorityConflictError if any two strategies share the
        same get_priority() value for the same FileType.

    Dispatch flow per page:
        1. Filter candidates to those whose supported_mime_types includes
           the document's FileType
        2. Call can_handle(page_profile) on each candidate
        3. Sort surviving candidates by get_priority() descending, dispatch
           to the winner
        4. Record the strategy class name on the resulting ParsedPage
    """

    def __init__(self, strategies: list[BasePageExtractionStrategy]) -> None:
        self._strategies = strategies
        self._validate_priorities()

    def _validate_priorities(self) -> None:
        seen: dict[tuple[FileType, int], type[BasePageExtractionStrategy]] = {}
        for strategy in self._strategies:
            priority = strategy.get_priority()
            for mime_type in strategy.supported_mime_types:
                key = (mime_type, priority)
                if key in seen:
                    raise ParserPriorityConflictError(
                        f"Priority conflict: {type(strategy).__name__} and "
                        f"{seen[key].__name__} both declare priority {priority} "
                        f"for {mime_type!r}."
                    )
                seen[key] = type(strategy)

    def parse(self, file_bytes: bytes, profile: DocumentProfile) -> ParsedDocument:
        parsed_pages = [
            self._parse_page(file_bytes, page_profile, profile.mime_type)
            for page_profile in profile.pages
        ]
        return ParsedDocument(
            mime_type=profile.mime_type,
            page_count=profile.page_count,
            pages=parsed_pages,
        )

    def _parse_page(
        self,
        file_bytes: bytes,
        page_profile,
        mime_type: FileType,
    ) -> ParsedPage:
        candidates = [
            s for s in self._strategies
            if mime_type in s.supported_mime_types
        ]

        survivors = [s for s in candidates if s.can_handle(page_profile)]

        if not survivors:
            raise NoStrategyFoundError(
                f"No strategy found for page {page_profile.page_number} "
                f"(mime_type={mime_type!r}). "
                "Ensure DefaultPageExtractionStrategy is registered."
            )

        winner = max(survivors, key=lambda s: s.get_priority())
        content = winner.extract(file_bytes, page_profile)

        return ParsedPage(
            page_number=page_profile.page_number,
            content=content,
            strategy=type(winner).__name__,
        )