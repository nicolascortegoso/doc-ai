from abc import ABC, abstractmethod

from libs.distiller.composer.models import ComposerInput


class Composer(ABC):
    @abstractmethod
    def compose(self, input: ComposerInput) -> str:
        """Compose structured output from extracted knowledge. Never raises."""