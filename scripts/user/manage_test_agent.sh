#!/bin/bash

AGENT_DIR="agents/test_$(date +%Y%m%d_%H%M%S)"

case "$1" in
    create)
        echo "🔧 Creando agente temporal: $AGENT_DIR"
        mkdir -p "$AGENT_DIR/routes"
        
        cat > "$AGENT_DIR/config.yaml" << 'YAML'
id: "temp_test"
name: "Temporal Test"
description: "Agente temporal para pruebas - puede eliminarse"
short_term_memory_window: 3
execution_mode: "parallel"
llm_provider:
  name: "ollama"
  model: "phi4-mini"
  temperature: 0.3
rag_config:
  enabled: false
YAML
        
        cat > "$AGENT_DIR/routes/test.yaml" << 'YAML'
route_id: "test"
type: "cognitive"
description: "pruebas, verificar funcionamiento"
system_prompt: "Eres un asistente de pruebas. Responde de forma útil."
gatekeeper_required: false
YAML
        
        echo "✅ Agente creado en: $AGENT_DIR"
        echo "📝 Ejecuta 'python main.py' y selecciona 'Temporal Test'"
        ;;
    
    list)
        echo "🔍 Agentes temporales encontrados:"
        ls -d agents/test_* 2>/dev/null || echo "   Ninguno"
        ;;
    
    clean)
        echo "🧹 Eliminando agentes temporales..."
        rm -rf agents/test_* 2>/dev/null
        echo "✅ Limpieza completada"
        ;;
    
    *)
        echo "Uso: $0 {create|list|clean}"
        exit 1
        ;;
esac
