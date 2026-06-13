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
        """Assemble full Markdown content with page delimiters.

        Every page is included regardless of whether its content is empty,
        keeping page numbers consistent with the DocumentProfile.
        """
        parts = []
        for page in self.pages:
            parts.append(f"<!-- page {page.page_number} -->\n{page.content}")
        return "\n\n".join(parts)