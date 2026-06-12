from libs.language.base import LanguageDetector


class DummyLanguageDetector(LanguageDetector):
    """Always returns 'en'. Used as the default when no real detector is configured."""

    def detect(self, text: str) -> str:
        return "en"
