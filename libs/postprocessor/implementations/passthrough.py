from libs.postprocessor.base import Postprocessor


class PassthroughPostprocessor(Postprocessor):
    """Returns text unchanged. Used as the default when no postprocessor is configured."""

    def process(self, text: str) -> str:
        return text