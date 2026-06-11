from typing import Dict, Any
from .base import BaseExecutor
from .llm_executor import LLMExecutor
from .script import ScriptExecutor

def create_executor(route_data: Dict[str, Any], agent_manifest=None) -> BaseExecutor:
    route_type = route_data.get("type", "cognitive")
    if route_type == "cognitive":
        if agent_manifest is None:
            raise ValueError("agent_manifest es requerido para LLMExecutor")
        return LLMExecutor(agent_manifest)
    elif route_type == "script":
        return ScriptExecutor()
    else:
        if agent_manifest is None:
            raise ValueError("agent_manifest es requerido para LLMExecutor")
        return LLMExecutor(agent_manifest)
