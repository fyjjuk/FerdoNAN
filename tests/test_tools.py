"""Tests para herramientas nativas."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from unittest.mock import patch, Mock
from tools.native.web_search import search_duckduckgo, run as web_search_run
from tools.native.web_fetch import fetch_and_summarize, run as web_fetch_run
from tools.native.spotify_control import run_spotify_command, check_playerctl


class TestWebSearch:
    """Tests para búsqueda web."""

    def test_search_empty_query(self):
        """Debe retornar error para query vacía."""
        result = web_search_run({"query": ""})
        assert "error" in result

    def test_search_no_query(self):
        """Debe retornar error sin query."""
        result = web_search_run({})
        assert "error" in result

    @patch('tools.native.web_search.requests.get')
    def test_search_returns_results(self, mock_get):
        """Debe retornar resultados de búsqueda."""
        mock_response = Mock()
        mock_response.text = '''
        <html>
            <div class="result">
                <a class="result__a">Título test</a>
                <a class="result__url">https://test.com</a>
                <div class="result__snippet">Descripción test</div>
            </div>
        </html>
        '''
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = web_search_run({"query": "python"})
        assert "results" in result
        assert len(result["results"]) >= 1

    @patch('tools.native.web_search.requests.get')
    def test_search_handles_timeout(self, mock_get):
        """Debe manejar timeout sin crashear."""
        mock_get.side_effect = Exception("Timeout")
        
        result = web_search_run({"query": "test"})
        # Debe retornar algo, no crashear
        assert "results" in result or "error" in result


class TestWebFetch:
    """Tests para fetch de URLs."""

    def test_fetch_empty_url(self):
        """Debe retornar error para URL vacía."""
        result = web_fetch_run({"url": ""})
        assert "error" in result

    @patch('tools.native.web_fetch.requests.get')
    def test_fetch_successful(self, mock_get):
        """Debe obtener y resumir contenido correctamente."""
        mock_response = Mock()
        mock_response.text = "<html><body><p>Contenido de prueba para resumir.</p></body></html>"
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = web_fetch_run({"url": "https://ejemplo.com"})
        assert "result" in result
        assert "Contenido" in result["result"] or "Error" not in result["result"]

    @patch('tools.native.web_fetch.requests.get')
    def test_fetch_handles_connection_error(self, mock_get):
        """Debe manejar errores de conexión."""
        mock_get.side_effect = Exception("Connection refused")
        
        result = web_fetch_run({"url": "https://ejemplo.com"})
        assert "result" in result
        assert "Error" in result["result"] or "❌" in result["result"]


class TestSpotifyControl:
    """Tests para control de Spotify."""

    @patch('tools.native.spotify_control.shutil.which')
    def test_check_playerctl_installed(self, mock_which):
        """check_playerctl debe detectar si playerctl está instalado."""
        mock_which.return_value = "/usr/bin/playerctl"
        assert check_playerctl() is True
        
        mock_which.return_value = None
        assert check_playerctl() is False

    @patch('tools.native.spotify_control.subprocess.run')
    @patch('tools.native.spotify_control.check_playerctl')
    def test_run_spotify_command_play(self, mock_check, mock_run):
        """Debe ejecutar comando play correctamente."""
        mock_check.return_value = True
        mock_run.return_value = Mock(returncode=0)
        
        result = run_spotify_command("play")
        assert "▶️" in result or "Reproduciendo" in result

    @patch('tools.native.spotify_control.subprocess.run')
    @patch('tools.native.spotify_control.check_playerctl')
    def test_run_spotify_command_status(self, mock_check, mock_run):
        """Debe obtener estado de reproducción."""
        mock_check.return_value = True
        mock_run.return_value = Mock(returncode=0, stdout="Playing", stderr="")
        
        result = run_spotify_command("status")
        assert "▶️" in result or "Reproduciendo" in result

    @patch('tools.native.spotify_control.check_playerctl')
    def test_run_spotify_command_no_playerctl(self, mock_check):
        """Debe mostrar error si playerctl no está instalado."""
        mock_check.return_value = False
        
        result = run_spotify_command("play")
        assert "no está instalado" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
