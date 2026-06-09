import os
import sys
import yaml
from core.logger import logger
import sys
sys.modules['tqdm'] = __import__('tqdm')
# Silenciar warnings de HF
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="huggingface_hub")
from models.manifest import AgentManifest
from core.engine import FerdoNANEngine
from persistence.memory_store import ShortTermMemory
from persistence.long_term_memory import LongTermMemory
from core.tracing import generate_request_id
from services.intent_router import RouteNotFoundError
from security.ingress import IngressFilter
from security.egress import EgressFilter
from security.semantic_output import SemanticOutputFilter
from ui.selector import select_agent_interactive

def check_ollama():
    """Verifica que Ollama esté corriendo antes de iniciar."""
    import requests
    try:
        ollama_host = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
        response = requests.get(f"{ollama_host}/api/tags", timeout=3)
        if response.status_code == 200:
            print("\033[92m✅ Ollama está corriendo correctamente.\033[0m")
            return True
        else:
            print(f"\033[91m❌ Ollama responde con código {response.status_code}\033[0m")
            return False
    except requests.ConnectionError:
        print("\033[91m❌ No se pudo conectar a Ollama en http://localhost:11434\033[0m")
        print("\033[93m   Asegúrate de ejecutar: ollama serve\033[0m")
        return False
    except Exception as e:
        print(f"\033[91m❌ Error verificando Ollama: {e}\033[0m")
        return False

def bootstrap_security_assets():
    from dotenv import load_dotenv
    load_dotenv()
    if not os.path.exists("config"):
        os.makedirs("config")
    security_files = {
        "config/ingress_blacklist.txt": "# Blacklist de comandos peligrosos (RegEx)\nrm -rf\nsudo\npasswd\n",
        "config/egress_cmd_blacklist.txt": "# Comandos prohibidos en salida\nrm\ncurl\nwget\n",
        "config/egress_tools_blacklist.txt": "# Herramientas prohibidas\ndangerous_tool\n"
    }
    for filepath, default_content in security_files.items():
        if not os.path.exists(filepath):
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(default_content)
            logger.info(f"Archivo de seguridad creado: {filepath}")
    return True

def bootstrap_core():
    from dotenv import load_dotenv
    load_dotenv()
    load_dotenv()
    bootstrap_security_assets()
    
    core_config = {}
    if os.path.exists("config/core.yaml"):
        with open("config/core.yaml", "r", encoding="utf-8") as f:
            core_config = yaml.safe_load(f) or {}
    
    # Verificar Ollama antes de continuar
    if not check_ollama():
        print("\033[93m⚠️  Ollama no está disponible. Los agentes que usen Ollama fallarán.\033[0m")
        respuesta = input("\033[93m¿Continuar de todas formas? (s/N): \033[0m")
        if respuesta.lower() != "s":
            print("\033[91mAbortando inicio...\033[0m")
            sys.exit(1)
        print("\033[93mContinuando sin Ollama...\033[0m")

    
    ingress = IngressFilter(global_regex_path="config/ingress_blacklist.txt", enabled_layer2=False)
    egress = EgressFilter("config/egress_cmd_blacklist.txt", "config/egress_tools_blacklist.txt")
    semantic = SemanticOutputFilter(default_enabled=False)
    
    from security.gatekeeper import Gatekeeper
    from persistence.cache import ResponseCache
    gatekeeper = Gatekeeper(default_timeout=60, force_all=False)
    cache = ResponseCache()
    engine = FerdoNANEngine(ingress=ingress, egress=egress, semantic=semantic,
                            gatekeeper=gatekeeper, cache=cache)
    engine.core_config = core_config
    # Inicializar RAG Engine para indexación automática
    from services.vector_store import RAGEngine
    engine.rag_engine = RAGEngine()
 
    # Inicializar RAG Engine para indexación automática
    
    
    agents_dir = "agents"
    loaded = {}
    
    if not os.path.exists(agents_dir):
        os.makedirs(agents_dir)
    
    for agent_id in os.listdir(agents_dir):
        path = os.path.join(agents_dir, agent_id)
        config_path = os.path.join(path, "config.yaml")
        if os.path.isdir(path) and os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                manifest = AgentManifest(**data)
                manifest.memory = ShortTermMemory(manifest.short_term_memory_window)
                manifest.long_term_memory = LongTermMemory(agent_id, engine.rag_engine)
                manifest.llm_client = engine._get_llm_client(agent_id, data, core_config)

                # Cargar rutas del agente
                routes_dir = os.path.join(path, "routes")
                routes_list = []
                if os.path.exists(routes_dir):
                    for route_file in os.listdir(routes_dir):
                        if route_file.endswith((".yaml", ".yml")):
                            with open(os.path.join(routes_dir, route_file), "r") as rf:
                                route_data = yaml.safe_load(rf)
                                if route_data and "route_id" in route_data:
                                    routes_list.append(route_data)
                manifest.routes_available = routes_list
                # Indexar documentos de la carpeta docs/ del agente si existe
                docs_dir = os.path.join(path, "docs")
                if os.path.exists(docs_dir) and engine.rag_engine:
                    for doc_file in os.listdir(docs_dir):
                        if doc_file.endswith(('.txt', '.md', '.docx', '.xlsx')):
                            file_path = os.path.join(docs_dir, doc_file)
                            try:
                                engine.rag_engine.process_and_index(agent_id, file_path)
                                logger.info(f"Documento indexado: {doc_file} para agente {agent_id}")
                            except Exception as e:
                                print(f"\033[93m⚠️ Error indexando {doc_file} para agente {agent_id}: {e}\033[0m")
                                logger.error(f"Error indexando {doc_file}: {e}")
                loaded[agent_id] = manifest
                logger.info(f"Agente {agent_id} cargado con éxito.", extra={"component": "core"})
                print(f"\033[92m✅ Agente {agent_id} cargado con éxito.\033[0m")
            except Exception as e:
                print(f"\033[91m❌ Error cargando agente {agent_id}: {e}\033[0m")
                logger.error(f"Error cargando agente {agent_id}: {e}", extra={"component": "core"})
    
    return engine, loaded
if __name__ == "__main__":
    engine, agents = bootstrap_core()
    generate_request_id()
    
    if not agents:
        print("❌ No se encontraron agentes configurados.")
        sys.exit(1)
    
    # Selección interactiva (menú con flechas)
    try:
        agent_manifest = select_agent_interactive(agents)
        if agent_manifest is None:
            print("👋 Selección cancelada. Saliendo...")
            sys.exit(0)
    except ImportError:
        # Fallback a selector numérico si prompt_toolkit no está instalado
        print("⚠️ prompt_toolkit no instalado. Usando selector numérico.")
        agent_manifest = select_agent(agents)
    
    print(f"[+] Agente Activo: {agent_manifest.name} ({agent_manifest.id})")
    print(f"[+] Concurrencia: {agent_manifest.execution_mode}")
    print(f"[+] Proveedor LLM: {agent_manifest.llm_provider.get('name', 'desconocido')}")
    print("[+] Escribe 'salir' para finalizar.\n")
    
    while True:
        try:
            user_query = input(f"\n[{agent_manifest.id}] > ")
            if user_query.strip().lower() == 'salir':
                break
            if not user_query.strip():
                continue
            
            output, summary = engine.process_pipeline(agent_manifest, user_query)
            print(f"\n[Enrutamiento Exitoso]")
            print(f" -> Ruta: {summary.get('route_id', 'unknown')}")
            print(f" -> Modo: {summary.get('execution_mode', 'exclusive')}")
            print(f" -> Respuesta:\n{output}")
            
        except PermissionError as pe:
            print(f"\n[!] BLOQUEADO POR FIREWALL: {pe}")
        except RouteNotFoundError as exc:
            print(f"\n[!] Ruta no encontrada: {exc}")
            if hasattr(exc, 'available_routes') and exc.available_routes:
                print("   Rutas disponibles:")
                for r in exc.available_routes:
                    print(f"     - {r.get('route_id')}: {r.get('description', '')[:50]}")
        except KeyboardInterrupt:
            print("\n[!] Interrupción recibida. Saliendo...")
            break
        except Exception as e:
            print(f"[-] Error: {e}")
            logger.error(f"Error en pipeline: {e}", extra={"component": "main"})
