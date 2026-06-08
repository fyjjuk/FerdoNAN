import os, sys, yaml
from core.logger import logger
from core.manifest_model import AgentManifest
from core.engine import FerdoNANEngine
from core.tracing import generate_request_id

def bootstrap_core():
    logger.info("Inicializando Núcleo...", extra={"component": "core"})
    engine = FerdoNANEngine()
    agents_dir = "agents"
    loaded = {}
    if not os.path.exists(agents_dir): os.makedirs(agents_dir)
    
    for agent_id in os.listdir(agents_dir):
        path = os.path.join(agents_dir, agent_id)
        config = os.path.join(path, "config.yaml")
        if os.path.isdir(path) and os.path.exists(config):
            try:
                with open(config, "r") as f:
                    data = yaml.safe_load(f)
                manifest = AgentManifest(**data)
                manifest.llm_client = engine.get_llm_client(agent_id, data)
                loaded[agent_id] = manifest
                logger.info(f"Agente {agent_id} cargado.", extra={"component": "core"})
            except Exception as e:
                logger.error(f"Error {agent_id}: {e}", extra={"component": "core"})
    return loaded

if __name__ == "__main__":
    agents = bootstrap_core()
    req_id = generate_request_id()
    logger.info("FerdoNAN iniciado", extra={"component": "main", "request_id": req_id})
    print("\nFerdoNAN Listo. Agentes cargados: " + ", ".join(agents.keys()))
