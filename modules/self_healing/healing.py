import json
import logging
from typing import Callable, Any, Optional

logger = logging.getLogger("ferdonan.self_healing")

class SelfHealingEngine:
    def __init__(self, max_retries: int = 2):
        self.max_retries = max_retries

    def validate_json(self, content: str) -> bool:
        try:
            json.loads(content)
            return True
        except ValueError:
            return False

    def execute_with_healing(self, llm_call_func: Callable[[], str], fallback_cpu_func: Optional[Callable[[str, str], str]] = None) -> str:
        """
        Ejecuta la llamada cognitiva original y repara si se detecta un JSON inválido.
        Principio de diseño: No razona sobre el contenido del negocio, solo corrige la estructura.
        """
        attempts = 0
        last_output = ""
        
        while attempts <= self.max_retries:
            if attempts == 0:
                last_output = llm_call_func()
            else:
                logger.debug(f"Ejecutando reintento de Self-Healing {attempts}/{self.max_retries}...", extra={"component": "self_healing"})
                repair_prompt = f"Corrige estrictamente la sintaxis de este JSON malformado, devuelve solo el JSON válido: {last_output}"
                if fallback_cpu_func:
                    # Invoca el modelo liviano en CPU asignado para reparaciones estructurales
                    last_output = fallback_cpu_func("system_format_fixer", repair_prompt)
                else:
                    last_output = llm_call_func()

            if self.validate_json(last_output):
                if attempts > 0:
                    logger.info("Formato JSON corregido con éxito mediante Self-Healing.", extra={"component": "self_healing"})
                return last_output
            
            attempts += 1

        logger.error("Self-Healing agotado sin poder reparar el formato de la respuesta.", extra={"component": "self_healing"})
        return last_output
