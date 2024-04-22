from abc import ABC, abstractmethod


class IDocumentSelector(ABC):
    @abstractmethod
    def select(self) -> str:
        pass
