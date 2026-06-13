from datetime import datetime
from uuid import UUID

from backends.record.enums import IngestionStatus
from backends.record.models import DocumentRecord


class DocumentRecordSerializer:
    """Converts DocumentRecord to and from a portable dict representation.

    Used by all store implementations to avoid duplicating serialisation logic.
    """

    def to_dict(self, record: DocumentRecord) -> dict:
        return {
            "id": str(record.id),
            "external_id": record.external_id,
            "status": record.status.value,
            "created_at": record.created_at.isoformat(),
            "updated_at": record.updated_at.isoformat(),
            "profile_uri": record.profile_uri,
            "parsed_document_uri": record.parsed_document_uri,
            "tree_uri": record.tree_uri,
        }

    def from_dict(self, data: dict) -> DocumentRecord:
        return DocumentRecord(
            id=UUID(data["id"]),
            external_id=data.get("external_id"),
            status=IngestionStatus(data["status"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            profile_uri=data.get("profile_uri"),
            parsed_document_uri=data.get("parsed_document_uri"),
            tree_uri=data.get("tree_uri"),
        )