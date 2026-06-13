from backends.blob.base import BlobNotFoundError, BlobStore


class InMemoryBlobStore(BlobStore):
    """In-memory blob store for testing and local development.

    Stores data in a Python dict. The URI returned by save is
    {collection}/{key}. Not thread-safe.
    """

    def __init__(self, collection: str) -> None:
        super().__init__(collection)
        self._store: dict[str, bytes] = {}

    def save(self, key: str, data: bytes) -> str:
        self._store[key] = data
        return f"{self._collection}/{key}"

    def get(self, key: str) -> bytes:
        if key not in self._store:
            raise BlobNotFoundError(
                f"Key {key!r} not found in collection {self._collection!r}."
            )
        return self._store[key]

    def delete(self, key: str) -> None:
        self._store.pop(key, None)

    def exists(self, key: str) -> bool:
        return key in self._store