import pytest

from backends.blob.base import BlobNotFoundError
from backends.blob.implementations.memory import InMemoryBlobStore


@pytest.fixture
def store() -> InMemoryBlobStore:
    return InMemoryBlobStore(collection="test-collection")


class TestInMemoryBlobStoreSave:
    def test_save_returns_uri(self, store):
        uri = store.save("profile.json", b"data")
        assert uri == "test-collection/profile.json"

    def test_save_uri_format_is_collection_slash_key(self, store):
        uri = store.save("subdir/file.json", b"data")
        assert uri == "test-collection/subdir/file.json"

    def test_save_persists_data(self, store):
        store.save("key.bin", b"hello bytes")
        result = store.get("key.bin")
        assert result == b"hello bytes"

    def test_save_overwrites_existing_key(self, store):
        store.save("key.bin", b"original")
        store.save("key.bin", b"updated")
        assert store.get("key.bin") == b"updated"


class TestInMemoryBlobStoreGet:
    def test_get_returns_correct_data(self, store):
        store.save("key.bin", b"expected data")
        assert store.get("key.bin") == b"expected data"

    def test_get_raises_blob_not_found_for_missing_key(self, store):
        with pytest.raises(BlobNotFoundError):
            store.get("nonexistent.bin")

    def test_get_raises_with_informative_message(self, store):
        with pytest.raises(BlobNotFoundError) as exc_info:
            store.get("missing.json")
        assert "missing.json" in str(exc_info.value)


class TestInMemoryBlobStoreDelete:
    def test_delete_removes_data(self, store):
        store.save("key.bin", b"data")
        store.delete("key.bin")
        assert not store.exists("key.bin")

    def test_delete_is_noop_for_missing_key(self, store):
        store.delete("nonexistent.bin")

    def test_delete_does_not_affect_other_keys(self, store):
        store.save("key1.bin", b"data1")
        store.save("key2.bin", b"data2")
        store.delete("key1.bin")
        assert store.exists("key2.bin")


class TestInMemoryBlobStoreExists:
    def test_exists_returns_true_for_existing_key(self, store):
        store.save("key.bin", b"data")
        assert store.exists("key.bin") is True

    def test_exists_returns_false_for_missing_key(self, store):
        assert store.exists("nonexistent.bin") is False

    def test_exists_returns_false_after_delete(self, store):
        store.save("key.bin", b"data")
        store.delete("key.bin")
        assert store.exists("key.bin") is False


class TestInMemoryBlobStoreCollection:
    def test_collection_is_scoped(self):
        store_a = InMemoryBlobStore(collection="collection-a")
        store_b = InMemoryBlobStore(collection="collection-b")
        store_a.save("key.bin", b"data a")
        assert not store_b.exists("key.bin")

    def test_uri_reflects_collection_name(self):
        store = InMemoryBlobStore(collection="my-bucket")
        uri = store.save("file.json", b"{}")
        assert uri.startswith("my-bucket/")