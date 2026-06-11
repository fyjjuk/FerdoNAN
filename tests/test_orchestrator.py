"""Tests para core/orchestrator.py."""

import pytest
from unittest.mock import Mock, patch


class TestOrchestrator:
    """Pruebas para FerdoNANEngine (Orchestrator)."""
    
    def test_initialization(self):
        """Verificar que el orquestador se inicializa correctamente."""
        from core.orchestrator import FerdoNANEngine
        from security.filters.ingress import IngressFilter
        from security.filters.egress import EgressFilter
        from security.filters.semantic import SemanticOutputFilter
        
        ingress = Mock(spec=IngressFilter)
        egress = Mock(spec=EgressFilter)
        semantic = Mock(spec=SemanticOutputFilter)
        
        engine = FerdoNANEngine(ingress, egress, semantic)
        assert engine.ingress == ingress
        assert engine.egress == egress
        assert engine.semantic == semantic
        assert engine.cache is None
    
    def test_initialization_with_cache(self):
        """Verificar que se puede pasar un caché opcional."""
        from core.orchestrator import FerdoNANEngine
        from security.filters.ingress import IngressFilter
        from security.filters.egress import EgressFilter
        from security.filters.semantic import SemanticOutputFilter
        
        ingress = Mock(spec=IngressFilter)
        egress = Mock(spec=EgressFilter)
        semantic = Mock(spec=SemanticOutputFilter)
        mock_cache = Mock()
        
        engine = FerdoNANEngine(ingress, egress, semantic, cache=mock_cache)
        assert engine.cache == mock_cache
    
    def test_set_rag_engine(self):
        """Verificar que se puede cambiar el motor RAG."""
        from core.orchestrator import FerdoNANEngine
        from security.filters.ingress import IngressFilter
        from security.filters.egress import EgressFilter
        from security.filters.semantic import SemanticOutputFilter
        
        ingress = Mock(spec=IngressFilter)
        egress = Mock(spec=EgressFilter)
        semantic = Mock(spec=SemanticOutputFilter)
        
        engine = FerdoNANEngine(ingress, egress, semantic)
        mock_rag = Mock()
        engine.set_rag_engine(mock_rag)
        assert engine.rag_engine == mock_rag


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
