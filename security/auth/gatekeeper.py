import sys
import select
import logging
import time
from collections import defaultdict
from security.auth.audit import audit

logger = logging.getLogger("ferdonan.core.gatekeeper")

class Gatekeeper:
    def __init__(self, default_timeout: int = 60, force_all: bool = False):
        self.default_timeout = default_timeout
        self.force_all = force_all
        self._session_cache = {}  # route_id -> bool (aprobado/rechazado en esta sesión)
        self._session_id = id(self)  # Identificador de sesión

    def verify(self, route_id: str, route_config: dict, request_id: str) -> bool:
        """
        Evalúa y ejecuta la confirmación humana si la ruta o la configuración global lo requieren.
        Regla #11: Verificación explícita.
        """
        # Verificar caché de sesión
        if route_id in self._session_cache:
            cached_decision = self._session_cache[route_id]
            logger.info(f"Gatekeeper usando decisión en caché para ruta '{route_id}': {'aprobada' if cached_decision else 'rechazada'}")
            print(f"\033[90m[GATEKEEPER] Usando decisión previa para '{route_id}' (aprobada: {cached_decision})\033[0m")
            return cached_decision
        
        gatekeeper_required = route_config.get("configuration", {}).get("gatekeeper_required", False)
        
        if not gatekeeper_required and not self.force_all:
            audit.log_approval(route_id, True, "Gatekeeper no requerido (ruta sin restricciones)")
            self._session_cache[route_id] = True
            return True

        print(f"\n[GATEKEEPER] ATENCIÓN: La ruta '{route_id}' requiere aprobación humana.")
        print(f"[REQUEST ID: {request_id}] ¿Desea permitir la ejecución? (Y/N): ", end="", flush=True)

        # Implementación de timeout compatible con sistemas POSIX (Fedora)
        rlist, _, _ = select.select([sys.stdin], [], [], self.default_timeout)
        
        if rlist:
            user_input = sys.stdin.readline().strip().upper()
            if user_input == 'Y':
                audit.log_approval(route_id, True, "Aprobado por usuario", {"input": "Y"})
                self._session_cache[route_id] = True
                logger.info({
                    "event": "gatekeeper_action",
                    "action": "confirmed",
                    "route_id": route_id,
                    "request_id": request_id
                })
                print("[GATEKEEPER] Acción confirmada por el usuario.")
                return True
            else:
                audit.log_approval(route_id, False, "Rechazado por usuario", {"input": user_input if user_input else "N"})
                self._session_cache[route_id] = False
                logger.warning({
                    "event": "gatekeeper_action",
                    "action": "rejected",
                    "route_id": route_id,
                    "request_id": request_id
                })
                print("\n[GATEKEEPER] Acción rechazada por el usuario.")
                return False
        else:
            audit.log_approval(route_id, False, f"Timeout después de {self.default_timeout}s")
            self._session_cache[route_id] = False
            logger.error({
                "event": "gatekeeper_action",
                "action": "timeout",
                "route_id": route_id,
                "request_id": request_id
            })
            print(f"\n[GATEKEEPER] Tiempo de espera agotado ({self.default_timeout}s). Acción rechazada por defecto (Fail-Closed).")
            return False
