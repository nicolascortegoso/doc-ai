from uuid import UUID

from backends.record.base import RecordStore
from backends.record.enums import IngestionStatus
from backends.record.models import DocumentRecord
from backends.record.serializer import DocumentRecordSerializer


class InMemoryRecordStore(RecordStore):
    """In-memory record store for testing and local development.

    Stores records in a Python dict keyed by id.
    Not thread-safe.
    """

    def __init__(self) -> None:
        self._store: dict[str, dict] = {}
        self._serializer = DocumentRecordSerializer()

    def save(self, record: DocumentRecord) -> None:
        self._store[str(record.id)] = self._serializer.to_dict(record)

    def get(self, id: UUID) -> DocumentRecord | None:
        data = self._store.get(str(id))
        if data is None:
            return None
        return self._serializer.from_dict(data)

    def update(self, record: DocumentRecord) -> None:
        self._store[str(record.id)] = self._serializer.to_dict(record)

    def delete(self, id: UUID) -> None:
        self._store.pop(str(id), None)

    def find_by_external_id(self, external_id: str) -> DocumentRecord | None:
        for data in self._store.values():
            if data.get("external_id") == external_id:
                return self._serializer.from_dict(data)
        return None

    def find_by_status(self, status: IngestionStatus) -> list[DocumentRecord]:
        return [
            self._serializer.from_dict(data)
            for data in self._store.values()
            if data["status"] == status.value
        ]