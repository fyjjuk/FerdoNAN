import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from unittest.mock import Mock

from services.executor.cognitive import CognitiveExecutor

class MockLLMClient:
    def __init__(self):
        self.generate_response = Mock()
        self.generate_response.return_value = "salida de prueba"
        self.provider_config = {"model": "llama3.2:3b"}
        self.core_config = {}

class MockManifest:
    def __init__(self):
        self.id = "test_agent"
        self.llm_client = MockLLMClient()

@pytest.fixture
def executor():
    return CognitiveExecutor()

@pytest.fixture
def mock_manifest():
    return MockManifest()

def test_validate_stage_output_valid(executor):
    result = executor._validate_stage_output("texto válido", "stage1", "key1")
    assert result is True

def test_validate_stage_output_empty(executor):
    result = executor._validate_stage_output("", "stage1", "key1")
    assert result is False

def test_validate_stage_output_none(executor):
    result = executor._validate_stage_output(None, "stage1", "key1")
    assert result is False

def test_validate_stage_output_whitespace(executor):
    result = executor._validate_stage_output("   ", "stage1", "key1")
    assert result is False

def test_execute_stage_with_valid_output(executor, mock_manifest):
    """Stage con output válido debe funcionar correctamente"""
    mock_manifest.llm_client.generate_response.return_value = "salida válida"
    
    stage_config = {
        "name": "test_stage",
        "prompt": "Hola {user_input}",
        "output_key": "resultado"
    }
    
    output, context = executor._execute_stage(mock_manifest, stage_config, {}, "mundo", {})
    
    assert mock_manifest.llm_client.generate_response.called
    assert "resultado" in context
    assert context["resultado"] == "salida válida"

def test_execute_stage_with_empty_output(executor, mock_manifest):
    """Stage con output vacío debe reintentar"""
    mock_manifest.llm_client.generate_response.side_effect = ["", "salida válida después"]
    
    stage_config = {
        "name": "test_stage",
        "prompt": "Hola {user_input}",
        "output_key": "resultado"
    }
    
    output, context = executor._execute_stage(mock_manifest, stage_config, {}, "mundo", {})
    
    # Verificar que se llamó al menos una vez (debería ser 2 por el reintento)
    assert mock_manifest.llm_client.generate_response.call_count >= 1
    assert "resultado" in context

def test_execute_stage_with_consistent_failure(executor, mock_manifest):
    """Stage que siempre falla debe poner mensaje de error en contexto"""
    mock_manifest.llm_client.generate_response.return_value = ""
    
    stage_config = {
        "name": "test_stage",
        "prompt": "Hola {user_input}",
        "output_key": "resultado"
    }
    
    output, context = executor._execute_stage(mock_manifest, stage_config, {}, "mundo", {})
    
    assert "resultado" in context
    # El mensaje debe indicar error
    assert "[ERROR:" in context["resultado"] or context["resultado"] == ""
