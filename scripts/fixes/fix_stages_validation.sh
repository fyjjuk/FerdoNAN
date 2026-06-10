#!/bin/bash
# Fix #1: Inyectar validación de stages en CognitiveExecutor.execute()
# Problema: _validate_stage_output() existe pero nunca se invoca

EXECUTOR_FILE="services/executor/cognitive.py"

echo "==== FIX #1: Stages Validation Injection ===="
echo "Target: $EXECUTOR_FILE"
echo ""

# Buscar la línea donde se asigna final_output
SEARCH_PATTERN='final_output = output  # la última etapa será la respuesta final'

# Verificar si existe
if grep -q "$SEARCH_PATTERN" "$EXECUTOR_FILE"; then
    echo "✓ Patrón encontrado"
    
    # Crear backup
    cp "$EXECUTOR_FILE" "${EXECUTOR_FILE}.backup_stages"
    echo "✓ Backup creado: ${EXECUTOR_FILE}.backup_stages"
    
    # Reemplazar: agregar validación antes de asignar final_output
    cat > /tmp/patch_stages.py << 'EOF'
import sys

with open(sys.argv[1], 'r') as f:
    content = f.read()

# Buscar el bloque donde se procesa cada stage
old_block = '''            output = llm.generate_response(formatted_prompt, system_prompt, llm_config)
            
            final_output = output  # la última etapa será la respuesta final'''

new_block = '''            output = llm.generate_response(formatted_prompt, system_prompt, llm_config)
            
            # === VALIDACIÓN DE STAGE ===
            if not self._validate_stage_output(output, stage_name, output_key):
                logger.error(f"Stage '{stage_name}' falló validación. Output: {output[:100]}")
                raise ValueError(f"Stage '{stage_name}' produjo salida inválida")
            # === FIN VALIDACIÓN ===
            
            final_output = output  # la última etapa será la respuesta final'''

if old_block in content:
    content = content.replace(old_block, new_block)
    with open(sys.argv[1], 'w') as f:
        f.write(content)
    print("✓ Bloque de validación inyectado")
else:
    print("✗ Patrón de reemplazo no encontrado (estructura diferente)")
    sys.exit(1)
EOF

    python3 /tmp/patch_stages.py "$EXECUTOR_FILE"
    
    if [ $? -eq 0 ]; then
        echo "✓ Validación de stages inyectada correctamente"
        echo ""
        echo "Cambios aplicados:"
        echo "  - Llamada a _validate_stage_output() después de LLM.generate_response()"
        echo "  - Lanzamiento de ValueError si validación falla"
        echo "  - Logging de errores detallado"
    else
        echo "✗ Error en inyección de validación"
        cp "${EXECUTOR_FILE}.backup_stages" "$EXECUTOR_FILE"
        exit 1
    fi
else
    echo "✗ Patrón no encontrado. Verifique estructura actual:"
    echo ""
    grep -n "final_output = output" "$EXECUTOR_FILE" || echo "  (no encontrado)"
    exit 1
fi
