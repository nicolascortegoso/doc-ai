from abc import ABC, abstractmethod
from uuid import UUID

from backends.record.enums import IngestionStatus
from backends.record.models import DocumentRecord


class RecordStore(ABC):
    """Abstract base for record store implementations.

    Tracks document ingestion state, timestamps, and URIs pointing to
    pipeline outputs in external storage.
    """

    @abstractmethod
    def save(self, record: DocumentRecord) -> None:
        """Persist a new record."""

    @abstractmethod
    def get(self, id: UUID) -> DocumentRecord | None:
        """Retrieve a record by internal ID. Returns None if not found."""

    @abstractmethod
    def update(self, record: DocumentRecord) -> None:
        """Update an existing record."""

    @abstractmethod
    def delete(self, id: UUID) -> None:
        """Remove a record by internal ID."""

    @abstractmethod
    def find_by_external_id(self, external_id: str) -> DocumentRecord | None:
        """Retrieve a record by external ID. Returns None if not found."""

    @abstractmethod
    def find_by_status(self, status: IngestionStatus) -> list[DocumentRecord]:
        """Retrieve all records with the given ingestion status."""