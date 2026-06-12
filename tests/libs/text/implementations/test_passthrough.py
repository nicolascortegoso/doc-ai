from libs.text.implementations.passthrough import PassthroughTextCleaner


class TestPassthroughTextCleaner:
    def setup_method(self):
        self.cleaner = PassthroughTextCleaner()

    def test_returns_text_unchanged(self):
        assert self.cleaner.clean("Hello, world!") == "Hello, world!"

    def test_returns_empty_string_unchanged(self):
        assert self.cleaner.clean("") == ""

    def test_returns_whitespace_unchanged(self):
        assert self.cleaner.clean("  \n\t  ") == "  \n\t  "

    def test_never_raises(self):
        result = self.cleaner.clean("any text \x00 with special chars")
        assert isinstance(result, str)