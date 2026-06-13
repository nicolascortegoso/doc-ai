from libs.postprocessor.implementations.passthrough import PassthroughPostprocessor


class TestPassthroughPostprocessor:
    def setup_method(self):
        self.postprocessor = PassthroughPostprocessor()

    def test_returns_text_unchanged(self):
        assert self.postprocessor.process("Hello, world!") == "Hello, world!"

    def test_returns_empty_string_unchanged(self):
        assert self.postprocessor.process("") == ""

    def test_returns_whitespace_unchanged(self):
        assert self.postprocessor.process("  \n\t  ") == "  \n\t  "

    def test_never_raises(self):
        result = self.postprocessor.process("any text \x00 with special chars")
        assert isinstance(result, str)