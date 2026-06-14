from __future__ import annotations

from uuid import uuid4

import pytest

from common.enums import FileType
from common.models import DocumentChunk, DocumentTree, SourceReference, TreeNode
from backends.graph.implementations.memory import InMemoryGraphStore


def _make_chunk(page: int = 1) -> DocumentChunk:
    return DocumentChunk(
        content=f"chunk content page {page}",
        source_reference=SourceReference(page_start=page, page_end=page),
        mime_type=FileType.PDF,
        strategy="PlainPdfExtractionStrategy",
    )


def _make_leaf(page: int = 1) -> TreeNode:
    return TreeNode(content=f"leaf {page}", level=0, chunk=_make_chunk(page))


def _make_tree(document_id=None) -> DocumentTree:
    """Build a simple 3-node tree: root → [leaf1, leaf2]"""
    leaf1 = _make_leaf(1)
    leaf2 = _make_leaf(2)
    root = TreeNode(content="root", level=1, children=[leaf1, leaf2])
    return DocumentTree(
        root=root,
        mime_type=FileType.PDF,
        document_id=document_id or uuid4(),
    )


@pytest.fixture
def store() -> InMemoryGraphStore:
    return InMemoryGraphStore()


@pytest.fixture
def tree() -> DocumentTree:
    return _make_tree()


class TestInMemoryGraphStoreSaveGet:
    def test_save_and_get_returns_tree(self, store, tree):
        store.save(tree)
        result = store.get(tree.document_id)
        assert result is not None
        assert result.document_id == tree.document_id

    def test_get_returns_none_for_missing_tree(self, store):
        assert store.get(uuid4()) is None

    def test_save_overwrites_existing_tree(self, store):
        doc_id = uuid4()
        tree1 = _make_tree(document_id=doc_id)
        tree2 = _make_tree(document_id=doc_id)
        tree2.root.content = "updated root"
        store.save(tree1)
        store.save(tree2)
        result = store.get(doc_id)
        assert result.root.content == "updated root"


class TestInMemoryGraphStoreDeleteExists:
    def test_exists_returns_true_after_save(self, store, tree):
        store.save(tree)
        assert store.exists(tree.document_id) is True

    def test_exists_returns_false_for_missing_tree(self, store):
        assert store.exists(uuid4()) is False

    def test_delete_removes_tree(self, store, tree):
        store.save(tree)
        store.delete(tree.document_id)
        assert store.get(tree.document_id) is None

    def test_delete_is_noop_for_missing_tree(self, store):
        store.delete(uuid4())

    def test_exists_returns_false_after_delete(self, store, tree):
        store.save(tree)
        store.delete(tree.document_id)
        assert store.exists(tree.document_id) is False


class TestInMemoryGraphStoreGetRoot:
    def test_get_root_returns_root_node(self, store, tree):
        store.save(tree)
        root = store.get_root(tree.document_id)
        assert root is not None
        assert root.id == tree.root.id

    def test_get_root_returns_none_for_missing_tree(self, store):
        assert store.get_root(uuid4()) is None

    def test_get_root_returns_none_after_delete(self, store, tree):
        store.save(tree)
        store.delete(tree.document_id)
        assert store.get_root(tree.document_id) is None


class TestInMemoryGraphStoreGetNode:
    def test_get_node_returns_root(self, store, tree):
        store.save(tree)
        node = store.get_node(tree.root.id)
        assert node is not None
        assert node.id == tree.root.id

    def test_get_node_returns_leaf(self, store, tree):
        store.save(tree)
        leaf = tree.root.children[0]
        node = store.get_node(leaf.id)
        assert node is not None
        assert node.id == leaf.id

    def test_get_node_returns_none_for_missing_id(self, store, tree):
        store.save(tree)
        assert store.get_node(uuid4()) is None

    def test_get_node_returns_none_after_delete(self, store, tree):
        store.save(tree)
        root_id = tree.root.id
        store.delete(tree.document_id)
        assert store.get_node(root_id) is None


class TestInMemoryGraphStoreGetChildren:
    def test_get_children_returns_direct_children(self, store, tree):
        store.save(tree)
        children = store.get_children(tree.root.id)
        assert len(children) == 2

    def test_get_children_returns_empty_for_leaf(self, store, tree):
        store.save(tree)
        leaf = tree.root.children[0]
        children = store.get_children(leaf.id)
        assert children == []

    def test_get_children_returns_empty_for_missing_node(self, store, tree):
        store.save(tree)
        assert store.get_children(uuid4()) == []

    def test_get_children_returns_only_direct_children(self, store):
        grandchild = _make_leaf(1)
        child = TreeNode(content="child", level=1, children=[grandchild])
        root = TreeNode(content="root", level=2, children=[child])
        tree = DocumentTree(root=root, mime_type=FileType.PDF, document_id=uuid4())
        store.save(tree)
        children = store.get_children(root.id)
        assert len(children) == 1
        assert children[0].id == child.id