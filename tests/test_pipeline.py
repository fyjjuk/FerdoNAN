"""
Tests para core/pipeline.py
"""
import pytest
from unittest.mock import Mock, patch, MagicMock


class TestPipeline:
    """Pruebas para el pipeline de procesamiento"""
    
    def setup_method(self):
        """Configuración inicial"""
        self.mock_agent = Mock()
        self.mock_agent.id = "test_agent"
        self.mock_agent.llm_client = Mock()
        
        # Mocks para dependencias
        self.mock_ingress = Mock()
        self.mock_ingress.evaluate.return_value = True
        
        self.mock_egress = Mock()
        self.mock_egress.evaluate.return_value = True
        
        self.mock_semantic = Mock()
        self.mock_semantic.evaluate_and_replace.return_value = "Filtered response"
        
        self.mock_gatekeeper = Mock()
        self.mock_gatekeeper.verify.return_value = True
        
        self.mock_cache = Mock()
        self.mock_cache.get.return_value = None
        
        self.mock_rag = Mock()
        self.core_config = {}
    
    def test_pipeline_ingress_blocked(self):
        """Verificar que el pipeline bloquea entrada maliciosa"""
        from core.pipeline import run_pipeline
        
        self.mock_ingress.evaluate.return_value = False
        
        with patch('core.pipeline.create_router') as mock_create_router, \
             patch('core.pipeline.create_sanitizer') as mock_create_sanitizer:
            
            mock_sanitizer = Mock()
            mock_sanitizer.clean.return_value = "bad input"
            mock_create_sanitizer.return_value = mock_sanitizer
            
            with pytest.raises(PermissionError, match="Entrada bloqueada por Firewall Ingress"):
                run_pipeline(
                    agent=self.mock_agent,
                    raw_input="bad input",
                    ingress=self.mock_ingress,
                    egress=self.mock_egress,
                    semantic=self.mock_semantic,
                    gatekeeper=self.mock_gatekeeper,
                    cache=self.mock_cache,
                    rag_engine=self.mock_rag,
                    core_config=self.core_config
                )
    
    def test_pipeline_egress_blocked(self):
        """Verificar que el pipeline bloquea salida peligrosa"""
        from core.pipeline import run_pipeline
        
        # Parchear los imports internos de pipeline.py
        with patch('core.pipeline.create_router') as mock_create_router, \
             patch('core.pipeline.create_sanitizer') as mock_create_sanitizer, \
             patch('orchestration.resource_manager.ResourceScheduler') as mock_scheduler, \
             patch('services.executor.factory.create_executor') as mock_create_executor:
            
            mock_router = Mock()
            mock_router.route.return_value = ("test_route", 0.9, {})
            mock_create_router.return_value = mock_router
            
            mock_sanitizer = Mock()
            mock_sanitizer.clean.return_value = "input"
            mock_create_sanitizer.return_value = mock_sanitizer
            
            mock_scheduler_instance = Mock()
            mock_scheduler_instance.can_run_parallel.return_value = (True, "")
            mock_scheduler.return_value = mock_scheduler_instance
            
            mock_executor = Mock()
            mock_executor.execute.return_value = "Dangerous output"
            mock_create_executor.return_value = mock_executor
            
            self.mock_egress.evaluate.return_value = False
            
            result, metadata = run_pipeline(
                agent=self.mock_agent,
                raw_input="input",
                ingress=self.mock_ingress,
                egress=self.mock_egress,
                semantic=self.mock_semantic,
                gatekeeper=self.mock_gatekeeper,
                cache=self.mock_cache,
                rag_engine=self.mock_rag,
                core_config=self.core_config
            )
            
            assert result == "ERROR_SEGURIDAD_EGRESS"
            assert metadata["status"] == "blocked"
    
    def test_pipeline_gatekeeper_rejected(self):
        """Verificar que el pipeline rechaza cuando Gatekeeper deniega"""
        from core.pipeline import run_pipeline
        
        with patch('core.pipeline.create_router') as mock_create_router, \
             patch('core.pipeline.create_sanitizer') as mock_create_sanitizer, \
             patch('orchestration.resource_manager.ResourceScheduler') as mock_scheduler:
            
            mock_router = Mock()
            mock_router.route.return_value = ("critical_route", 0.9, {
                "gatekeeper_required": True
            })
            mock_create_router.return_value = mock_router
            
            mock_sanitizer = Mock()
            mock_sanitizer.clean.return_value = "input"
            mock_create_sanitizer.return_value = mock_sanitizer
            
            mock_scheduler_instance = Mock()
            mock_scheduler_instance.can_run_parallel.return_value = (True, "")
            mock_scheduler.return_value = mock_scheduler_instance
            
            self.mock_gatekeeper.verify.return_value = False
            
            with pytest.raises(PermissionError, match="Acción rechazada por Gatekeeper"):
                run_pipeline(
                    agent=self.mock_agent,
                    raw_input="input",
                    ingress=self.mock_ingress,
                    egress=self.mock_egress,
                    semantic=self.mock_semantic,
                    gatekeeper=self.mock_gatekeeper,
                    cache=self.mock_cache,
                    rag_engine=self.mock_rag,
                    core_config=self.core_config
                )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
