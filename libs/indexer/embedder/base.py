from abc import ABC, abstractmethod


class Embedder(ABC):
    @property
    @abstractmethod
    def dimension(self) -> int:
        """The dimensionality of the produced embeddings."""

    @abstractmethod
    def embed(self, text: str) -> list[float]:
        """Embed a single text. Returns a vector of length dimension. Never raises."""

    @abstractmethod
    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Embed multiple texts. Returns one embedding per input text. Never raises."""