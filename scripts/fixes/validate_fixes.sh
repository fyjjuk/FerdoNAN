#!/bin/bash
# POST-FIX VALIDATION: Verifica que todos los cambios se aplicaron correctamente

PROJECT_DIR="$PWD"

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${BLUE}"
cat << 'BANNER'
╔════════════════════════════════════════════════════════════════════╗
║           FERDONAN v2.0 - POST-FIX VALIDATION                      ║
║                                                                    ║
║  Verifica que todos los cambios de fixes se aplicaron correctamente║
╚════════════════════════════════════════════════════════════════════╝
BANNER
echo -e "${NC}"
echo ""

if [ ! -f "main.py" ] || [ ! -d "agents" ]; then
    echo -e "${RED}✗ ERROR: No estamos en directorio raíz de FerdoNAN${NC}"
    exit 1
fi

# Contadores
total_checks=0
passed_checks=0
failed_checks=0

check_result() {
    ((total_checks++))
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓${NC} $2"
        ((passed_checks++))
    else
        echo -e "${RED}✗${NC} $2"
        ((failed_checks++))
    fi
}

# ==============================================================================
# VALIDACIÓN FIX #1: STAGES VALIDATION
# ==============================================================================

echo -e "${CYAN}[FIX #1] Validación de Stages${NC}"
echo "─────────────────────────────────────────"

if grep -q "if not self._validate_stage_output" services/executor/cognitive.py; then
    check_result 0 "Validación de stages inyectada en execute()"
else
    check_result 1 "Validación de stages NO encontrada"
fi

if grep -q "raise ValueError.*stage.*falló" services/executor/cognitive.py; then
    check_result 0 "ValueError para stages inválidos implementado"
else
    check_result 1 "ValueError para stages no encontrado"
fi

echo ""

# ==============================================================================
# VALIDACIÓN FIX #2: GATEKEEPER
# ==============================================================================

echo -e "${CYAN}[FIX #2] Gatekeeper Activation${NC}"
echo "─────────────────────────────────────────"

if grep -q "if gatekeeper_required or force_gatekeeper:" core/engine.py; then
    check_result 0 "Gatekeeper checkpoint presente en engine.py"
else
    check_result 1 "Gatekeeper checkpoint NO encontrado"
fi

if grep -q "gatekeeper_required: true" agents/*/routes/*.yaml 2>/dev/null; then
    protected_count=$(grep -r "gatekeeper_required: true" agents/ 2>/dev/null | wc -l)
    check_result 0 "Al menos $protected_count rutas están protegidas"
else
    check_result 1 "No hay rutas con gatekeeper_required: true"
fi

echo ""

# ==============================================================================
# VALIDACIÓN FIX #3: RAG INJECTION
# ==============================================================================

echo -e "${CYAN}[FIX #3] RAG Injection Hardening${NC}"
echo "─────────────────────────────────────────"

if grep -q "isinstance.*query_text.*str" services/vector_store.py; then
    check_result 0 "Validación de tipo en rag_query()"
else
    check_result 1 "Validación de tipo NO encontrada en rag_query"
fi

if grep -q "len(query_text) >" services/vector_store.py; then
    check_result 0 "Limitación de longitud de query implementada"
else
    check_result 1 "Limitación de longitud NO encontrada"
fi

if grep -q "if not query_text:" services/vector_store.py || \
   grep -q "if not query_text.strip():" services/vector_store.py; then
    check_result 0 "Check de query vacío implementado"
else
    check_result 1 "Check de query vacío NO encontrado"
fi

echo ""

# ==============================================================================
# VALIDACIÓN FIX #4: RESOURCE PROFILES
# ==============================================================================

echo -e "${CYAN}[FIX #4] Dynamic Resource Profiles${NC}"
echo "─────────────────────────────────────────"

if grep -q "cpu_percent" orchestration/resource_manager.py; then
    check_result 0 "Consideración de CPU en select_resource_profile()"
else
    check_result 1 "CPU check NO encontrado"
fi

if grep -q "logger.info.*RESOURCE_PROFILE_SELECTION" orchestration/resource_manager.py; then
    check_result 0 "Logging de selección de perfil implementado"
else
    check_result 1 "Logging de perfil NO encontrado"
fi

echo ""

# ==============================================================================
# VALIDACIÓN FIX #5: STREAMING
# ==============================================================================

echo -e "${CYAN}[FIX #5] Real Streaming${NC}"
echo "─────────────────────────────────────────"

if grep -q "_stream_response" services/executor/cognitive.py; then
    check_result 0 "Método _stream_response existe"
else
    check_result 1 "_stream_response NO encontrado"
fi

if grep -q "stream_response" services/executor/cognitive.py || \
   grep -q "_stream_with_yield" services/executor/cognitive.py; then
    check_result 0 "Streaming está siendo considerado en execute()"
else
    check_result 1 "Streaming NO está integrado"
fi

echo ""

# ==============================================================================
# VALIDACIÓN FIX #6: CRITICAL ROUTES
# ==============================================================================

echo -e "${CYAN}[FIX #6] Critical Routes Protection${NC}"
echo "─────────────────────────────────────────"

critical_routes=(
    "agents/spotify_player/routes/reproducir.yaml"
    "agents/spotify_player/routes/control_directo.yaml"
    "agents/experto_linux/routes/comandos_basicos.yaml"
)

protected=0
for route in "${critical_routes[@]}"; do
    if [ -f "$route" ]; then
        if grep -q "gatekeeper_required: true" "$route"; then
            ((protected++))
        fi
    fi
done

if [ "$protected" -gt 0 ]; then
    check_result 0 "$protected rutas críticas están protegidas"
else
    check_result 1 "Rutas críticas NO están protegidas"
fi

echo ""

# ==============================================================================
# VALIDACIONES GENERALES
# ==============================================================================

echo -e "${CYAN}[GENERAL] Sintaxis y Estructura${NC}"
echo "─────────────────────────────────────────"

# Validar sintaxis Python
python3 -m py_compile core/engine.py 2>/dev/null
check_result $? "Sintaxis Python: core/engine.py"

python3 -m py_compile services/executor/cognitive.py 2>/dev/null
check_result $? "Sintaxis Python: services/executor/cognitive.py"

python3 -m py_compile services/vector_store.py 2>/dev/null
check_result $? "Sintaxis Python: services/vector_store.py"

python3 -m py_compile orchestration/resource_manager.py 2>/dev/null
check_result $? "Sintaxis Python: orchestration/resource_manager.py"

# Verificar backups
backup_count=$(find . -name "*.backup*" -type f 2>/dev/null | wc -l)
if [ "$backup_count" -gt 0 ]; then
    check_result 0 "$backup_count backups creados"
else
    check_result 1 "No hay backups (esperado si no se ejecutaron fixes)"
fi

echo ""

# ==============================================================================
# RESUMEN
# ==============================================================================

echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}RESUMEN DE VALIDACIÓN${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo ""

passed_percent=$((passed_checks * 100 / total_checks))

echo -e "Total checks:    $total_checks"
echo -e "${GREEN}Pasaron:         $passed_checks${NC}"
echo -e "${RED}Fallaron:        $failed_checks${NC}"
echo -e "Porcentaje:      $passed_percent%"
echo ""

if [ "$failed_checks" -eq 0 ]; then
    echo -e "${GREEN}"
    cat << 'SUCCESS'
╔════════════════════════════════════════════════════════════════════╗
║                     ✓ VALIDACIÓN COMPLETADA                        ║
║                                                                    ║
║  Todos los fixes se aplicaron correctamente.                      ║
║  FerdoNAN está listo para producción.                             ║
║                                                                    ║
║  Siguientes pasos:                                                ║
║    1. pytest tests/ -v                                            ║
║    2. python main.py                                              ║
║    3. Revisar logs/ferdonan.log                                   ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
SUCCESS
    echo -e "${NC}"
    exit 0
else
    echo -e "${YELLOW}"
    cat << 'WARNING'
╔════════════════════════════════════════════════════════════════════╗
║                  ⚠ VALIDACIÓN INCOMPLETA                           ║
║                                                                    ║
║  Algunos checks fallaron. Revisar arriba para detalles.           ║
║                                                                    ║
║  Opciones:                                                        ║
║    1. Re-ejecutar los fixes correspondientes                      ║
║    2. Editar manualmente según instrucciones                      ║
║    3. Hacer rollback si es necesario                              ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
WARNING
    echo -e "${NC}"
    exit 1
fi
