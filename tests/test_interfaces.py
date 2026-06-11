"""
Tests para verificar que las implementaciones cumplen con las interfaces.
"""

import pytest
from core.interfaces import (
    LLMClientInterface, RAGEngineInterface, CacheInterface,
    GatekeeperInterface, RouterInterface, ExecutorInterface, SanitizerInterface
)


class TestInterfaces:
    """Verifica que las clases existentes implementen las interfaces correctamente."""
    
    def test_llm_clients_implement_interface(self):
        """Verificar que los clientes LLM implementan la interfaz."""
        from services.llm_providers.ollama import OllamaClient
        from services.llm_providers.gemini import GeminiClient
        from services.llm_providers.groq import GroqClient
        
        # Verificar que las clases tienen los métodos requeridos
        assert hasattr(OllamaClient, 'generate_response')
        assert hasattr(GeminiClient, 'generate_response')
        assert hasattr(GroqClient, 'generate_response')
    
    def test_rag_engine_implements_interface(self):
        """Verificar que RAGEngine implementa la interfaz."""
        from services.rag import RAGEngine
        
        assert hasattr(RAGEngine, 'index_document')
        assert hasattr(RAGEngine, 'rag_query')
        assert hasattr(RAGEngine, 'delete_namespace')
    
    def test_cache_implements_interface(self):
        """Verificar que ResponseCache implementa la interfaz."""
        from persistence.cache import ResponseCache
        
        cache = ResponseCache()
        assert hasattr(cache, 'get')
        assert hasattr(cache, 'set')
        assert hasattr(cache, 'invalidate')
    
    def test_gatekeeper_implements_interface(self):
        """Verificar que Gatekeeper implementa la interfaz."""
        from security.auth.gatekeeper import Gatekeeper
        
        gatekeeper = Gatekeeper()
        assert hasattr(gatekeeper, 'verify')
    
    def test_router_implements_interface(self):
        """Verificar que Router implementa la interfaz."""
        from services.router.intent_router import Router
        
        router = Router(mode="keyword")
        assert hasattr(router, 'route')
        assert hasattr(router, 'needs_rag_context')
    
    def test_executor_implements_interface(self):
        """Verificar que ejecutores implementan la interfaz."""
        from services.executor.cognitive import LLMExecutor
        from services.executor.script_executor import ScriptExecutor
        
        assert hasattr(LLMExecutor, 'execute')
        assert hasattr(ScriptExecutor, 'execute')
    
    def test_sanitizer_implements_interface(self):
        """Verificar que sanitizadores implementan la interfaz."""
        from services.sanitizer.simple import SimpleSanitizer
        from services.sanitizer.llm import LLMSanitizer
        
        assert hasattr(SimpleSanitizer, 'clean')
        assert hasattr(LLMSanitizer, 'clean')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
