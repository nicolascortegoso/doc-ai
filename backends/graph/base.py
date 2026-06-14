from abc import ABC, abstractmethod
from uuid import UUID

from common.models import DocumentTree, TreeNode


class GraphStore(ABC):
    """Abstract base for graph store implementations.

    Stores DocumentTree objects as graph structures and supports
    tree-level and node-level operations.
    """

    @abstractmethod
    def save(self, tree: DocumentTree) -> None:
        """Persist the full tree."""

    @abstractmethod
    def get(self, document_id: UUID) -> DocumentTree | None:
        """Retrieve a tree by document ID. Returns None if not found."""

    @abstractmethod
    def delete(self, document_id: UUID) -> None:
        """Remove a tree. No-op if not found."""

    @abstractmethod
    def exists(self, document_id: UUID) -> bool:
        """Returns True if a tree exists for the given document ID."""

    @abstractmethod
    def get_node(self, node_id: UUID) -> TreeNode | None:
        """Retrieve a node by ID. Returns None if not found."""

    @abstractmethod
    def get_children(self, node_id: UUID) -> list[TreeNode]:
        """Retrieve direct children of a node. Returns empty list if not found."""

    @abstractmethod
    def get_root(self, document_id: UUID) -> TreeNode | None:
        """Retrieve the root node of a tree. Returns None if not found."""