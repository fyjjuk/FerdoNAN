import re
import requests
from core.logger import logger

class Sanitizer:
    def __init__(self, enabled: bool = True, model: str = "phi4-mini", use_llm_threshold: int = 50):
        self.enabled = enabled
        self.model = model
        self.use_llm_threshold = use_llm_threshold
        self.ollama_url = "http://localhost:11434/api/generate"

    def _simple_clean(self, text: str) -> str:
        """Limpieza básica sin LLM (rápida)."""
        text = text.strip()
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\x20-\x7EáéíóúñÑüÜ¿?¡!]', '', text)
        return text

    def _is_likely_error(self, text: str) -> bool:
        """Detecta si la salida del LLM parece un mensaje de error o negación."""
        error_patterns = [
            r'no tengo información',
            r'lo siento',
            r'no sé',
            r'no puedo',
            r'error',
            r'no entiendo',
            r'no conozco'
        ]
        text_lower = text.lower()
        return any(re.search(pattern, text_lower) for pattern in error_patterns)

    def _llm_clean(self, text: str) -> str:
        """Usa LLM para limpiar consultas largas/complejas, con validación de salida."""
        prompt = f"""Limpia esta consulta eliminando muletillas, ruido y ambigüedades. Devuelve SOLO el texto limpio, sin explicaciones ni comillas.

Consulta: "{text}"
Texto limpio:"""
        try:
            response = requests.post(
                self.ollama_url,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.0, "num_predict": 200}
                },
                timeout=30  # Aumentado de 15 a 30 segundos
            )
            response.raise_for_status()
            cleaned = response.json().get("response", "").strip()
            # Eliminar posibles prefijos residuales
            cleaned = re.sub(r'^(Texto limpio:|La consulta limpia es:|Claro, aquí está:)\s*', '', cleaned, flags=re.IGNORECASE)
            cleaned = cleaned.strip('"\'')
            
            # Validar que la salida no sea un error aparente
            if not cleaned or self._is_likely_error(cleaned):
                logger.warning(f"Sanitizador LLM devolvió salida sospechosa: '{cleaned}'. Usando limpieza simple.")
                return self._simple_clean(text)
            
            return cleaned if cleaned else text
        except requests.exceptions.Timeout:
            logger.warning(f"Timeout en sanitizador LLM (30s). Usando limpieza simple.")
            return self._simple_clean(text)
        except Exception as e:
            logger.warning(f"Error en sanitizador LLM: {e}. Usando limpieza simple.")
            return self._simple_clean(text)

    def clean(self, user_input: str) -> str:
        if not self.enabled:
            return user_input
        if len(user_input) < self.use_llm_threshold:
            cleaned = self._simple_clean(user_input)
            logger.debug(f"Sanitizador (simple): '{user_input}' -> '{cleaned}'")
            return cleaned
        cleaned = self._llm_clean(user_input)
        logger.info(f"Sanitizador (LLM): '{user_input}' -> '{cleaned}'")
        return cleaned
