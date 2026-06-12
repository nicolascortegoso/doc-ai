import pytest

from libs.language.implementations.dummy import DummyLanguageDetector


class TestDummyLanguageDetector:
    def setup_method(self):
        self.detector = DummyLanguageDetector()

    def test_returns_en_for_english_text(self):
        assert self.detector.detect("Hello, world!") == "en"

    def test_returns_en_for_non_english_text(self):
        assert self.detector.detect("Bonjour le monde") == "en"

    def test_returns_en_for_empty_string(self):
        assert self.detector.detect("") == "en"

    def test_never_raises(self):
        # Should not raise for any input
        result = self.detector.detect("こんにちは")
        assert result == "en"
