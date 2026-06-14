import math

import pytest

from libs.embedder.implementations.random import RandomEmbedder


@pytest.fixture
def embedder() -> RandomEmbedder:
    return RandomEmbedder()


class TestRandomEmbedderConstruction:
    def test_default_dimension_is_768(self, embedder):
        assert embedder.dimension == 768

    def test_custom_dimension(self):
        assert RandomEmbedder(dimension=128).dimension == 128


class TestRandomEmbedderEmbed:
    def test_embed_returns_list_of_floats(self, embedder):
        result = embedder.embed("hello world")
        assert isinstance(result, list)
        assert all(isinstance(x, float) for x in result)

    def test_embed_returns_correct_dimension(self, embedder):
        result = embedder.embed("hello world")
        assert len(result) == embedder.dimension

    def test_embed_returns_unit_vector(self, embedder):
        result = embedder.embed("hello world")
        norm = math.sqrt(sum(x * x for x in result))
        assert abs(norm - 1.0) < 1e-6

    def test_embed_never_raises(self, embedder):
        result = embedder.embed("")
        assert isinstance(result, list)

    def test_embed_custom_dimension(self):
        embedder = RandomEmbedder(dimension=32)
        result = embedder.embed("test")
        assert len(result) == 32


class TestRandomEmbedderEmbedBatch:
    def test_embed_batch_returns_correct_count(self, embedder):
        texts = ["hello", "world", "foo"]
        result = embedder.embed_batch(texts)
        assert len(result) == 3

    def test_embed_batch_each_embedding_has_correct_dimension(self, embedder):
        result = embedder.embed_batch(["a", "b", "c"])
        for embedding in result:
            assert len(embedding) == embedder.dimension

    def test_embed_batch_each_embedding_is_unit_vector(self, embedder):
        result = embedder.embed_batch(["a", "b"])
        for embedding in result:
            norm = math.sqrt(sum(x * x for x in embedding))
            assert abs(norm - 1.0) < 1e-6

    def test_embed_batch_empty_input_returns_empty_list(self, embedder):
        assert embedder.embed_batch([]) == []

    def test_embed_batch_single_text(self, embedder):
        result = embedder.embed_batch(["single"])
        assert len(result) == 1
        assert len(result[0]) == embedder.dimension