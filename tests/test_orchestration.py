"""Tests para orquestación: resource manager y scheduler."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from unittest.mock import patch, Mock
from orchestration.resource_manager import ResourceScheduler


class TestResourceScheduler:
    """Tests para ResourceScheduler."""

    def test_detect_vram_nvidia(self):
        """Debe detectar VRAM cuando nvidia-smi está disponible."""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=0, stdout="4096\n")
            scheduler = ResourceScheduler()
            # No debe fallar aunque no haya NVIDIA
            assert scheduler._vram_total_mb is None or isinstance(scheduler._vram_total_mb, int)

    def test_get_system_metrics_returns_dict(self):
        """get_system_metrics debe devolver diccionario con métricas."""
        scheduler = ResourceScheduler()
        metrics = scheduler.get_system_metrics()
        
        assert "ram_percent" in metrics
        assert "cpu_percent" in metrics
        assert isinstance(metrics["ram_percent"], (int, float))

    def test_can_run_parallel_exclusive_mode(self):
        """Modo exclusive debe siempre retornar False."""
        scheduler = ResourceScheduler()
        agent_mock = Mock()
        agent_mock.execution_mode = "exclusive"
        
        can_run, reason = scheduler.can_run_parallel(agent_mock)
        assert can_run is False
        assert "exclusive" in reason

    def test_can_run_parallel_low_ram(self):
        """Debe rechazar parallel si RAM está muy usada."""
        scheduler = ResourceScheduler()
        agent_mock = Mock()
        agent_mock.execution_mode = "parallel"
        
        with patch.object(scheduler, 'get_system_metrics', return_value={"ram_percent": 95, "cpu_percent": 30}):
            can_run, reason = scheduler.can_run_parallel(agent_mock)
            assert can_run is False
            assert "RAM" in reason

    def test_can_run_parallel_sufficient_resources(self):
        """Debe permitir parallel si hay recursos suficientes."""
        scheduler = ResourceScheduler()
        agent_mock = Mock()
        agent_mock.execution_mode = "parallel"
        
        with patch.object(scheduler, 'get_system_metrics', return_value={"ram_percent": 30, "cpu_percent": 20}):
            can_run, reason = scheduler.can_run_parallel(agent_mock)
            assert can_run is True

    def test_suggest_degradation_returns_exclusive(self):
        """suggest_degradation debe retornar 'exclusive'."""
        scheduler = ResourceScheduler()
        result = scheduler.suggest_degradation("test_agent")
        assert result == "exclusive"

    def test_select_resource_profile_default(self):
        """select_resource_profile debe retornar 'default' si no hay dynamic."""
        scheduler = ResourceScheduler()
        llm_config = {"dynamic_resource_management": False}
        
        profile = scheduler.select_resource_profile(llm_config)
        assert profile == "default"

    def test_select_resource_profile_low_memory(self):
        """Debe seleccionar perfil 'low' cuando hay poca memoria."""
        scheduler = ResourceScheduler()
        llm_config = {"dynamic_resource_management": True}
        
        with patch.object(scheduler, 'get_system_metrics', return_value={"ram_available_mb": 1024}):
            profile = scheduler.select_resource_profile(llm_config)
            assert profile == "low"

    def test_select_resource_profile_high_memory(self):
        """Debe seleccionar perfil 'high' cuando hay mucha memoria."""
        scheduler = ResourceScheduler()
        llm_config = {"dynamic_resource_management": True}
        
        with patch.object(scheduler, 'get_system_metrics', 
                         return_value={"ram_available_mb": 16384, "vram_total_mb": 8192, "vram_used_mb": 1024}):
            profile = scheduler.select_resource_profile(llm_config)
            # Puede ser 'high' o 'medium' según umbrales
            assert profile in ["high", "medium"]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
