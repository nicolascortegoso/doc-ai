from __future__ import annotations

from typing import ClassVar

from common.enums import FileType
from common.models import DocumentChunk, DocumentTree, TreeNode
from libs.merger.base import BaseMergingStrategy
from libs.merger.reducer.base import Reducer
from libs.merger.reducer.implementations.truncating import TruncatingReducer
from libs.merger.reducer.models import ReducerInput


class BottomUpMergingStrategy(BaseMergingStrategy):
    """Iteratively merges chunks bottom-up into a DocumentTree.

    Builds leaf nodes from DocumentChunk objects, then groups them into
    batches of branching_factor and reduces each batch into a parent node.
    Repeats until a single root node remains.

    A Reducer is injected at construction time to produce parent node content.
    Defaults to TruncatingReducer.

    Args:
        branching_factor: Number of nodes to merge per parent. Default: 4.
        reducer: Injected Reducer. Default: TruncatingReducer.
    """

    supported_mime_types: ClassVar[list[FileType]] = list(FileType)

    def __init__(
        self,
        branching_factor: int = 4,
        reducer: Reducer = None,
    ) -> None:
        if branching_factor < 2:
            raise ValueError(f"branching_factor must be >= 2, got {branching_factor}")
        self._branching_factor = branching_factor
        self._reducer = reducer or TruncatingReducer()

    def can_handle(self, chunks: list[DocumentChunk]) -> bool:
        return True

    def get_priority(self) -> int:
        return 1

    def merge(self, chunks: list[DocumentChunk]) -> DocumentTree:
        mime_type = chunks[0].mime_type

        nodes = [
            TreeNode(content=chunk.content, level=0, chunk=chunk)
            for chunk in chunks
        ]

        if len(nodes) == 1:
            return DocumentTree(root=nodes[0], mime_type=mime_type)

        level = 1
        while len(nodes) > 1:
            nodes = self._merge_level(nodes, level)
            level += 1

        return DocumentTree(root=nodes[0], mime_type=mime_type)

    def _merge_level(
        self, nodes: list[TreeNode], level: int
    ) -> list[TreeNode]:
        parents = []
        for i in range(0, len(nodes), self._branching_factor):
            batch = nodes[i:i + self._branching_factor]
            texts = [node.content for node in batch]
            content = self._reducer.reduce(ReducerInput(texts=texts))
            parent = TreeNode(
                content=content,
                level=level,
                children=batch,
            )
            parents.append(parent)
        return parents