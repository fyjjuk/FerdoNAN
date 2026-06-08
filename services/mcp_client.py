import subprocess
import json
import time
import os
from core.logger import logger

class MCPClient:
    def __init__(self):
        self.server_path = "mcp_servers/" # Directorio donde residen los servidores

    def call_tool(self, server_name: str, tool_name: str, arguments: dict):
        start_time = time.perf_counter()
        try:
            # Ahora busca scripts en mcp_servers/ o intenta ejecutar como módulo
            cmd = ["python", "-m", f"mcp_server_{server_name}"]
            if not subprocess.run(["python", "-c", f"import mcp_server_{server_name}"], capture_output=True).returncode == 0:
                cmd = ["python", f"{self.server_path}/mcp_server_{server_name}.py"]

            process = subprocess.run(
                cmd + [tool_name, json.dumps(arguments)],
                capture_output=True, text=True, timeout=30
            )
            success = process.returncode == 0
            duration_ms = (time.perf_counter() - start_time) * 1000
            
            logger.info(f"MCP Tool execution: {tool_name}", extra={"duration_ms": duration_ms, "success": success})
            return json.loads(process.stdout) if success else {"error": process.stderr}
        except Exception as e:
            return {"error": str(e)}
