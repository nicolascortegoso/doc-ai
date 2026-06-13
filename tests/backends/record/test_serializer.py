from datetime import datetime, timezone
from uuid import uuid4

import pytest

from backends.record.enums import IngestionStatus
from backends.record.models import DocumentRecord
from backends.record.serializer import DocumentRecordSerializer


@pytest.fixture
def serializer() -> DocumentRecordSerializer:
    return DocumentRecordSerializer()


@pytest.fixture
def record() -> DocumentRecord:
    return DocumentRecord(
        id=uuid4(),
        external_id="ext-123",
        status=IngestionStatus.PROFILED,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        profile_uri="s3://bucket/profile.json",
        parsed_document_uri="s3://bucket/parsed.json",
        tree_uri="s3://bucket/tree.json",
    )


class TestDocumentRecordSerializer:
    def test_to_dict_returns_dict(self, serializer, record):
        result = serializer.to_dict(record)
        assert isinstance(result, dict)

    def test_to_dict_serialises_id_as_string(self, serializer, record):
        result = serializer.to_dict(record)
        assert result["id"] == str(record.id)

    def test_to_dict_serialises_status_as_string(self, serializer, record):
        result = serializer.to_dict(record)
        assert result["status"] == record.status.value

    def test_to_dict_serialises_timestamps_as_iso_strings(self, serializer, record):
        result = serializer.to_dict(record)
        assert isinstance(result["created_at"], str)
        assert isinstance(result["updated_at"], str)

    def test_to_dict_includes_all_uri_fields(self, serializer, record):
        result = serializer.to_dict(record)
        assert result["profile_uri"] == record.profile_uri
        assert result["parsed_document_uri"] == record.parsed_document_uri
        assert result["tree_uri"] == record.tree_uri

    def test_from_dict_returns_document_record(self, serializer, record):
        data = serializer.to_dict(record)
        result = serializer.from_dict(data)
        assert isinstance(result, DocumentRecord)

    def test_round_trip_preserves_id(self, serializer, record):
        result = serializer.from_dict(serializer.to_dict(record))
        assert result.id == record.id

    def test_round_trip_preserves_status(self, serializer, record):
        result = serializer.from_dict(serializer.to_dict(record))
        assert result.status == record.status

    def test_round_trip_preserves_external_id(self, serializer, record):
        result = serializer.from_dict(serializer.to_dict(record))
        assert result.external_id == record.external_id

    def test_round_trip_preserves_uris(self, serializer, record):
        result = serializer.from_dict(serializer.to_dict(record))
        assert result.profile_uri == record.profile_uri
        assert result.parsed_document_uri == record.parsed_document_uri
        assert result.tree_uri == record.tree_uri

    def test_round_trip_with_none_fields(self, serializer):
        record = DocumentRecord(
            id=uuid4(),
            status=IngestionStatus.PENDING,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        result = serializer.from_dict(serializer.to_dict(record))
        assert result.external_id is None
        assert result.profile_uri is None
        assert result.parsed_document_uri is None
        assert result.tree_uri is None