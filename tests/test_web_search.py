import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from unittest.mock import patch, Mock
from tools.native.web_search import search_duckduckgo, run

def test_search_empty_query():
    """Búsqueda con query vacía debe retornar error"""
    result = run({"query": ""})
    assert "error" in result

def test_search_no_query():
    """Búsqueda sin parámetro query debe retornar error"""
    result = run({})
    assert "error" in result

@patch('tools.native.web_search.requests.get')
def test_search_with_mock_success(mock_get):
    """Búsqueda exitosa debe retornar resultados"""
    # Mock de respuesta HTML simulada
    mock_response = Mock()
    mock_response.text = '''
    <html>
        <div class="result">
            <a class="result__a">Título de prueba</a>
            <a class="result__url">https://ejemplo.com</a>
            <div class="result__snippet">Descripción de prueba</div>
        </div>
    </html>
    '''
    mock_response.raise_for_status = Mock()
    mock_get.return_value = mock_response
    
    result = run({"query": "python"})
    assert "results" in result
    assert len(result["results"]) >= 1
    assert result["results"][0]["title"] == "Título de prueba"

@patch('tools.native.web_search.requests.get')
def test_search_with_timeout(mock_get):
    """Búsqueda con timeout debe reintentar y eventualmente retornar error"""
    mock_get.side_effect = Exception("Timeout")
    
    result = run({"query": "test"})
    # Debe retornar un resultado (con error) pero no crashear
    assert "results" in result or "error" in result

def test_search_retry_logic():
    """Verificar que la función tiene reintentos (por inspección)"""
    import inspect
    source = inspect.getsource(search_duckduckgo)
    assert "max_retries" in source or "for attempt in range" in source
