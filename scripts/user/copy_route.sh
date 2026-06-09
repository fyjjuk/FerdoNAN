#!/bin/bash
# Uso: ./copy_route.sh <nombre_ruta> <id_agente>
# Ejemplo: ./copy_route.sh web_search mi_agente

LIBRARY="route_library"
AGENTS_DIR="agents"

if [ $# -ne 2 ]; then
    echo "Uso: $0 <nombre_ruta_sin_extensión> <id_agente>"
    echo "Rutas disponibles:"
    ls -1 "$LIBRARY"/*.yaml 2>/dev/null | xargs -n 1 basename | sed 's/\.yaml$//'
    exit 1
fi

ROUTE_NAME="$1"
AGENT_ID="$2"
ROUTE_FILE="$LIBRARY/$ROUTE_NAME.yaml"
AGENT_ROUTES_DIR="$AGENTS_DIR/$AGENT_ID/routes"

if [ ! -f "$ROUTE_FILE" ]; then
    echo "❌ Ruta '$ROUTE_NAME' no encontrada en $LIBRARY"
    exit 1
fi

if [ ! -d "$AGENT_ROUTES_DIR" ]; then
    echo "❌ Agente '$AGENT_ID' no existe o no tiene directorio de rutas"
    exit 1
fi

cp "$ROUTE_FILE" "$AGENT_ROUTES_DIR/"
echo "✅ Ruta '$ROUTE_NAME' copiada a $AGENT_ROUTES_DIR/"
echo "   Recuerda editar 'route_id' y otros campos si es necesario."
