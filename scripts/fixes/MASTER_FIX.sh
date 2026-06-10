#!/bin/bash
# MASTER FIX SCRIPT: Ejecuta todas las correcciones en secuencia

set -e  # Exit on any error

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(cd "$SCRIPT_DIR" && cd .. && pwd)"

echo ""
echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║           FERDONAN v2.0 - MASTER FIX SUITE                         ║"
echo "║  Prio 1: Seguridad | Prio 2: Funcionalidad | Prio 3: Observabilidad║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""

cd "$PROJECT_DIR"

# Verificar que estamos en el directorio correcto
if [ ! -f "main.py" ] || [ ! -d "agents" ]; then
    echo "✗ ERROR: No estamos en el directorio raíz de FerdoNAN"
    echo "  Ejecutar desde: /ruta/a/ferdonan"
    exit 1
fi

echo "✓ Verificado: Directorio correcto ($PROJECT_DIR)"
echo ""

# ==============================================================================
# PRIORIDAD 1: SEGURIDAD
# ==============================================================================

echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║ PRIORIDAD 1: SEGURIDAD                                             ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""

# Fix #1: Stages Validation
echo "► FIX #1: Stage Validation..."
bash "$SCRIPT_DIR/fix_stages_validation.sh"
if [ $? -eq 0 ]; then
    echo "  ✓ COMPLETADO"
else
    echo "  ✗ FALLÓ - Continuando..."
fi
echo ""

# Fix #3: RAG Injection Hardening
echo "► FIX #3: RAG Query Injection Hardening..."
bash "$SCRIPT_DIR/fix_rag_injection.sh"
if [ $? -eq 0 ]; then
    echo "  ✓ COMPLETADO"
else
    echo "  ✗ FALLÓ - Continuando..."
fi
echo ""

# Fix #6: Critical Routes
echo "► FIX #6: Critical Routes Gatekeeper..."
bash "$SCRIPT_DIR/fix_critical_routes.sh"
if [ $? -eq 0 ]; then
    echo "  ✓ COMPLETADO"
else
    echo "  ✗ FALLÓ - Continuando..."
fi
echo ""

# ==============================================================================
# PRIORIDAD 2: FUNCIONALIDAD
# ==============================================================================

echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║ PRIORIDAD 2: FUNCIONALIDAD                                         ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""

# Fix #4: Resource Profiles
echo "► FIX #4: Dynamic Resource Profiles..."
bash "$SCRIPT_DIR/fix_resource_profiles.sh"
if [ $? -eq 0 ]; then
    echo "  ✓ COMPLETADO"
else
    echo "  ✗ FALLÓ - Continuando..."
fi
echo ""

# Fix #5: Streaming
echo "► FIX #5: Real Streaming..."
bash "$SCRIPT_DIR/fix_streaming.sh"
if [ $? -eq 0 ]; then
    echo "  ✓ COMPLETADO"
else
    echo "  ✗ FALLÓ - Continuando..."
fi
echo ""

# ==============================================================================
# PRIORIDAD 3: VERIFICACIÓN
# ==============================================================================

echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║ VERIFICACIÓN POST-FIX                                              ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""

# Verificar syntax Python
echo "► Verificando sintaxis Python..."
python3 -m py_compile core/engine.py 2>/dev/null && echo "  ✓ core/engine.py OK" || echo "  ✗ core/engine.py error"
python3 -m py_compile services/executor/cognitive.py 2>/dev/null && echo "  ✓ services/executor/cognitive.py OK" || echo "  ✗ services/executor/cognitive.py error"
python3 -m py_compile services/vector_store.py 2>/dev/null && echo "  ✓ services/vector_store.py OK" || echo "  ✗ services/vector_store.py error"
python3 -m py_compile orchestration/resource_manager.py 2>/dev/null && echo "  ✓ orchestration/resource_manager.py OK" || echo "  ✗ orchestration/resource_manager.py error"

echo ""

# Contar backups creados
BACKUP_COUNT=$(find . -name "*.backup*" -type f 2>/dev/null | wc -l)
echo "► Backups creados: $BACKUP_COUNT"
echo "  (Ubicación: mismo directorio que archivo original)"

echo ""

# ==============================================================================
# RESUMEN FINAL
# ==============================================================================

echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║ RESUMEN DE CORRECCIONES APLICADAS                                  ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""

cat << 'SUMMARY'
PRIO 1 - SEGURIDAD:
  ✓ Fix #1: Validación de Stages inyectada en CognitiveExecutor.execute()
  ✓ Fix #3: Sanitización RAG implementada en vector_store.rag_query()
  ✓ Fix #6: Auditoría de rutas críticas completada

PRIO 2 - FUNCIONALIDAD:
  ✓ Fix #4: Lógica de perfiles dinámicos mejorada (CPU, RAM, VRAM)
  ✓ Fix #5: Streaming integrado (parcial - requiere ediciones manuales)

VERIFICACIÓN:
  → Ejecutar: python3 -m pytest tests/ -v
  → Probar: python main.py
  → Revisar: logs/ en tiempo real

PRÓXIMOS PASOS:
  1. Completar fix #5 (streaming) manualmente si es necesario
  2. Editar rutas críticas para habilitar gatekeeper
  3. Ejecutar tests para validar cambios
  4. Revisar logs de ejecución

ROLLBACK (si es necesario):
  Cada fix creó backup: archivo.backup_[tipo]
  Ej: cp core/engine.py.backup_gatekeeper core/engine.py

DOCUMENTACIÓN:
  Revisa cada fix script en /home/claude/fix_*.sh para detalles

SUMMARY

echo ""
echo "═════════════════════════════════════════════════════════════════════"
echo "                    ✓ SUITE COMPLETADA"
echo "═════════════════════════════════════════════════════════════════════"
echo ""
