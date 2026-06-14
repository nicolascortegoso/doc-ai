from abc import ABC, abstractmethod

from libs.distiller.analyzer.models import AnalyzerInput


class Analyzer(ABC):
    @abstractmethod
    def analyze(self, input: AnalyzerInput) -> str:
        """Analyze content and return extracted information. Never raises."""