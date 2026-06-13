from datetime import datetime, timezone
from uuid import uuid4

import pytest

from backends.record.enums import IngestionStatus
from backends.record.implementations.memory import InMemoryRecordStore
from backends.record.models import DocumentRecord


def _make_record(
    status: IngestionStatus = IngestionStatus.PENDING,
    external_id: str | None = None,
) -> DocumentRecord:
    return DocumentRecord(
        id=uuid4(),
        status=status,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        external_id=external_id,
    )


@pytest.fixture
def store() -> InMemoryRecordStore:
    return InMemoryRecordStore()


class TestInMemoryRecordStoreSave:
    def test_save_persists_record(self, store):
        record = _make_record()
        store.save(record)
        assert store.get(record.id) is not None

    def test_save_persists_correct_record(self, store):
        record = _make_record()
        store.save(record)
        result = store.get(record.id)
        assert result.id == record.id
        assert result.status == record.status


class TestInMemoryRecordStoreGet:
    def test_get_returns_none_for_missing_record(self, store):
        assert store.get(uuid4()) is None

    def test_get_returns_correct_record(self, store):
        record = _make_record()
        store.save(record)
        result = store.get(record.id)
        assert result.id == record.id


class TestInMemoryRecordStoreUpdate:
    def test_update_changes_status(self, store):
        record = _make_record(status=IngestionStatus.PENDING)
        store.save(record)
        record.status = IngestionStatus.PROFILED
        store.update(record)
        result = store.get(record.id)
        assert result.status == IngestionStatus.PROFILED

    def test_update_changes_uri(self, store):
        record = _make_record()
        store.save(record)
        record.profile_uri = "s3://bucket/profile.json"
        store.update(record)
        result = store.get(record.id)
        assert result.profile_uri == "s3://bucket/profile.json"


class TestInMemoryRecordStoreDelete:
    def test_delete_removes_record(self, store):
        record = _make_record()
        store.save(record)
        store.delete(record.id)
        assert store.get(record.id) is None

    def test_delete_nonexistent_record_does_not_raise(self, store):
        store.delete(uuid4())


class TestInMemoryRecordStoreFindByExternalId:
    def test_find_by_external_id_returns_matching_record(self, store):
        record = _make_record(external_id="ext-123")
        store.save(record)
        result = store.find_by_external_id("ext-123")
        assert result is not None
        assert result.external_id == "ext-123"

    def test_find_by_external_id_returns_none_when_not_found(self, store):
        assert store.find_by_external_id("nonexistent") is None

    def test_find_by_external_id_returns_correct_record(self, store):
        r1 = _make_record(external_id="ext-1")
        r2 = _make_record(external_id="ext-2")
        store.save(r1)
        store.save(r2)
        result = store.find_by_external_id("ext-2")
        assert result.id == r2.id


class TestInMemoryRecordStoreFindByStatus:
    def test_find_by_status_returns_matching_records(self, store):
        r1 = _make_record(status=IngestionStatus.PENDING)
        r2 = _make_record(status=IngestionStatus.PENDING)
        r3 = _make_record(status=IngestionStatus.PROFILED)
        store.save(r1)
        store.save(r2)
        store.save(r3)
        result = store.find_by_status(IngestionStatus.PENDING)
        assert len(result) == 2

    def test_find_by_status_returns_empty_list_when_none_match(self, store):
        record = _make_record(status=IngestionStatus.PENDING)
        store.save(record)
        result = store.find_by_status(IngestionStatus.INDEXED)
        assert result == []

    def test_find_by_status_returns_all_matching_statuses(self, store):
        for status in [IngestionStatus.PENDING, IngestionStatus.PROFILED, IngestionStatus.FAILED]:
            store.save(_make_record(status=status))
        result = store.find_by_status(IngestionStatus.PENDING)
        assert all(r.status == IngestionStatus.PENDING for r in result)