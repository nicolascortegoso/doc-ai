from __future__ import annotations

from typing import ClassVar

from libs.common.enums import FileType
from libs.common.models import DocumentChunk, ParsedDocument, SourceReference
from libs.chunker.base import BaseChunkingStrategy
from libs.splitter.base import Splitter
from libs.splitter.implementations.character import CharacterSplitter


class SlidingWindowChunkingStrategy(BaseChunkingStrategy):
    """Sliding window chunker operating directly on ParsedDocument.pages.

    Concatenates page content in order, builds a page map to track character
    positions, then slides a window over the concatenated text. Each chunk
    records the pages it spans via SourceReference.

    A Splitter is injected at construction time to control where windows
    are cut. Defaults to CharacterSplitter (exact character boundary).

    Args:
        window_size: Number of characters per chunk. Default: 1000.
        overlap_ratio: Fraction of window_size to overlap between consecutive
            chunks. Must be in [0, 1). Default: 0.2.
        splitter: Injected Splitter. Default: CharacterSplitter.
    """

    supported_mime_types: ClassVar[list[FileType]] = list(FileType)

    def __init__(
        self,
        window_size: int = 1000,
        overlap_ratio: float = 0.2,
        splitter: Splitter = None,
    ) -> None:
        if not (0 <= overlap_ratio < 1):
            raise ValueError(f"overlap_ratio must be in [0, 1), got {overlap_ratio}")
        if window_size < 1:
            raise ValueError(f"window_size must be >= 1, got {window_size}")
        self._window_size = window_size
        self._overlap_ratio = overlap_ratio
        self._splitter = splitter or CharacterSplitter()

    def can_handle(self, document: ParsedDocument) -> bool:
        return True

    def get_priority(self) -> int:
        return 1

    def chunk(self, document: ParsedDocument) -> list[DocumentChunk]:
        text, page_map = self._build_text_and_page_map(document)

        if not text.strip():
            return []

        step = max(1, int(self._window_size * (1 - self._overlap_ratio)))
        chunks = []
        pos = 0

        while pos < len(text):
            proposed_end = min(pos + self._window_size, len(text))
            actual_end = self._splitter.find_split(text, proposed_end)
            actual_end = max(pos + 1, min(actual_end, len(text)))

            window = text[pos:actual_end]

            if window.strip():
                chunks.append(DocumentChunk(
                    content=window,
                    source_reference=SourceReference(
                        page_start=self._resolve_page(page_map, pos),
                        page_end=self._resolve_page(page_map, actual_end - 1),
                    ),
                    mime_type=document.mime_type,
                    strategy=type(self).__name__,
                ))

            pos += step

        return chunks

    def _build_text_and_page_map(
        self, document: ParsedDocument
    ) -> tuple[str, list[tuple[int, int]]]:
        """Concatenate page content and build a page map.

        Returns:
            text: Concatenated content of all pages.
            page_map: List of (char_position, page_number) tuples marking
                where each page begins in the concatenated text.
        """
        parts = []
        page_map: list[tuple[int, int]] = []
        cursor = 0

        for page in document.pages:
            page_map.append((cursor, page.page_number))
            parts.append(page.content)
            cursor += len(page.content)

        return "".join(parts), page_map

    def _resolve_page(self, page_map: list[tuple[int, int]], position: int) -> int:
        """Return the page number for a given character position."""
        page = page_map[0][1]
        for char_pos, page_number in page_map:
            if char_pos <= position:
                page = page_number
            else:
                break
        return page