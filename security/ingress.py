import re
import logging
from typing import Dict, Any

logger = logging.getLogger("ferdonan.firewall.ingress")

class IngressFilter:
    def __init__(self, global_regex_path: str, layer2_model_name: str = None, enabled_layer2: bool = False):
        self.enabled_layer2 = enabled_layer2  # Desactivado por defecto
        self.global_regex = self._load_regex_blacklist(global_regex_path)
        self.classifier = None
        
        # Capa 2 desactivada para evitar errores de modelo
        if self.enabled_layer2:
            logger.warning("Capa 2 semántica no disponible - ejecutando solo con Capa 1 (RegEx)")

    def _load_regex_blacklist(self, path: str) -> list:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return [line.strip() for line in f if line.strip() and not line.startswith('#')]
        except Exception as e:
            logger.error(f"Error cargando blacklist RegEx global: {str(e)}")
            return []

    def evaluate(self, user_input: str, agent_manifest: Dict[str, Any]) -> bool:
        # CAPA 1: RegEx Determinista
        agent_blacklist = agent_manifest.get("firewall_override", {}).get("ingress", {}).get("layer1_regex", {}).get("blacklist", [])
        full_blacklist = self.global_regex + agent_blacklist

        for pattern in full_blacklist:
            if re.search(pattern, user_input, re.IGNORECASE):
                logger.error(f"INPUT BLOQUEADO por Capa 1 (RegEx). Patrón: {pattern}")
                return False

        # CAPA 2: Desactivada por ahora
        if self.enabled_layer2 and self.classifier:
            try:
                prediction = self.classifier(user_input)[0]
                if prediction['label'] == 'LABEL_1' and prediction['score'] > 0.85:
                    logger.error(f"INPUT BLOQUEADO por Capa 2 (Semántica)")
                    return False
            except Exception as e:
                logger.critical(f"Error en Capa 2: {str(e)}. Aplicando Fail-Closed.")
                return False

        logger.info("Input verificado por IngressFilter.")
        return True
