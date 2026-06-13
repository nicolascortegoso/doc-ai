from libs.splitter.base import TextSplitter


class CharacterTextSplitter(TextSplitter):
    """Returns the position unchanged — cuts at the exact character boundary.

    Used as the default when no real splitter is configured.
    """

    def find_split(self, text: str, position: int) -> int:
        return position