from datetime import datetime, timezone
from uuid import UUID, uuid4

from backends.record.enums import IngestionStatus
from backends.record.models import DocumentRecord


def _make_record(**kwargs) -> DocumentRecord:
    defaults = dict(
        id=uuid4(),
        status=IngestionStatus.PENDING,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    defaults.update(kwargs)
    return DocumentRecord(**defaults)


class TestDocumentRecord:
    def test_construction_with_required_fields(self):
        record = _make_record()
        assert isinstance(record.id, UUID)
        assert record.status == IngestionStatus.PENDING
        assert isinstance(record.created_at, datetime)
        assert isinstance(record.updated_at, datetime)

    def test_optional_fields_default_to_none(self):
        record = _make_record()
        assert record.external_id is None
        assert record.profile_uri is None
        assert record.parsed_document_uri is None
        assert record.tree_uri is None

    def test_construction_with_all_fields(self):
        record = _make_record(
            external_id="ext-123",
            profile_uri="s3://bucket/profile.json",
            parsed_document_uri="s3://bucket/parsed.json",
            tree_uri="s3://bucket/tree.json",
        )
        assert record.external_id == "ext-123"
        assert record.profile_uri == "s3://bucket/profile.json"
        assert record.parsed_document_uri == "s3://bucket/parsed.json"
        assert record.tree_uri == "s3://bucket/tree.json"