from abc import ABC, abstractmethod

from libs.merger.reducer.models import ReducerInput


class Reducer(ABC):
    @abstractmethod
    def reduce(self, input: ReducerInput) -> str:
        """Produces a single reduced representation from the input. Never raises."""