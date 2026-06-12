from __future__ import annotations

from dataclasses import dataclass, field

from libs.profiler.enums import FileType, Layout


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
