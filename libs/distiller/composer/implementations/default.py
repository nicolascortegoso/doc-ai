from libs.distiller.composer.base import Composer
from libs.distiller.composer.models import ComposerInput


class DefaultComposer(Composer):
    """No-op composer. Returns empty string.

    Used as the default when no real composer is configured.
    """

    def compose(self, input: ComposerInput) -> str:
        return ""