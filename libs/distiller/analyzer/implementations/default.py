from libs.distiller.analyzer.base import Analyzer
from libs.distiller.analyzer.models import AnalyzerInput


class DefaultAnalyzer(Analyzer):
    """No-op analyzer. Returns empty string.

    Used as the default when no real analyzer is configured.
    """

    def analyze(self, input: AnalyzerInput) -> str:
        return ""