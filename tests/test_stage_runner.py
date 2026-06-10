"""
Tests para services/executor/stage_runner.py
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from services.executor.stage_runner import StageRunner


class TestStageRunner:
    """Pruebas para StageRunner"""
    
    def setup_method(self):
        """Configuración inicial para cada test"""
        self.mock_agent = Mock()
        self.mock_agent.llm_client = Mock()
        self.runner = StageRunner(self.mock_agent)
    
    def test_validate_stage_output_valid(self):
        """Verificar validación de output válido"""
        result = self.runner.validate_stage_output("Valid output", "test_stage", "output")
        assert result is True
    
    def test_validate_stage_output_none(self):
        """Verificar validación de output None"""
        result = self.runner.validate_stage_output(None, "test_stage", "output")
        assert result is False
    
    def test_validate_stage_output_empty_string(self):
        """Verificar validación de string vacío"""
        result = self.runner.validate_stage_output("", "test_stage", "output")
        assert result is False
    
    def test_validate_stage_output_not_string(self):
        """Verificar validación de output no string"""
        result = self.runner.validate_stage_output(123, "test_stage", "output")
        assert result is False
    
    def test_validate_stage_output_very_long(self):
        """Verificar validación de output muy largo (solo warning)"""
        long_output = "x" * 15000
        result = self.runner.validate_stage_output(long_output, "test_stage", "output")
        assert result is True  # Sigue siendo válido, solo warning
    
    def test_execute_llm_stage_success(self):
        """Verificar ejecución exitosa de stage LLM"""
        stage_config = {
            "type": "llm",
            "name": "test_stage",
            "prompt": "Test prompt: {{input}}",
            "system_prompt": "You are a test assistant",
            "output_key": "test_output"
        }
        context = {}
        cleaned_input = "Hello, world!"
        core_config = {}
        
        self.mock_agent.llm_client.generate_response.return_value = "Generated response"
        
        output, new_context = self.runner.execute_stage(stage_config, context, cleaned_input, core_config)
        
        assert output == "Generated response"
        assert "test_output" in new_context
        assert new_context["test_output"] == "Generated response"
    
    def test_execute_llm_stage_with_context(self):
        """Verificar ejecución de stage con contexto"""
        stage_config = {
            "type": "llm",
            "name": "test_stage",
            "prompt": "Context: {{context}}, Input: {{input}}",
            "output_key": "test_output"
        }
        context = {"previous": "value"}
        cleaned_input = "User query"
        core_config = {}
        
        self.mock_agent.llm_client.generate_response.return_value = "Response with context"
        
        output, new_context = self.runner.execute_stage(stage_config, context, cleaned_input, core_config)
        
        # Verificar que el prompt se formateó correctamente
        call_args = self.mock_agent.llm_client.generate_response.call_args[0]
        assert "Context: {'previous': 'value'}" in call_args[0]
        assert "Input: User query" in call_args[0]
    
    def test_execute_llm_stage_with_retry(self):
        """Verificar reintento cuando la salida es inválida"""
        stage_config = {
            "type": "llm",
            "name": "test_stage",
            "prompt": "Test",
            "output_key": "test_output"
        }
        context = {}
        cleaned_input = "test"
        core_config = {}
        
        # Primera llamada retorna None (inválido), segunda retorna string válido
        self.mock_agent.llm_client.generate_response.side_effect = [None, "Valid after retry"]
        
        output, new_context = self.runner.execute_stage(stage_config, context, cleaned_input, core_config)
        
        assert output == "Valid after retry"
        assert self.mock_agent.llm_client.generate_response.call_count == 2
    
    def test_execute_llm_stage_exception(self):
        """Verificar manejo de excepciones en stage LLM"""
        stage_config = {
            "type": "llm",
            "name": "test_stage",
            "prompt": "Test",
            "output_key": "test_output"
        }
        context = {}
        cleaned_input = "test"
        core_config = {}
        
        self.mock_agent.llm_client.generate_response.side_effect = Exception("LLM Error")
        
        output, new_context = self.runner.execute_stage(stage_config, context, cleaned_input, core_config)
        
        assert "Error: LLM Error" in output
        assert "test_output" in new_context
    
    def test_execute_tool_stage(self):
        """Verificar ejecución de stage tipo tool"""
        stage_config = {
            "type": "tool",
            "name": "test_tool",
            "tool": "web_search",
            "params": {"query": "test"},
            "output_key": "tool_output"
        }
        context = {}
        cleaned_input = "ignored for tools"
        core_config = {}
        
        output, new_context = self.runner.execute_stage(stage_config, context, cleaned_input, core_config)
        
        assert "Tool web_search executed" in output
        assert "tool_output" in new_context


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
