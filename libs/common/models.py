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


@dataclass
class TreeNode:
    content: str
    level: int
    children: list[TreeNode] = field(default_factory=list)
    chunk: DocumentChunk | None = None

    @property
    def source_reference(self) -> SourceReference:
        """Computed dynamically — never stored.

        Leaf node: returns chunk.source_reference.
        Internal node: spans page_start of leftmost leaf to page_end of rightmost leaf.
        """
        if self.chunk is not None:
            return self.chunk.source_reference
        return SourceReference(
            page_start=self._leftmost_leaf().chunk.source_reference.page_start,
            page_end=self._rightmost_leaf().chunk.source_reference.page_end,
        )

    def _leftmost_leaf(self) -> TreeNode:
        node = self
        while node.children:
            node = node.children[0]
        return node

    def _rightmost_leaf(self) -> TreeNode:
        node = self
        while node.children:
            node = node.children[-1]
        return node


@dataclass
class DocumentTree:
    root: TreeNode
    mime_type: FileType