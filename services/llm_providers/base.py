import abc
import os
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
        if self.provider_config.get("api_key"):
            return self.provider_config["api_key"]
        env_var = f"{provider_name}_API_KEY"
        return os.getenv(env_var, "")

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
