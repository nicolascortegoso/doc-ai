from libs.merger.reducer.base import Reducer
from libs.merger.reducer.models import ReducerInput


class TruncatingReducer(Reducer):
    """Truncates each text to max_chars_per_text characters and joins with a space.

    Produces a genuinely reduced output without requiring an LLM.

    Args:
        max_chars_per_text: Maximum characters to retain from each input text.
            Default: 200.
    """

    def __init__(self, max_chars_per_text: int = 200) -> None:
        self._max_chars = max_chars_per_text

    def reduce(self, input: ReducerInput) -> str:
        try:
            return " ".join(text[:self._max_chars] for text in input.texts)
        except Exception:
            return ""