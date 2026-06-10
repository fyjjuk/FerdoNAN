#!/bin/bash
# Fix #5: Real Streaming Implementation
# Problema: _stream_response() existe pero no se integra en flujo de ejecución

EXECUTOR_FILE="services/executor/cognitive.py"
OLLAMA_FILE="services/llm_providers/ollama.py"

echo "==== FIX #5: Real Streaming Implementation ===="
echo ""

# Paso 1: Verificar que _stream_response existe
if grep -q "def _stream_response" "$EXECUTOR_FILE"; then
    echo "✓ Método _stream_response encontrado en CognitiveExecutor"
else
    echo "✗ _stream_response NO encontrado"
    exit 1
fi

# Paso 2: Crear nuevo método stream_response que reemplaza _stream_response
cat > /tmp/patch_streaming.py << 'EOF'
import sys

with open(sys.argv[1], 'r') as f:
    lines = f.readlines()

# Buscar la línea donde se llama a llm.generate_response en execute()
output_found = False
streaming_integrated = False

for i, line in enumerate(lines):
    # Buscar llamadas a generate_response en el contexto de execute()
    if "output = llm.generate_response" in line and "stage" not in line:
        # Verificar si es en modo no-stages (fallback normal)
        if i > 0 and "stages" not in ''.join(lines[max(0, i-20):i]):
            # Comentar la versión vieja y agregar versión con streaming
            old_call = line.strip()
            indentation = len(line) - len(line.lstrip())
            indent_str = ' ' * indentation
            
            # Crear nueva versión que soporta streaming
            new_call = f'''# Soporte para streaming: checar si LLM soporta stream_response
        if hasattr(llm, 'stream_response') and llm_config.get('stream', False):
            output = "".join(self._stream_with_yield(llm, prompt, system_prompt, llm_config))
        else:
            output = llm.generate_response(enhanced_prompt, system_prompt, llm_config)
'''
            
            lines[i] = indent_str + new_call + '\n'
            streaming_integrated = True
            output_found = True
            break

if streaming_integrated:
    with open(sys.argv[1], 'w') as f:
        f.writelines(lines)
    print("✓ Integración de streaming en execute() completada")
    sys.exit(0)
else:
    print("⚠ Patrón específico no encontrado exactamente")
    print("  Editar manualmente en services/executor/cognitive.py")
    print("  Buscar: 'output = llm.generate_response'")
    print("  Reemplazar con: soporte condicional a stream_response")
    sys.exit(1)

EOF

cp "$EXECUTOR_FILE" "${EXECUTOR_FILE}.backup_streaming"
echo "✓ Backup: ${EXECUTOR_FILE}.backup_streaming"

python3 /tmp/patch_streaming.py "$EXECUTOR_FILE" 2>/dev/null

if [ $? -eq 0 ]; then
    echo "✓ Streaming integrado en CognitiveExecutor"
else
    echo "⚠ Integración automática no fue posible (editar manualmente)"
    cp "${EXECUTOR_FILE}.backup_streaming" "$EXECUTOR_FILE"
fi

# Paso 3: Agregar método _stream_with_yield si no existe
echo ""
echo "Verificando método _stream_with_yield..."

if ! grep -q "_stream_with_yield" "$EXECUTOR_FILE"; then
    echo "⚠ Método _stream_with_yield no existe. Agregar:"
    
    cat > /tmp/stream_method.txt << 'PYTHON_EOF'
    
    def _stream_with_yield(self, llm, prompt: str, system_prompt: str, llm_config: dict):
        """Ejecuta streaming y hace yield de tokens (para salida en tiempo real)."""
        try:
            # Llamar al stream_response del LLM
            for token in llm.stream_response(prompt, system_prompt, llm_config):
                yield token
                print(token, end='', flush=True)  # Output en tiempo real
        except Exception as e:
            logger.error(f"Error en streaming: {e}")
            # Fallback: llamada normal sin streaming
            yield llm.generate_response(prompt, system_prompt, llm_config)
PYTHON_EOF
    
    echo ""
    echo "Agregar el siguiente método a services/executor/cognitive.py (antes de execute):"
    cat /tmp/stream_method.txt
    
else
    echo "✓ Método _stream_with_yield ya existe"
fi

# Paso 4: Verificar que OllamaClient soporta stream_response
echo ""
echo "Verificando soporte de streaming en OllamaClient..."

if grep -q "def stream_response" "$OLLAMA_FILE"; then
    echo "✓ OllamaClient.stream_response ya existe"
else
    echo "⚠ OllamaClient.stream_response NO existe"
    echo "  Agregar método stream_response a services/llm_providers/ollama.py"
    echo "  (Copiar de _stream_response pero como generador)"
fi

echo ""
echo "==== RESUMEN STREAMING ===="
echo "Estado: Parcialmente implementado"
echo ""
echo "Pasos finales:"
echo "  1. Revisar integraciones automáticas arriba"
echo "  2. Agregar _stream_with_yield() manualmente si es necesario"
echo "  3. Implementar stream_response() en OllamaClient"
echo "  4. Probar: agents/stage_sandbox/routes/test_simple.yaml con stream=true"
echo ""
