from libs.distiller.analyzer.implementations.default import DefaultAnalyzer
from libs.distiller.analyzer.models import AnalyzerInput


class TestDefaultAnalyzer:
    def test_returns_empty_string(self):
        analyzer = DefaultAnalyzer()
        result = analyzer.analyze(AnalyzerInput(content="text", instruction="extract"))
        assert result == ""

    def test_never_raises(self):
        analyzer = DefaultAnalyzer()
        result = analyzer.analyze(AnalyzerInput(content="", instruction=""))
        assert isinstance(result, str)

    def test_with_context(self):
        analyzer = DefaultAnalyzer()
        result = analyzer.analyze(AnalyzerInput(
            content="text",
            instruction="extract",
            context={"key": "value"},
        ))
        assert result == ""