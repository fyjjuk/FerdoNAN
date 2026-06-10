#!/bin/bash
# Fix #6: Activate Gatekeeper on Critical Routes
# Identifica y habilita gatekeeper en rutas críticas

echo "==== FIX #6: Critical Routes Gatekeeper Activation ===="
echo ""

# Script Python para auditar e identificar rutas críticas
cat > /tmp/find_critical_routes.py << 'EOF'
import os
import yaml

agents_dir = "agents"
critical_keywords = [
    "reproducir", "control", "eliminar", "crear", "modificar",
    "ejecutar", "comando", "linux", "system", "script"
]

critical_routes = []

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
        description = route_config.get('description', '').lower()
        route_type = route_config.get('type', '').lower()
        tools = route_config.get('tools_allowed', [])
        
        is_critical = False
        reason = ""
        
        # Criterios de criticidad:
        # 1. Tiene herramientas permitidas (acceso a sistema)
        if tools:
            is_critical = True
            reason = f"Herramientas permitidas: {tools}"
        
        # 2. Keywords en descripción
        for keyword in critical_keywords:
            if keyword in description:
                is_critical = True
                reason = f"Keyword detectado: '{keyword}'"
                break
        
        # 3. Agentes específicamente críticos
        if agent_folder in ["spotify_player", "experto_linux"]:
            if route_id not in ["estado", "help"]:  # excepciones
                is_critical = True
                reason = f"Agente crítico: {agent_folder}"
        
        if is_critical:
            gatekeeper_status = route_config.get('gatekeeper_required', False)
            critical_routes.append({
                "agent": agent_folder,
                "route_id": route_id,
                "file": route_path,
                "is_protected": gatekeeper_status,
                "reason": reason,
                "tools": tools
            })

print("\n" + "="*80)
print("AUDITORÍA: Rutas Críticas Detectadas")
print("="*80 + "\n")

unprotected = [r for r in critical_routes if not r['is_protected']]
protected = [r for r in critical_routes if r['is_protected']]

print(f"Total rutas críticas: {len(critical_routes)}")
print(f"  ✓ Protegidas (gatekeeper=true): {len(protected)}")
print(f"  ✗ SIN PROTEGER (gatekeeper=false): {len(unprotected)}\n")

if unprotected:
    print("RUTAS QUE REQUIEREN GATEKEEPER:\n")
    for i, route in enumerate(unprotected, 1):
        print(f"{i}. {route['agent']}/{route['route_id']}")
        print(f"   File: {route['file']}")
        print(f"   Razón: {route['reason']}")
        if route['tools']:
            print(f"   Herramientas: {route['tools']}")
        print()

EOF

python3 /tmp/find_critical_routes.py
audit_result=$?

echo ""
echo "==== INSTRUCCIONES DE REMEDIACIÓN ===="
echo ""
echo "Para CADA ruta sin proteger en la lista arriba:"
echo ""
echo "1. Abrir el archivo .yaml"
echo "2. Cambiar: gatekeeper_required: false"
echo "3. A:       gatekeeper_required: true"
echo ""
echo "Ejemplo (Automated):"
echo ""

# Generar script de remediación
cat > /tmp/enable_gatekeeper.sh << 'BASH_SCRIPT'
#!/bin/bash

# Script para habilitar gatekeeper en rutas críticas de forma automática
# USO: bash /tmp/enable_gatekeeper.sh [ruta_archivo]

if [ -z "$1" ]; then
    echo "Uso: $0 <ruta_archivo.yaml>"
    echo ""
    echo "Ejemplo:"
    echo "  $0 agents/spotify_player/routes/reproducir.yaml"
    exit 1
fi

FILE=$1

if [ ! -f "$FILE" ]; then
    echo "✗ Archivo no encontrado: $FILE"
    exit 1
fi

# Crear backup
cp "$FILE" "${FILE}.backup_gatekeeper"
echo "✓ Backup creado: ${FILE}.backup_gatekeeper"

# Reemplazar usando sed
sed -i 's/gatekeeper_required: false/gatekeeper_required: true/g' "$FILE"
sed -i 's/gatekeeper_required:.*/gatekeeper_required: true/g' "$FILE"

# Verificar cambio
if grep -q "gatekeeper_required: true" "$FILE"; then
    echo "✓ Gatekeeper activado en: $FILE"
    echo ""
    echo "Contenido relevante:"
    grep -A2 -B2 "gatekeeper_required" "$FILE"
else
    echo "✗ Error al activar gatekeeper"
    cp "${FILE}.backup_gatekeeper" "$FILE"
    exit 1
fi

BASH_SCRIPT

chmod +x /tmp/enable_gatekeeper.sh

echo "#!/bin/bash"
echo "# Activar gatekeeper en rutas críticas"
echo ""

# Rutas conocidas como críticas
CRITICAL_ROUTES=(
    "agents/spotify_player/routes/reproducir.yaml"
    "agents/spotify_player/routes/control_directo.yaml"
    "agents/spotify_player/routes/control_rapido.yaml"
)

for route in "${CRITICAL_ROUTES[@]}"; do
    if [ -f "$route" ]; then
        echo "bash /tmp/enable_gatekeeper.sh $route"
    fi
done

echo ""
echo "==== VERIFICACIÓN ===="
echo "Tras ejecutar los comandos arriba, verificar:"
echo ""
echo "grep -r 'gatekeeper_required' agents/ | grep true"
echo ""
