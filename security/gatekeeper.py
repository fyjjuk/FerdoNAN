import sys
import select
import logging
import time

logger = logging.getLogger("ferdonan.core.gatekeeper")

class Gatekeeper:
    def __init__(self, default_timeout: int = 60, force_all: bool = False):
        self.default_timeout = default_timeout
        self.force_all = force_all

    def verify(self, route_id: str, route_config: dict, request_id: str) -> bool:
        """
        Evalúa y ejecuta la confirmación humana si la ruta o la configuración global lo requieren.
        Regla #11: Verificación explícita.
        """
        gatekeeper_required = route_config.get("configuration", {}).get("gatekeeper_required", False)
        
        if not gatekeeper_required and not self.force_all:
            return True

        print(f"\n[GATEKEEPER] ATENCIÓN: La ruta '{route_id}' requiere aprobación humana.")
        print(f"[REQUEST ID: {request_id}] ¿Desea permitir la ejecución? (Y/N): ", end="", flush=True)

        # Implementación de timeout compatible con sistemas POSIX (Fedora)
        rlist, _, _ = select.select([sys.stdin], [], [], self.default_timeout)
        
        if rlist:
            user_input = sys.stdin.readline().strip().upper()
            if user_input == 'Y':
                logger.info({
                    "event": "gatekeeper_action",
                    "action": "confirmed",
                    "route_id": route_id,
                    "request_id": request_id
                })
                print("[GATEKEEPER] Acción confirmada por el usuario.")
                return True
            else:
                logger.warning({
                    "event": "gatekeeper_action",
                    "action": "rejected",
                    "route_id": route_id,
                    "request_id": request_id
                })
                print("\n[GATEKEEPER] Acción rechazada por el usuario.")
                return False
        else:
            logger.error({
                "event": "gatekeeper_action",
                "action": "timeout",
                "route_id": route_id,
                "request_id": request_id
            })
            print(f"\n[GATEKEEPER] Tiempo de espera agotado ({self.default_timeout}s). Acción rechazada por defecto (Fail-Closed).")
            return False
