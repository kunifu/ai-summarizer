from abc import ABC, abstractmethod


class IChatCompleter(ABC):
    @abstractmethod
    def complete(self, prompt: str) -> str:
        pass
