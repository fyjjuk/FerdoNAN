from abc import ABC, abstractmethod
from typing import Tuple, Dict, Any, List, Optional

class BaseRouter(ABC):
    @abstractmethod
    def route(self, routes: List[Dict[str, Any]], user_input: str, threshold: float) -> Tuple[str, float, Dict]:
        pass
