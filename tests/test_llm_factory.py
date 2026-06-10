"""
Tests para core/llm_factory.py
"""
import pytest
from unittest.mock import Mock, patch, MagicMock


class TestLLMFactory:
    """Pruebas para la creación de clientes LLM"""
    
    def test_create_ollama_client(self):
        """Verificar creación de cliente Ollama"""
        from core.llm_factory import create_llm_client
        
        manifest_data = {
            "llm_provider": {
                "name": "ollama",
                "model": "llama3.2:3b",
                "temperature": 0.7
            }
        }
        
        with patch('services.llm_providers.OllamaClient') as mock_ollama:
            mock_ollama.return_value = MagicMock()
            client = create_llm_client("test_agent", manifest_data, {})
            
            mock_ollama.assert_called_once()
            assert client is not None
    
    def test_create_gemini_client(self):
        """Verificar creación de cliente Gemini"""
        from core.llm_factory import create_llm_client
        
        manifest_data = {
            "llm_provider": {
                "name": "gemini",
                "model": "gemini-1.5-flash"
            }
        }
        core_config = {
            "llm": {
                "gemini": {
                    "api_key": "test_key"
                }
            }
        }
        
        with patch('services.llm_providers.GeminiClient') as mock_gemini:
            mock_gemini.return_value = MagicMock()
            client = create_llm_client("test_agent", manifest_data, core_config)
            
            mock_gemini.assert_called_once()
            assert client is not None
    
    def test_create_groq_client(self):
        """Verificar creación de cliente Groq"""
        from core.llm_factory import create_llm_client
        
        manifest_data = {
            "llm_provider": {
                "name": "groq",
                "model": "llama3-8b-8192"
            }
        }
        core_config = {
            "llm": {
                "groq": {
                    "api_key": "test_key"
                }
            }
        }
        
        with patch('services.llm_providers.GroqClient') as mock_groq:
            mock_groq.return_value = MagicMock()
            client = create_llm_client("test_agent", manifest_data, core_config)
            
            mock_groq.assert_called_once()
            assert client is not None
    
    def test_create_local_client_fallback(self):
        """Verificar que fallback a LocalClient funciona"""
        from core.llm_factory import create_llm_client
        
        manifest_data = {
            "llm_provider": {
                "name": "unknown_provider"
            }
        }
        
        with patch('services.llm_providers.LocalClient') as mock_local:
            mock_local.return_value = MagicMock()
            client = create_llm_client("test_agent", manifest_data, {})
            
            mock_local.assert_called_once()
            assert client is not None
    
    def test_dynamic_resource_profile(self):
        """Verificar que perfiles dinámicos se aplican correctamente"""
        from core.llm_factory import create_llm_client
        
        manifest_data = {
            "llm_provider": {
                "name": "ollama",
                "dynamic_resource_management": True,
                "resource_profiles": {
                    "high": {"model": "qwen2.5:3b", "temperature": 0.8},
                    "low": {"model": "phi4-mini", "temperature": 0.3}
                }
            }
        }
        
        with patch('services.llm_providers.OllamaClient') as mock_ollama:
            with patch('core.llm_factory.ResourceScheduler') as mock_scheduler:
                mock_scheduler_instance = MagicMock()
                mock_scheduler_instance.select_resource_profile.return_value = "high"
                mock_scheduler.return_value = mock_scheduler_instance
                
                mock_ollama.return_value = MagicMock()
                client = create_llm_client("test_agent", manifest_data, {})
                
                mock_ollama.assert_called_once()
                assert client is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
