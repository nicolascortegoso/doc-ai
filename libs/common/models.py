from __future__ import annotations

from dataclasses import dataclass, field

from libs.common.enums import FileType, Layout


@dataclass
class PageProfile:
    page_number: int
    has_text: bool
    has_images: bool
    has_tables: bool
    is_scanned: bool
    layout: Layout
    language: str | None


@dataclass
class DocumentProfile:
    mime_type: FileType
    page_count: int
    pages: list[PageProfile] = field(default_factory=list)


@dataclass
class ParsedPage:
    page_number: int
    content: str
    strategy: str  # class name of the strategy that produced this page


@dataclass
class ParsedDocument:
    mime_type: FileType
    page_count: int
    pages: list[ParsedPage] = field(default_factory=list)

    def to_markdown(self) -> str:
        """Utility method for debugging and storage purposes.

        Assembles the full document as a single Markdown string with
        <!-- page N --> delimiters joined by double newlines. Not part
        of the pipeline — the chunker operates directly on pages.
        """
        parts = []
        for page in self.pages:
            parts.append(f"<!-- page {page.page_number} -->\n{page.content}")
        return "\n\n".join(parts)


@dataclass
class SourceReference:
    page_start: int
    page_end: int


@dataclass
class DocumentChunk:
    content: str
    source_reference: SourceReference
    mime_type: FileType
    strategy: str