from abc import ABC, abstractmethod


class BlobNotFoundError(Exception):
    """Raised when a requested key does not exist in the blob store."""


class BlobStore(ABC):
    """Abstract base for blob store implementations.

    Each instance is scoped to a single collection at construction time,
    mapping naturally to concepts like buckets (MinIO, S3) or directories
    (filesystem).
    """

    def __init__(self, collection: str) -> None:
        self._collection = collection

    @abstractmethod
    def save(self, key: str, data: bytes) -> str:
        """Store data under the given key.

        Returns the URI of the stored object.
        """

    @abstractmethod
    def get(self, key: str) -> bytes:
        """Retrieve data by key.

        Raises BlobNotFoundError if the key does not exist.
        """

    @abstractmethod
    def delete(self, key: str) -> None:
        """Remove data by key. No-op if the key does not exist."""

    @abstractmethod
    def exists(self, key: str) -> bool:
        """Returns True if the key exists, False otherwise."""