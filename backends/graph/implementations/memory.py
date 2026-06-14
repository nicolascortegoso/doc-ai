from __future__ import annotations

from uuid import UUID

from libs.common.models import DocumentTree, TreeNode
from backends.graph.base import GraphStore


class InMemoryGraphStore(GraphStore):
    """In-memory graph store for testing and local development.

    Stores trees in a Python dict keyed by document_id. Traversal methods
    operate directly on the in-memory tree structure. Not thread-safe.
    """

    def __init__(self) -> None:
        self._trees: dict[str, DocumentTree] = {}
        self._node_index: dict[str, TreeNode] = {}

    def save(self, tree: DocumentTree) -> None:
        key = str(tree.document_id)
        self._trees[key] = tree
        self._index_nodes(tree.root)

    def get(self, document_id: UUID) -> DocumentTree | None:
        return self._trees.get(str(document_id))

    def delete(self, document_id: UUID) -> None:
        key = str(document_id)
        tree = self._trees.pop(key, None)
        if tree is not None:
            self._deindex_nodes(tree.root)

    def exists(self, document_id: UUID) -> bool:
        return str(document_id) in self._trees

    def get_node(self, node_id: UUID) -> TreeNode | None:
        return self._node_index.get(str(node_id))

    def get_children(self, node_id: UUID) -> list[TreeNode]:
        node = self._node_index.get(str(node_id))
        if node is None:
            return []
        return list(node.children)

    def get_root(self, document_id: UUID) -> TreeNode | None:
        tree = self._trees.get(str(document_id))
        if tree is None:
            return None
        return tree.root

    def _index_nodes(self, node: TreeNode) -> None:
        self._node_index[str(node.id)] = node
        for child in node.children:
            self._index_nodes(child)

    def _deindex_nodes(self, node: TreeNode) -> None:
        self._node_index.pop(str(node.id), None)
        for child in node.children:
            self._deindex_nodes(child)