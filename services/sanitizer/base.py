from abc import ABC, abstractmethod

class BaseSanitizer(ABC):
    @abstractmethod
    def clean(self, user_input: str) -> str:
        pass
