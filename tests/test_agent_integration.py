"""Tests de integración con agentes reales y LLM (requiere Ollama corriendo)."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import yaml
from models.manifest import AgentManifest
from core.engine import FerdoNANEngine
from security.ingress import IngressFilter
from security.egress import EgressFilter
from security.semantic_output import SemanticOutputFilter
from persistence.memory_store import ShortTermMemory
from persistence.long_term_memory import LongTermMemory
from services.vector_store import RAGEngine

# Marcador para pruebas que requieren Ollama
pytestmark = pytest.mark.skipif(
    not os.environ.get('TEST_WITH_OLLAMA', False),
    reason="Ollama no disponible o TEST_WITH_OLLAMA no está activado"
)

@pytest.fixture
def engine():
    """Crea una instancia del motor con configuraciones básicas."""
    ingress = IngressFilter(global_regex_path="config/ingress_blacklist.txt", enabled_layer2=False)
    egress = EgressFilter("config/egress_cmd_blacklist.txt", "config/egress_tools_blacklist.txt")
    semantic = SemanticOutputFilter(default_enabled=False)
    eng = FerdoNANEngine(ingress=ingress, egress=egress, semantic=semantic)
    eng.rag_engine = RAGEngine()
    return eng

@pytest.fixture
def agent_experto_linux(engine):
    """Carga el agente experto_linux real."""
    with open("agents/experto_linux/config.yaml", "r") as f:
        data = yaml.safe_load(f)
    manifest = AgentManifest(**data)
    manifest.memory = ShortTermMemory(manifest.short_term_memory_window)
    manifest.long_term_memory = LongTermMemory(manifest.id, engine.rag_engine)
    manifest.llm_client = engine._get_llm_client(manifest.id, data, {})
    return manifest

@pytest.fixture
def agent_buscador_web(engine):
    """Carga el agente buscador_web real."""
    with open("agents/buscador_web/config.yaml", "r") as f:
        data = yaml.safe_load(f)
    manifest = AgentManifest(**data)
    manifest.memory = ShortTermMemory(manifest.short_term_memory_window)
    manifest.long_term_memory = LongTermMemory(manifest.id, engine.rag_engine)
    manifest.llm_client = engine._get_llm_client(manifest.id, data, {})
    return manifest

def test_experto_linux_responde_comando(engine, agent_experto_linux):
    """Prueba que el agente experto_linux dé una respuesta útil a un comando básico."""
    output, summary = engine.process_pipeline(agent_experto_linux, "¿cómo veo los procesos en linux?")
    assert "ps" in output.lower() or "top" in output.lower() or "htop" in output.lower()
    assert "error" not in output.lower()

def test_buscador_web_no_falla(engine, agent_buscador_web):
    """Prueba que el buscador web responda sin errores (puede devolver resultados o mensaje de no resultados)."""
    output, summary = engine.process_pipeline(agent_buscador_web, "buscar python")
    assert "error" not in output.lower() or "no se encontraron" in output.lower()
    assert len(output) > 10

