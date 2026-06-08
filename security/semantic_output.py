import logging
from typing import Dict, Any

logger = logging.getLogger("ferdonan.firewall.semantic_output")

class SemanticOutputFilter:
    def __init__(self, default_enabled: bool = False, blocked_message: str = "La respuesta fue bloqueada por contenido inapropiado."):
        self.default_enabled = default_enabled
        self.blocked_message = blocked_message
        self.classifier = None
        if self.default_enabled:
            self._init_classifier()

    def _init_classifier(self):
        try:
            from transformers import pipeline
            # Clasificador local ligero para toxicidad y contenido inadecuado
            self.classifier = pipeline("text-classification", model="unitary/toxic-bert", device=-1)
        except Exception as e:
            logger.warning(f"Filtro Semántico de Salida no disponible de forma óptima: {str(e)}")

    def evaluate_and_replace(self, response_text: str, route_config: Dict[str, Any]) -> str:
        """
        Intercepta y reemplaza la respuesta por un mensaje genérico de bloqueo ante violaciones semánticas.
        """
        enabled = route_config.get("firewall", {}).get("semantic_output_filter_enabled", self.default_enabled)
        
        if not enabled:
            return response_text

        if self.classifier is None:
            # Comportamiento ante fallos: Registra WARN y permite la salida (Fail-Open controlado)
            logger.warning("Filtro Semántico de Usuario no disponible. Omitiendo verificación.", extra={
                "firewall_component": "semantic_output",
                "action": "passed"
            })
            return response_text

        try:
            prediction = self.classifier(response_text)[0]
            if prediction['label'] == 'toxic' and prediction['score'] > 0.80:
                logger.error(f"Respuesta interceptada por Filtro Semántico (Contenido Inapropiado). Score: {prediction['score']}", extra={
                    "firewall_component": "semantic_output",
                    "action": "blocked"
                })
                return self.blocked_message
        except Exception as e:
            logger.warning(f"Error en inferencia de Filtro Semántico: {str(e)}. Permitiendo salida por política Fail-Open.")
            
        return response_text
