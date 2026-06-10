"""Tests para el motor principal FerdoNANEngine."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from unittest.mock import Mock, patch
from core.engine import FerdoNANEngine
from security.filters.ingress import IngressFilter
from security.filters.egress import EgressFilter
from security.filters.semantic import SemanticOutputFilter


class MockAgentManifest:
    def __init__(self):
        self.id = "test_agent"
        self.execution_mode = "parallel"
        self.execution_timeout = 30
        self.router_config = Mock()
        self.router_config.mode = "keyword"
        self.router_config.model = None
        self.router_config.threshold = 0.3
        self.sanitizer_config = Mock()
        self.sanitizer_config.enabled = True
        self.sanitizer_config.model = None
        self.llm_provider = {"name": "ollama", "model": "phi3:mini"}


@pytest.fixture
def mock_filters():
    ingress = Mock(spec=IngressFilter)
    ingress.evaluate.return_value = True
    egress = Mock(spec=EgressFilter)
    egress.evaluate.return_value = True
    semantic = Mock(spec=SemanticOutputFilter)
    semantic.evaluate_and_replace.side_effect = lambda x, y: x
    return ingress, egress, semantic


@pytest.fixture
def engine(mock_filters):
    ingress, egress, semantic = mock_filters
    return FerdoNANEngine(ingress, egress, semantic)


class TestFerdoNANEngine:
    """Tests para FerdoNANEngine."""

    def test_engine_initialization(self, engine):
        """Debe inicializarse correctamente."""
        assert engine is not None
        assert engine.scheduler is not None
        assert engine.cache is not None

    def test_set_rag_engine(self, engine):
        """Debe permitir establecer el motor RAG."""
        mock_rag = Mock()
        engine.set_rag_engine(mock_rag)
        assert engine.rag_engine == mock_rag

    @patch('core.engine.Router')
    @patch('core.engine.Sanitizer')
    def test_process_pipeline_ingress_blocked(self, mock_sanitizer, mock_router, engine, mock_filters):
        """Debe lanzar PermissionError si Ingress bloquea la entrada."""
        ingress, _, _ = mock_filters
        ingress.evaluate.return_value = False
        
        mock_manifest = MockAgentManifest()
        
        with pytest.raises(PermissionError, match="Entrada bloqueada por Firewall Ingress"):
            engine.process_pipeline(mock_manifest, "input peligroso")

    @patch('services.executor.factory.create_executor')
    @patch('core.engine.Router')
    @patch('core.engine.Sanitizer')
    def test_process_pipeline_successful(self, mock_sanitizer, mock_router, mock_executor_factory, engine):
        """Debe procesar el pipeline exitosamente."""
        # Configurar mocks
        mock_router_instance = Mock()
        mock_router_instance.route.return_value = ("test_route", 0.9, {"type": "cognitive"})
        mock_router.return_value = mock_router_instance
        
        mock_sanitizer_instance = Mock()
        mock_sanitizer_instance.clean.return_value = "input limpio"
        mock_sanitizer.return_value = mock_sanitizer_instance
        
        mock_executor = Mock()
        mock_executor.execute.return_value = "respuesta del agente"
        mock_executor_factory.return_value = mock_executor
        
        # Mock cache miss
        engine.cache.get = Mock(return_value=None)
        
        mock_manifest = MockAgentManifest()
        
        output, summary = engine.process_pipeline(mock_manifest, "consulta de prueba")
        
        assert output == "respuesta del agente"
        assert summary["route_id"] == "test_route"
        assert "execution_mode" in summary

    @patch('core.engine.Router')
    @patch('core.engine.Sanitizer')
    def test_process_pipeline_route_not_found(self, mock_sanitizer, mock_router, engine):
        """Debe propagar RouteNotFoundError."""
        from services.router.intent_router import RouteNotFoundError
        
        mock_router_instance = Mock()
        mock_router_instance.route.side_effect = RouteNotFoundError("No routes", [])
        mock_router.return_value = mock_router_instance
        
        mock_sanitizer_instance = Mock()
        mock_sanitizer_instance.clean.return_value = "input"
        mock_sanitizer.return_value = mock_sanitizer_instance
        
        mock_manifest = MockAgentManifest()
        
        with pytest.raises(RouteNotFoundError):
            engine.process_pipeline(mock_manifest, "consulta")

    @patch('services.executor.factory.create_executor')
    @patch('core.engine.Router')
    @patch('core.engine.Sanitizer')
    def test_process_pipeline_egress_blocks(self, mock_sanitizer, mock_router, mock_executor_factory, engine, mock_filters):
        """Debe retornar error si Egress bloquea la salida."""
        _, egress, _ = mock_filters
        egress.evaluate.return_value = False
        
        mock_router_instance = Mock()
        mock_router_instance.route.return_value = ("test_route", 0.9, {"type": "cognitive"})
        mock_router.return_value = mock_router_instance
        
        mock_sanitizer_instance = Mock()
        mock_sanitizer_instance.clean.return_value = "input"
        mock_sanitizer.return_value = mock_sanitizer_instance
        
        mock_executor = Mock()
        mock_executor.execute.return_value = "salida peligrosa"
        mock_executor_factory.return_value = mock_executor
        
        # Mock cache miss
        engine.cache.get = Mock(return_value=None)
        
        mock_manifest = MockAgentManifest()
        
        output, summary = engine.process_pipeline(mock_manifest, "consulta")
        
        assert output == "ERROR_SEGURIDAD_EGRESS"
        assert summary["status"] == "blocked"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
