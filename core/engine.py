import yaml
import os
from core.llm_client import GeminiClient, GroqClient, LocalClient
from core.logger import logger
from core.tracing import get_request_id

class FerdoNANEngine:
    def __init__(self, core_config_path: str = "config/core.yaml"):
        self.core_config = self._load_config(core_config_path)

    def _load_config(self, path: str) -> dict:
        if os.path.exists(path):
            with open(path, 'r') as f:
                return yaml.safe_load(f)
        return {}

    def get_llm_client(self, agent_id: str, manifest: dict):
        provider_info = manifest.get("llm_provider", {})
        provider_name = provider_info.get("name", "local").lower()
        
        clients = {"gemini": GeminiClient, "groq": GroqClient, "local": LocalClient}
        client_class = clients.get(provider_name, LocalClient)
        
        logger.info(f"Instanciando cliente {provider_name}", 
                    extra={"component": "engine", "request_id": get_request_id(), "agent_id": agent_id})
        return client_class(agent_id, provider_info, self.core_config)
