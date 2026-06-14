from libs.distiller.composer.implementations.default import DefaultComposer
from libs.distiller.composer.models import ComposerInput


class TestDefaultComposer:
    def test_returns_empty_string(self):
        composer = DefaultComposer()
        result = composer.compose(ComposerInput(content="text", instruction="refine"))
        assert result == ""

    def test_never_raises(self):
        composer = DefaultComposer()
        result = composer.compose(ComposerInput(content="", instruction=""))
        assert isinstance(result, str)

    def test_with_context(self):
        composer = DefaultComposer()
        result = composer.compose(ComposerInput(
            content="text",
            instruction="refine",
            context={"key": "value"},
        ))
        assert result == ""