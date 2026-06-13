import pytest

from libs.reducer.implementations.truncating import TruncatingReducer
from libs.reducer.models import ReducerInput


@pytest.fixture
def reducer() -> TruncatingReducer:
    return TruncatingReducer()


class TestTruncatingReducerConstruction:
    def test_default_max_chars_is_200(self):
        assert TruncatingReducer()._max_chars == 200

    def test_custom_max_chars(self):
        assert TruncatingReducer(max_chars_per_text=50)._max_chars == 50


class TestTruncatingReducerReduce:
    def test_returns_string(self, reducer):
        result = reducer.reduce(ReducerInput(texts=["hello", "world"]))
        assert isinstance(result, str)

    def test_joins_texts_with_space(self, reducer):
        result = reducer.reduce(ReducerInput(texts=["hello", "world"]))
        assert result == "hello world"

    def test_truncates_text_exceeding_max_chars(self):
        reducer = TruncatingReducer(max_chars_per_text=5)
        result = reducer.reduce(ReducerInput(texts=["hello world", "foo bar"]))
        assert result == "hello foo b"

    def test_does_not_truncate_text_within_max_chars(self, reducer):
        result = reducer.reduce(ReducerInput(texts=["short"]))
        assert result == "short"

    def test_output_length_constraint(self):
        reducer = TruncatingReducer(max_chars_per_text=10)
        texts = ["a" * 100, "b" * 100, "c" * 100]
        result = reducer.reduce(ReducerInput(texts=texts))
        total_input = sum(len(t) for t in texts)
        assert len(result) < total_input

    def test_empty_texts_returns_empty_string(self, reducer):
        result = reducer.reduce(ReducerInput(texts=[]))
        assert result == ""

    def test_single_text_returns_truncated(self):
        reducer = TruncatingReducer(max_chars_per_text=5)
        result = reducer.reduce(ReducerInput(texts=["hello world"]))
        assert result == "hello"

    def test_never_raises(self, reducer):
        result = reducer.reduce(ReducerInput(texts=["any text"]))
        assert isinstance(result, str)

    def test_ignores_prompt_template(self, reducer):
        result = reducer.reduce(ReducerInput(
            texts=["hello"],
            prompt_template="Summarize: {texts}",
        ))
        assert result == "hello"

    def test_ignores_context(self, reducer):
        result = reducer.reduce(ReducerInput(
            texts=["hello"],
            context={"level": 1},
        ))
        assert result == "hello"