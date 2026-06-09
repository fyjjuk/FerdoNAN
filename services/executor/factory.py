from typing import Dict, Any
from .base import BaseExecutor
from .cognitive import CognitiveExecutor
from .script import ScriptExecutor

def create_executor(route_data: Dict[str, Any]) -> BaseExecutor:
    route_type = route_data.get("type", "cognitive")
    if route_type == "cognitive":
        return CognitiveExecutor()
    elif route_type == "script":
        return ScriptExecutor()
    else:
        # Por defecto cognitivo
        return CognitiveExecutor()
