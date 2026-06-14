from libs.chunker.splitter.implementations.character import CharacterSplitter


class TestCharacterSplitter:
    def setup_method(self):
        self.splitter = CharacterSplitter()

    def test_returns_position_unchanged(self):
        assert self.splitter.find_split("hello world", 5) == 5

    def test_returns_zero_position(self):
        assert self.splitter.find_split("hello world", 0) == 0

    def test_returns_end_of_text_position(self):
        text = "hello world"
        assert self.splitter.find_split(text, len(text)) == len(text)

    def test_never_raises_for_any_input(self):
        result = self.splitter.find_split("some text", 3)
        assert isinstance(result, int)

    def test_returns_position_for_empty_string(self):
        assert self.splitter.find_split("", 0) == 0