"""
Legacy wrapper para RAGEngine.
Mantiene compatibilidad con código que importa desde services.vector_store.
"""

from services.rag import RAGEngine

# Re-exportar para mantener compatibilidad
__all__ = ['RAGEngine']
