import subprocess
import json
from typing import Dict, Any
from core.logger import logger
from .base import BaseExecutor

class ScriptExecutor(BaseExecutor):
    """Ejecuta rutas de script (nativas o MCP)."""
    def execute(self, agent_manifest, route_data: Dict[str, Any], cleaned_input: str, router, rag_engine) -> str:
        script_path = route_data.get("script_path")
        script_args = route_data.get("script_args", {})
        try:
            if script_args:
                args_str = json.dumps(script_args)
                result = subprocess.run(["python", script_path, args_str], capture_output=True, text=True, timeout=10)
            else:
                result = subprocess.run(["python", script_path, cleaned_input], capture_output=True, text=True, timeout=10)
            output = result.stdout.strip() if result.returncode == 0 else f"Error: {result.stderr}"
            return output
        except Exception as e:
            return f"Error: {str(e)}"
