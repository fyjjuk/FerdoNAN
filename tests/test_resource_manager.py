"""Tests para el gestor de recursos."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from unittest.mock import patch, Mock
from orchestration.resource_manager import ResourceScheduler


class MockAgentManifest:
    def __init__(self, mode="parallel"):
        self.execution_mode = mode


class TestResourceScheduler:
    """Tests para ResourceScheduler."""

    def test_init_no_vram_detection(self):
        """Debe inicializarse incluso sin detección de VRAM."""
        scheduler = ResourceScheduler()
        assert scheduler._vram_total_mb is None or isinstance(scheduler._vram_total_mb, int)

    def test_get_system_metrics_returns_dict(self):
        """Debe retornar un diccionario con métricas."""
        scheduler = ResourceScheduler()
        metrics = scheduler.get_system_metrics()
        
        assert "ram_percent" in metrics
        assert "cpu_percent" in metrics
        assert isinstance(metrics["ram_percent"], (int, float))

    def test_can_run_parallel_exclusive_mode(self):
        """Modo exclusive siempre debe retornar False."""
        scheduler = ResourceScheduler()
        agent = MockAgentManifest(mode="exclusive")
        
        can_run, reason = scheduler.can_run_parallel(agent)
        assert can_run is False
        assert "exclusive" in reason

    def test_can_run_parallel_low_ram(self):
        """Debe rechazar parallel si la RAM está muy ocupada."""
        scheduler = ResourceScheduler()
        agent = MockAgentManifest(mode="parallel")
        
        with patch.object(scheduler, 'get_system_metrics', return_value={"ram_percent": 95, "cpu_percent": 30}):
            can_run, reason = scheduler.can_run_parallel(agent)
            assert can_run is False
            assert "RAM" in reason

    def test_can_run_parallel_sufficient_ram(self):
        """Debe permitir parallel si hay RAM suficiente."""
        scheduler = ResourceScheduler()
        agent = MockAgentManifest(mode="parallel")
        
        with patch.object(scheduler, 'get_system_metrics', return_value={"ram_percent": 30, "cpu_percent": 20}):
            can_run, reason = scheduler.can_run_parallel(agent)
            assert can_run is True

    def test_suggest_degradation_returns_exclusive(self):
        """Debe sugerir degradación a modo exclusive."""
        scheduler = ResourceScheduler()
        result = scheduler.suggest_degradation("test_agent")
        assert result == "exclusive"

    def test_select_resource_profile_default(self):
        """Sin gestión dinámica, debe retornar 'default'."""
        scheduler = ResourceScheduler()
        llm_config = {"dynamic_resource_management": False}
        
        profile = scheduler.select_resource_profile(llm_config)
        assert profile == "default"

    def test_select_resource_profile_low_memory(self):
        """Con poca memoria, debe elegir perfil 'low'."""
        scheduler = ResourceScheduler()
        llm_config = {"dynamic_resource_management": True}
        
        with patch.object(scheduler, 'get_system_metrics', return_value={"ram_available_mb": 1024}):
            profile = scheduler.select_resource_profile(llm_config)
            assert profile == "low"

    def test_select_resource_profile_high_memory(self):
        """Con mucha memoria, debe elegir perfil 'high' o 'medium'."""
        scheduler = ResourceScheduler()
        llm_config = {"dynamic_resource_management": True}
        
        with patch.object(scheduler, 'get_system_metrics', 
                         return_value={"ram_available_mb": 16384, "vram_total_mb": 8192, "vram_used_mb": 1024}):
            profile = scheduler.select_resource_profile(llm_config)
            assert profile in ["high", "medium"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
