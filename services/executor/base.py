"""
Clase base para ejecutores de rutas.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseExecutor(ABC):
    """Clase base para todos los ejecutores."""
    
    @abstractmethod
    def execute(self, agent_manifest, route_data: Dict[str, Any], 
                cleaned_input: str, router, rag_engine) -> str:
        """
        Ejecuta una ruta y retorna la respuesta.
        
        Args:
            agent_manifest: Manifiesto del agente
            route_data: Datos de la ruta
            cleaned_input: Input sanitizado
            router: Router para determinar necesidades
            rag_engine: Motor RAG para contexto
            
        Returns:
            str: Respuesta generada
        """
        pass
