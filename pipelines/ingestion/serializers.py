from __future__ import annotations

from uuid import UUID

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


class DocumentProfileSerializer:
    def to_dict(self, profile: DocumentProfile) -> dict:
        return {
            "mime_type": profile.mime_type.value,
            "page_count": profile.page_count,
            "pages": [self._page_profile_to_dict(p) for p in profile.pages],
        }

    def from_dict(self, data: dict) -> DocumentProfile:
        return DocumentProfile(
            mime_type=FileType(data["mime_type"]),
            page_count=data["page_count"],
            pages=[self._page_profile_from_dict(p) for p in data.get("pages", [])],
        )

    def _page_profile_to_dict(self, page: PageProfile) -> dict:
        return {
            "page_number": page.page_number,
            "has_text": page.has_text,
            "has_images": page.has_images,
            "has_tables": page.has_tables,
            "is_scanned": page.is_scanned,
            "layout": page.layout.value,
            "language": page.language,
        }

    def _page_profile_from_dict(self, data: dict) -> PageProfile:
        return PageProfile(
            page_number=data["page_number"],
            has_text=data["has_text"],
            has_images=data["has_images"],
            has_tables=data["has_tables"],
            is_scanned=data["is_scanned"],
            layout=Layout(data["layout"]),
            language=data.get("language"),
        )


class ParsedDocumentSerializer:
    def to_dict(self, document: ParsedDocument) -> dict:
        return {
            "mime_type": document.mime_type.value,
            "page_count": document.page_count,
            "pages": [self._parsed_page_to_dict(p) for p in document.pages],
        }

    def from_dict(self, data: dict) -> ParsedDocument:
        return ParsedDocument(
            mime_type=FileType(data["mime_type"]),
            page_count=data["page_count"],
            pages=[self._parsed_page_from_dict(p) for p in data.get("pages", [])],
        )

    def _parsed_page_to_dict(self, page: ParsedPage) -> dict:
        return {
            "page_number": page.page_number,
            "content": page.content,
            "strategy": page.strategy,
        }

    def _parsed_page_from_dict(self, data: dict) -> ParsedPage:
        return ParsedPage(
            page_number=data["page_number"],
            content=data["content"],
            strategy=data["strategy"],
        )


class DocumentChunkSerializer:
    def to_dict(self, chunk: DocumentChunk) -> dict:
        return {
            "id": str(chunk.id),
            "document_id": str(chunk.document_id) if chunk.document_id else None,
            "content": chunk.content,
            "mime_type": chunk.mime_type.value,
            "strategy": chunk.strategy,
            "source_reference": {
                "page_start": chunk.source_reference.page_start,
                "page_end": chunk.source_reference.page_end,
            },
        }

    def from_dict(self, data: dict) -> DocumentChunk:
        return DocumentChunk(
            id=UUID(data["id"]),
            document_id=UUID(data["document_id"]) if data.get("document_id") else None,
            content=data["content"],
            mime_type=FileType(data["mime_type"]),
            strategy=data["strategy"],
            source_reference=SourceReference(
                page_start=data["source_reference"]["page_start"],
                page_end=data["source_reference"]["page_end"],
            ),
        )

    def list_to_dict(self, chunks: list[DocumentChunk]) -> list[dict]:
        return [self.to_dict(c) for c in chunks]

    def list_from_dict(self, data: list[dict]) -> list[DocumentChunk]:
        return [self.from_dict(d) for d in data]


class DocumentTreeSerializer:
    def __init__(self) -> None:
        self._chunk_serializer = DocumentChunkSerializer()

    def to_dict(self, tree: DocumentTree) -> dict:
        return {
            "document_id": str(tree.document_id) if tree.document_id else None,
            "mime_type": tree.mime_type.value,
            "root": self._node_to_dict(tree.root),
        }

    def from_dict(self, data: dict) -> DocumentTree:
        return DocumentTree(
            document_id=UUID(data["document_id"]) if data.get("document_id") else None,
            mime_type=FileType(data["mime_type"]),
            root=self._node_from_dict(data["root"]),
        )

    def _node_to_dict(self, node: TreeNode) -> dict:
        return {
            "id": str(node.id),
            "content": node.content,
            "level": node.level,
            "chunk": self._chunk_serializer.to_dict(node.chunk) if node.chunk else None,
            "children": [self._node_to_dict(c) for c in node.children],
        }

    def _node_from_dict(self, data: dict) -> TreeNode:
        return TreeNode(
            id=UUID(data["id"]),
            content=data["content"],
            level=data["level"],
            chunk=self._chunk_serializer.from_dict(data["chunk"]) if data.get("chunk") else None,
            children=[self._node_from_dict(c) for c in data.get("children", [])],
        )