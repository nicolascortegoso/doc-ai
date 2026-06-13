from __future__ import annotations

from dataclasses import dataclass

from libs.common.models import DocumentChunk


@dataclass
class SearchResult:
    chunk: DocumentChunk
    score: float