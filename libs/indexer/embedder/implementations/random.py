import math
import random

from libs.indexer.embedder.base import Embedder


class RandomEmbedder(Embedder):
    """Returns random unit vectors of configurable dimension.

    Used as the default when no real embedder is configured.

    Args:
        dimension: Dimensionality of the produced embeddings. Default: 768.
    """

    def __init__(self, dimension: int = 768) -> None:
        self._dimension = dimension

    @property
    def dimension(self) -> int:
        return self._dimension

    def embed(self, text: str) -> list[float]:
        return self._random_unit_vector()

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return [self._random_unit_vector() for _ in texts]

    def _random_unit_vector(self) -> list[float]:
        vec = [random.gauss(0, 1) for _ in range(self._dimension)]
        norm = math.sqrt(sum(x * x for x in vec))
        if norm == 0:
            vec[0] = 1.0
            return vec
        return [x / norm for x in vec]