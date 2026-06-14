from __future__ import annotations

from uuid import uuid4

from common.enums import FileType, Layout
from common.models import (
    DocumentChunk,
    DocumentProfile,
    DocumentTree,
    PageProfile,
    ParsedDocument,
    ParsedPage,
    SourceReference,
    TreeNode,
)
from pipelines.ingestion.serializers import (
    DocumentChunkSerializer,
    DocumentProfileSerializer,
    DocumentTreeSerializer,
    ParsedDocumentSerializer,
)


class TestDocumentProfileSerializer:
    def test_round_trip_preserves_mime_type(self):
        s = DocumentProfileSerializer()
        profile = DocumentProfile(mime_type=FileType.PDF, page_count=1, pages=[])
        assert s.from_dict(s.to_dict(profile)).mime_type == FileType.PDF

    def test_round_trip_preserves_page_count(self):
        s = DocumentProfileSerializer()
        profile = DocumentProfile(mime_type=FileType.PDF, page_count=3, pages=[])
        assert s.from_dict(s.to_dict(profile)).page_count == 3

    def test_round_trip_preserves_pages(self):
        s = DocumentProfileSerializer()
        profile = DocumentProfile(
            mime_type=FileType.PDF,
            page_count=1,
            pages=[
                PageProfile(
                    page_number=1,
                    has_text=True,
                    has_images=False,
                    has_tables=True,
                    is_scanned=False,
                    layout=Layout.SINGLE_COLUMN,
                    language="en",
                )
            ],
        )
        result = s.from_dict(s.to_dict(profile))
        assert len(result.pages) == 1
        assert result.pages[0].page_number == 1
        assert result.pages[0].has_text is True
        assert result.pages[0].has_tables is True
        assert result.pages[0].layout == Layout.SINGLE_COLUMN
        assert result.pages[0].language == "en"

    def test_round_trip_with_none_language(self):
        s = DocumentProfileSerializer()
        profile = DocumentProfile(
            mime_type=FileType.PDF,
            page_count=1,
            pages=[
                PageProfile(
                    page_number=1,
                    has_text=False,
                    has_images=True,
                    has_tables=False,
                    is_scanned=True,
                    layout=Layout.UNKNOWN,
                    language=None,
                )
            ],
        )
        result = s.from_dict(s.to_dict(profile))
        assert result.pages[0].language is None

    def test_round_trip_empty_pages(self):
        s = DocumentProfileSerializer()
        profile = DocumentProfile(mime_type=FileType.UNKNOWN, page_count=0, pages=[])
        result = s.from_dict(s.to_dict(profile))
        assert result.pages == []


class TestParsedDocumentSerializer:
    def test_round_trip_preserves_mime_type(self):
        s = ParsedDocumentSerializer()
        doc = ParsedDocument(mime_type=FileType.PDF, page_count=1, pages=[])
        assert s.from_dict(s.to_dict(doc)).mime_type == FileType.PDF

    def test_round_trip_preserves_page_count(self):
        s = ParsedDocumentSerializer()
        doc = ParsedDocument(mime_type=FileType.PDF, page_count=2, pages=[])
        assert s.from_dict(s.to_dict(doc)).page_count == 2

    def test_round_trip_preserves_pages(self):
        s = ParsedDocumentSerializer()
        doc = ParsedDocument(
            mime_type=FileType.PDF,
            page_count=1,
            pages=[ParsedPage(page_number=1, content="hello world", strategy="PlainPdfExtractionStrategy")],
        )
        result = s.from_dict(s.to_dict(doc))
        assert result.pages[0].page_number == 1
        assert result.pages[0].content == "hello world"
        assert result.pages[0].strategy == "PlainPdfExtractionStrategy"

    def test_round_trip_empty_pages(self):
        s = ParsedDocumentSerializer()
        doc = ParsedDocument(mime_type=FileType.PDF, page_count=0, pages=[])
        assert s.from_dict(s.to_dict(doc)).pages == []


class TestDocumentChunkSerializer:
    def test_round_trip_preserves_id(self):
        s = DocumentChunkSerializer()
        chunk = _make_chunk()
        assert s.from_dict(s.to_dict(chunk)).id == chunk.id

    def test_round_trip_preserves_content(self):
        s = DocumentChunkSerializer()
        chunk = _make_chunk(content="specific content")
        assert s.from_dict(s.to_dict(chunk)).content == "specific content"

    def test_round_trip_preserves_document_id(self):
        s = DocumentChunkSerializer()
        doc_id = uuid4()
        chunk = _make_chunk(document_id=doc_id)
        assert s.from_dict(s.to_dict(chunk)).document_id == doc_id

    def test_round_trip_preserves_none_document_id(self):
        s = DocumentChunkSerializer()
        chunk = _make_chunk()
        assert s.from_dict(s.to_dict(chunk)).document_id is None

    def test_round_trip_preserves_source_reference(self):
        s = DocumentChunkSerializer()
        chunk = _make_chunk(page_start=3, page_end=5)
        result = s.from_dict(s.to_dict(chunk))
        assert result.source_reference.page_start == 3
        assert result.source_reference.page_end == 5

    def test_round_trip_preserves_mime_type(self):
        s = DocumentChunkSerializer()
        chunk = _make_chunk()
        assert s.from_dict(s.to_dict(chunk)).mime_type == FileType.PDF

    def test_list_round_trip_preserves_count(self):
        s = DocumentChunkSerializer()
        chunks = [_make_chunk(content=f"chunk {i}") for i in range(5)]
        result = s.list_from_dict(s.list_to_dict(chunks))
        assert len(result) == 5

    def test_list_round_trip_preserves_content(self):
        s = DocumentChunkSerializer()
        chunks = [_make_chunk(content=f"chunk {i}") for i in range(3)]
        result = s.list_from_dict(s.list_to_dict(chunks))
        assert result[2].content == "chunk 2"

    def test_list_round_trip_empty(self):
        s = DocumentChunkSerializer()
        assert s.list_from_dict(s.list_to_dict([])) == []


class TestDocumentTreeSerializer:
    def test_round_trip_preserves_document_id(self):
        s = DocumentTreeSerializer()
        doc_id = uuid4()
        tree = _make_simple_tree(document_id=doc_id)
        assert s.from_dict(s.to_dict(tree)).document_id == doc_id

    def test_round_trip_preserves_mime_type(self):
        s = DocumentTreeSerializer()
        tree = _make_simple_tree()
        assert s.from_dict(s.to_dict(tree)).mime_type == FileType.PDF

    def test_round_trip_preserves_root_content(self):
        s = DocumentTreeSerializer()
        tree = _make_simple_tree()
        assert s.from_dict(s.to_dict(tree)).root.content == "root"

    def test_round_trip_preserves_root_id(self):
        s = DocumentTreeSerializer()
        tree = _make_simple_tree()
        assert s.from_dict(s.to_dict(tree)).root.id == tree.root.id

    def test_round_trip_preserves_children(self):
        s = DocumentTreeSerializer()
        tree = _make_simple_tree()
        result = s.from_dict(s.to_dict(tree))
        assert len(result.root.children) == 2

    def test_round_trip_preserves_leaf_chunk(self):
        s = DocumentTreeSerializer()
        tree = _make_simple_tree()
        result = s.from_dict(s.to_dict(tree))
        leaf = result.root.children[0]
        assert leaf.chunk is not None
        assert leaf.chunk.content == "leaf 1"

    def test_round_trip_preserves_levels(self):
        s = DocumentTreeSerializer()
        tree = _make_simple_tree()
        result = s.from_dict(s.to_dict(tree))
        assert result.root.level == 1
        assert result.root.children[0].level == 0

    def test_round_trip_none_document_id(self):
        s = DocumentTreeSerializer()
        leaf = TreeNode(content="leaf", level=0, chunk=_make_chunk())
        root = TreeNode(content="root", level=1, children=[leaf])
        tree = DocumentTree(root=root, mime_type=FileType.PDF, document_id=None)
        assert s.from_dict(s.to_dict(tree)).document_id is None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_chunk(
    content: str = "chunk content",
    page_start: int = 1,
    page_end: int = 1,
    document_id=None,
) -> DocumentChunk:
    return DocumentChunk(
        content=content,
        source_reference=SourceReference(page_start=page_start, page_end=page_end),
        mime_type=FileType.PDF,
        strategy="SlidingWindowChunkingStrategy",
        document_id=document_id,
    )


def _make_simple_tree(document_id=None) -> DocumentTree:
    leaf1 = TreeNode(
        content="leaf 1",
        level=0,
        chunk=_make_chunk(content="leaf 1", page_start=1, page_end=1),
    )
    leaf2 = TreeNode(
        content="leaf 2",
        level=0,
        chunk=_make_chunk(content="leaf 2", page_start=2, page_end=2),
    )
    root = TreeNode(content="root", level=1, children=[leaf1, leaf2])
    return DocumentTree(
        root=root,
        mime_type=FileType.PDF,
        document_id=document_id or uuid4(),
    )