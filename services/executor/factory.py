from typing import Dict, Any
from .base import BaseExecutor
from .cognitive import CognitiveExecutor
from .script import ScriptExecutor

def create_executor(route_data: Dict[str, Any], agent_manifest=None) -> BaseExecutor:
    route_type = route_data.get("type", "cognitive")
    if route_type == "cognitive":
        if agent_manifest is None:
            raise ValueError("agent_manifest es requerido para CognitiveExecutor")
        return CognitiveExecutor(agent_manifest)
    elif route_type == "script":
        return ScriptExecutor()
    else:
        if agent_manifest is None:
            raise ValueError("agent_manifest es requerido para CognitiveExecutor")
        return CognitiveExecutor(agent_manifest)
