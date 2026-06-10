#!/bin/bash
# Fix #2: Verificar gatekeeper está siendo invocado correctamente
# Problema: Gatekeeper existe pero gatekeeper_required está siempre false en rutas

GATEKEEPER_FILE="security/gatekeeper.py"
ENGINE_FILE="core/engine.py"

echo "==== FIX #2: Gatekeeper Activation Checkpoint ===="
echo ""

# Verificar que gatekeeper está siendo invocado en engine
if grep -q "if gatekeeper_required or force_gatekeeper:" "$ENGINE_FILE"; then
    echo "✓ Gatekeeper checkpoint exists en engine.py"
    
    # Ahora necesitamos habilitar gatekeeper_required en rutas críticas
    # Crear script para auditar y reportar rutas
    
    cat > /tmp/audit_gatekeeper_routes.py << 'EOF'
import os
import yaml
import json

agents_dir = "agents"
critical_routes = {}  # route_id -> config
insecure_routes = []  # rutas con gatekeeper_required=false

for agent_folder in os.listdir(agents_dir):
    agent_path = os.path.join(agents_dir, agent_folder)
    if not os.path.isdir(agent_path):
        continue
    
    routes_dir = os.path.join(agent_path, "routes")
    if not os.path.exists(routes_dir):
        continue
    
    for route_file in os.listdir(routes_dir):
        if not route_file.endswith('.yaml'):
            continue
        
        route_path = os.path.join(routes_dir, route_file)
        with open(route_path, 'r') as f:
            route_config = yaml.safe_load(f)
        
        route_id = route_config.get('route_id', 'unknown')
        gatekeeper_req = route_config.get('gatekeeper_required', False)
        
        if gatekeeper_req:
            critical_routes[route_id] = {
                "file": route_path,
                "type": route_config.get('type'),
                "status": "✓ PROTEGIDA"
            }
        else:
            insecure_routes.append({
                "route_id": route_id,
                "file": route_path,
                "type": route_config.get('type'),
                "tools": route_config.get('tools_allowed', [])
            })

print("\n" + "="*70)
print("REPORTE: Rutas sin Gatekeeper (gatekeeper_required=false)")
print("="*70)

if insecure_routes:
    print(f"\nTotal rutas sin protección: {len(insecure_routes)}\n")
    for route in insecure_routes:
        print(f"  Route: {route['route_id']}")
        print(f"    File: {route['file']}")
        print(f"    Type: {route['type']}")
        if route['tools']:
            print(f"    Tools: {', '.join(route['tools'])}")
        print()
else:
    print("\nTodas las rutas están protegidas ✓\n")

print("\nRutas CRÍTICAS que deberían tener gatekeeper=true:")
print("  - spotify_player/reproducir (acceso a sistema)")
print("  - spotify_player/control_directo")
print("  - narrador_dnd/trama_principal (si modifica persistencia)")

EOF

    python3 /tmp/audit_gatekeeper_routes.py
    
else
    echo "✗ Gatekeeper checkpoint NO ENCONTRADO en engine.py"
    echo "  Verificar que bootstrap_core() está inyectando Gatekeeper"
    exit 1
fi

echo ""
echo "==== SIGUIENTES PASOS ===="
echo "1. Revisar output arriba para identificar rutas críticas"
echo "2. Editar agents/[agent]/routes/[critical].yaml"
echo "3. Cambiar 'gatekeeper_required: false' → 'gatekeeper_required: true'"
echo "4. Prueba: python main.py y ejecutar ruta protegida"
echo ""
