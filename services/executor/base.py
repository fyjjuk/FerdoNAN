from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseExecutor(ABC):
    """Clase base para ejecutores de rutas."""
    @abstractmethod
    def execute(self, agent_manifest, route_data: Dict[str, Any], cleaned_input: str, router, rag_engine) -> str:
        """Ejecuta la ruta y devuelve la salida."""
        pass
