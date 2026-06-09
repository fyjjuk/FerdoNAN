#!/usr/bin/env python3
"""Tests de estrés y comportamiento fail-closed de los firewalls."""

import sys
import os
import tempfile
import pytest
from unittest.mock import Mock, patch

# Añadir el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from security.ingress import IngressFilter
from security.egress import EgressFilter
from security.semantic_output import SemanticOutputFilter
from security.rate_limiter import RateLimiter
from security.gatekeeper import Gatekeeper
from security.audit import ApprovalAudit


class TestIngressFilter:
    """Tests para IngressFilter (capa 1 y 2)."""

    def test_layer1_blocks_dangerous_commands(self, tmp_path):
        """Capa 1: debe bloquear comandos peligrosos."""
        blacklist = tmp_path / "ingress.txt"
        blacklist.write_text("rm -rf\nsudo\npasswd\n")
        
        ingress = IngressFilter(str(blacklist), enabled_layer2=False)
        agent_manifest = {"id": "test", "firewall_override": {}}
        
        assert ingress.evaluate("rm -rf /home", agent_manifest) is False
        assert ingress.evaluate("sudo apt update", agent_manifest) is False
        assert ingress.evaluate("passwd", agent_manifest) is False
        assert ingress.evaluate("comando seguro", agent_manifest) is True

    def test_layer1_blocks_agent_specific_patterns(self, tmp_path):
        """Capa 1: puede tener blacklist específica por agente."""
        blacklist = tmp_path / "ingress.txt"
        blacklist.write_text("global_bad\n")
        
        ingress = IngressFilter(str(blacklist), enabled_layer2=False)
        agent_manifest = {
            "id": "test",
            "firewall_override": {
                "ingress": {
                    "layer1_regex": {
                        "blacklist": ["agent_specific_bad"]
                    }
                }
            }
        }
        
        assert ingress.evaluate("global_bad", agent_manifest) is False
        assert ingress.evaluate("agent_specific_bad", agent_manifest) is False
        assert ingress.evaluate("safe_text", agent_manifest) is True

    def test_rate_limiter_blocks_excessive_requests(self, tmp_path):
        """Rate limiter: debe bloquear cuando se excede el límite."""
        blacklist = tmp_path / "ingress.txt"
        blacklist.write_text("")
        
        ingress = IngressFilter(str(blacklist), enabled_layer2=False)
        agent_manifest = {"id": "test_user", "firewall_override": {}}
        
        # 100 requests should be allowed (max_requests=100)
        for i in range(100):
            assert ingress.evaluate(f"request_{i}", agent_manifest) is True
        
        # The 101st should be blocked
        assert ingress.evaluate("request_101", agent_manifest) is False

    def test_rate_limiter_resets_after_window(self):
        """Rate limiter: debe resetear después de la ventana de tiempo."""
        limiter = RateLimiter(max_requests=2, window_seconds=1)
        
        assert limiter.is_allowed("user1") is True
        assert limiter.is_allowed("user1") is True
        assert limiter.is_allowed("user1") is False  # Third within window
        
        # Simulate waiting for window to pass
        import time
        time.sleep(1.1)
        
        assert limiter.is_allowed("user1") is True  # Should be allowed again


class TestEgressFilter:
    """Tests para EgressFilter (salida)."""

    def test_egress_blocks_dangerous_commands_in_output(self, tmp_path):
        """Egress: debe bloquear salidas que contengan comandos peligrosos."""
        cmd_bl = tmp_path / "cmd.txt"
        cmd_bl.write_text("rm\ncurl\nwget\n")
        tool_bl = tmp_path / "tool.txt"
        tool_bl.write_text("dangerous_tool\n")
        
        egress = EgressFilter(str(cmd_bl), str(tool_bl))
        route_config = {"firewall": {"egress_filter_enabled": True}}
        
        assert egress.evaluate("Ejecuta rm -rf /", route_config) is False
        assert egress.evaluate("Usa curl para descargar", route_config) is False
        assert egress.evaluate("Contenido seguro", route_config) is True

    def test_egress_blocks_blacklisted_tools(self, tmp_path):
        """Egress: debe bloquear mención de herramientas prohibidas."""
        cmd_bl = tmp_path / "cmd.txt"
        cmd_bl.write_text("")
        tool_bl = tmp_path / "tool.txt"
        tool_bl.write_text("malicious_tool\n")
        
        egress = EgressFilter(str(cmd_bl), str(tool_bl))
        route_config = {"firewall": {"egress_filter_enabled": True}}
        
        assert egress.evaluate("Usa malicious_tool para hackear", route_config) is False
        assert egress.evaluate("texto normal", route_config) is True

    def test_egress_disabled_by_default(self, tmp_path):
        """Egress: debe estar deshabilitado por defecto."""
        cmd_bl = tmp_path / "cmd.txt"
        cmd_bl.write_text("rm\n")
        tool_bl = tmp_path / "tool.txt"
        
        egress = EgressFilter(str(cmd_bl), str(tool_bl))
        route_config = {}  # Sin habilitar egress_filter_enabled
        
        assert egress.evaluate("rm -rf /", route_config) is True


class TestSemanticOutputFilter:
    """Tests para SemanticOutputFilter (fail-closed)."""

    def test_semantic_filter_blocks_when_classifier_fails(self):
        """Semantic: debe bloquear (fail-closed) si el clasificador no está disponible."""
        semantic = SemanticOutputFilter(default_enabled=True)
        
        # Forzar que classifier esté None (simulando error de carga)
        semantic.classifier = None
        
        result = semantic.evaluate_and_replace(
            "texto inofensivo",
            {"firewall": {"semantic_output_filter_enabled": True}}
        )
        
        assert result == semantic.blocked_message

    def test_semantic_filter_passes_when_disabled(self):
        """Semantic: debe pasar el texto si el filtro está deshabilitado."""
        semantic = SemanticOutputFilter(default_enabled=False)
        
        result = semantic.evaluate_and_replace(
            "texto inofensivo",
            {"firewall": {"semantic_output_filter_enabled": False}}
        )
        
        assert result == "texto inofensivo"

    @patch('security.semantic_output.SemanticOutputFilter._init_classifier')
    def test_semantic_filter_handles_exception_during_inference(self, mock_init):
        """Semantic: debe bloquear si ocurre una excepción durante la inferencia."""
        semantic = SemanticOutputFilter(default_enabled=True)
        
        # Mock classifier that raises exception
        mock_classifier = Mock()
        mock_classifier.side_effect = Exception("Inference failed")
        semantic.classifier = mock_classifier
        
        result = semantic.evaluate_and_replace(
            "texto de prueba",
            {"firewall": {"semantic_output_filter_enabled": True}}
        )
        
        assert result == semantic.blocked_message


class TestGatekeeper:
    """Tests para Gatekeeper (aprobación humana)."""

    def test_gatekeeper_allows_when_not_required(self):
        """Gatekeeper: debe permitir sin preguntar si la ruta no lo requiere."""
        audit = ApprovalAudit(audit_file="/tmp/test_audit.log")
        gatekeeper = Gatekeeper(default_timeout=1, force_all=False)
        
        route_config = {"configuration": {"gatekeeper_required": False}}
        
        # No debe pedir confirmación (simulado)
        result = gatekeeper.verify("test_route", route_config, "req_123")
        assert result is True

    def test_gatekeeper_uses_session_cache(self, monkeypatch):
        """Gatekeeper: debe cachear la decisión en la sesión."""
        gatekeeper = Gatekeeper(default_timeout=1, force_all=False)
        
        route_config = {"configuration": {"gatekeeper_required": True}}
        
        # Mock input to simulate 'Y'
        monkeypatch.setattr('sys.stdin.readline', lambda: 'Y')
        monkeypatch.setattr('select.select', lambda a,b,c,t: ([sys.stdin], [], []))
        
        # First call should ask and approve
        result1 = gatekeeper.verify("cached_route", route_config, "req_1")
        assert result1 is True
        
        # Second call should use cache
        result2 = gatekeeper.verify("cached_route", route_config, "req_2")
        assert result2 is True

    def test_gatekeeper_rejects_on_timeout(self, monkeypatch):
        """Gatekeeper: debe rechazar (fail-closed) si hay timeout."""
        gatekeeper = Gatekeeper(default_timeout=1, force_all=False)
        
        route_config = {"configuration": {"gatekeeper_required": True}}
        
        # Mock select to return empty (timeout)
        monkeypatch.setattr('select.select', lambda a,b,c,t: ([], [], []))
        
        result = gatekeeper.verify("timeout_route", route_config, "req_timeout")
        assert result is False


class TestIntegrationSecurityPipeline:
    """Tests de integración del pipeline completo de seguridad."""

    def test_ingress_egress_pipeline_blocks_dangerous_flow(self, tmp_path):
        """Pipeline completo: debe bloquear entrada peligrosa y salida peligrosa."""
        ingress_bl = tmp_path / "ingress.txt"
        ingress_bl.write_text("delete_all\n")
        egress_cmd = tmp_path / "egress_cmd.txt"
        egress_cmd.write_text("rm\n")
        egress_tool = tmp_path / "egress_tool.txt"
        egress_tool.write_text("")
        
        ingress = IngressFilter(str(ingress_bl), enabled_layer2=False)
        egress = EgressFilter(str(egress_cmd), str(egress_tool))
        
        agent_manifest = {"id": "test", "firewall_override": {}}
        route_config = {"firewall": {"egress_filter_enabled": True}}
        
        # Entrada peligrosa debe ser bloqueada
        assert ingress.evaluate("delete_all", agent_manifest) is False
        
        # Entrada segura pasa
        assert ingress.evaluate("texto seguro", agent_manifest) is True
        
        # Salida peligrosa debe ser bloqueada
        assert egress.evaluate("rm -rf /", route_config) is False


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
