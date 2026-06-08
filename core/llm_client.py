import os, abc, json
from typing import Dict, Any
from core.logger import logger
from core.tracing import get_request_id

class LLMClient(abc.ABC):
    def __init__(self, agent_id: str, provider_config: Dict[str, Any], core_config: Dict[str, Any]):
        self.agent_id = agent_id
        self.provider_config = provider_config
        self.core_config = core_config
        self.api_key = self._resolve_api_key()

    @abc.abstractmethod
    def generate_response(self, prompt: str, system_prompt: str, config: Dict[str, Any]) -> str:
        pass

    def _resolve_api_key(self) -> str:
        provider_name = self.__class__.__name__.replace("Client", "").upper()
        if self.provider_config.get("api_key"): return self.provider_config["api_key"]
        return os.getenv(f"{provider_name}_API_KEY", "")

    def _log_telemetry(self, provider: str, model: str, ti: int, to: int):
        logger.info("Telemetría de tokens", extra={
            "component": "llm_client",
            "request_id": get_request_id(),
            "provider": provider,
            "model": model,
            "tokens_input": ti,
            "tokens_output": to,
            "agent_id": self.agent_id
        })

class GeminiClient(LLMClient):
    def generate_response(self, prompt, system_prompt, config) -> str:
        import google.generativeai as genai
        genai.configure(api_key=self.api_key)
        model = genai.GenerativeModel(model_name=config.get("model", "gemini-1.5-flash"), system_instruction=system_prompt)
        response = model.generate_content(prompt)
        self._log_telemetry("gemini", config.get("model"), response.usage_metadata.prompt_token_count, response.usage_metadata.candidates_token_count)
        return response.text

class GroqClient(LLMClient):
    def generate_response(self, prompt, system_prompt, config) -> str:
        from groq import Groq
        client = Groq(api_key=self.api_key)
        chat_completion = client.chat.completions.create(messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}], model=config.get("model", "llama3-8b-8192"))
        self._log_telemetry("groq", config.get("model"), chat_completion.usage.prompt_tokens, chat_completion.usage.completion_tokens)
        return chat_completion.choices[0].message.content

class LocalClient(LLMClient):
    def generate_response(self, prompt, system_prompt, config) -> str:
        # Simulación de respuesta local
        ti, to = 10, 20
        self._log_telemetry("local", "stub", ti, to)
        return f"Respuesta local: {prompt[:20]}"
