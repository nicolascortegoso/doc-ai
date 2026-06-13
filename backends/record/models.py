from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from backends.record.enums import IngestionStatus


@dataclass
class DocumentRecord:
    id: UUID
    status: IngestionStatus
    created_at: datetime
    updated_at: datetime
    external_id: str | None = None
    profile_uri: str | None = None
    parsed_document_uri: str | None = None
    tree_uri: str | None = None