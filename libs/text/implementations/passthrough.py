from libs.text.base import TextCleaner


class PassthroughTextCleaner(TextCleaner):
    """Returns text unchanged. Used as the default when no real cleaner is configured."""

    def clean(self, text: str) -> str:
        return text