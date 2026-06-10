#!/bin/bash
# Verification script: Diagnostica el estado actual antes de aplicar fixes

PROJECT_DIR="$PWD"

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
cat << 'BANNER'
╔════════════════════════════════════════════════════════════════════╗
║           FERDONAN v2.0 - PRE-FIX VERIFICATION                     ║
║                                                                    ║
║  Diagnóstico del estado actual del proyecto                       ║
╚════════════════════════════════════════════════════════════════════╝
BANNER
echo -e "${NC}"
echo ""

# Verificar que estamos en directorio correcto
if [ ! -f "main.py" ] || [ ! -d "agents" ]; then
    echo -e "${RED}✗ ERROR: No estamos en directorio raíz de FerdoNAN${NC}"
    echo "  Ejecutar desde: ~/ferdonan"
    exit 1
fi

echo -e "${GREEN}✓ Verificación de directorio${NC}"
echo ""

# ==============================================================================
# 1. Verificar estructura de archivos críticos
# ==============================================================================

echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}1. ESTRUCTURA DE ARCHIVOS CRÍTICOS${NC}"
echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
echo ""

CRITICAL_FILES=(
    "core/engine.py"
    "services/executor/cognitive.py"
    "services/vector_store.py"
    "orchestration/resource_manager.py"
    "security/gatekeeper.py"
    "config/settings.py"
)

for file in "${CRITICAL_FILES[@]}"; do
    if [ -f "$file" ]; then
        size=$(wc -l < "$file")
        echo -e "${GREEN}✓${NC} $file ($size líneas)"
    else
        echo -e "${RED}✗${NC} $file (NO ENCONTRADO)"
    fi
done

echo ""

# ==============================================================================
# 2. Diagnóstico de Fix #1: Stages Validation
# ==============================================================================

echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}2. DIAGNÓSTICO FIX #1: STAGES VALIDATION${NC}"
echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
echo ""

echo "Buscando: _validate_stage_output() método..."
if grep -q "_validate_stage_output" services/executor/cognitive.py; then
    echo -e "${GREEN}✓${NC} Método existe"
    
    if grep -q "if not self._validate_stage_output" services/executor/cognitive.py; then
        echo -e "${GREEN}  ✓ Validación ya está siendo invocada${NC}"
    else
        echo -e "${RED}  ✗ Validación NO está siendo invocada (VULNERABLE)${NC}"
        echo "     → Fix #1 REQUERIDA"
    fi
else
    echo -e "${RED}✗${NC} Método NO existe"
fi

echo ""

# ==============================================================================
# 3. Diagnóstico de Fix #2: Gatekeeper
# ==============================================================================

echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}3. DIAGNÓSTICO FIX #2: GATEKEEPER${NC}"
echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
echo ""

echo "Verificando gatekeeper_required en rutas..."
gatekeeper_true=$(grep -r "gatekeeper_required: true" agents/ 2>/dev/null | wc -l)
gatekeeper_false=$(grep -r "gatekeeper_required: false" agents/ 2>/dev/null | wc -l)
gatekeeper_missing=$(find agents/ -name "*.yaml" -type f 2>/dev/null | xargs grep -L "gatekeeper_required" 2>/dev/null | wc -l)

echo "  gatekeeper_required: true  = $gatekeeper_true rutas"
echo "  gatekeeper_required: false = $gatekeeper_false rutas"
echo "  Sin gatekeeper_required    = $gatekeeper_missing rutas"

if [ "$gatekeeper_true" -eq 0 ]; then
    echo -e "${RED}  ✗ NINGUNA ruta está protegida (VULNERABLE)${NC}"
    echo "     → Fix #2 REQUERIDA"
else
    echo -e "${GREEN}  ✓ Algunas rutas están protegidas${NC}"
fi

echo ""

# ==============================================================================
# 4. Diagnóstico de Fix #3: RAG Injection
# ==============================================================================

echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}4. DIAGNÓSTICO FIX #3: RAG INJECTION HARDENING${NC}"
echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
echo ""

echo "Buscando sanitización en rag_query()..."
if grep -q "def rag_query" services/vector_store.py; then
    echo -e "${GREEN}✓${NC} Método rag_query existe"
    
    if grep -A10 "def rag_query" services/vector_store.py | grep -q "isinstance.*str"; then
        echo -e "${GREEN}  ✓ Validación de tipo detectada${NC}"
    else
        echo -e "${RED}  ✗ Sin validación de tipo (VULNERABLE)${NC}"
        echo "     → Fix #3 REQUERIDA"
    fi
else
    echo -e "${RED}✗${NC} Método rag_query NO existe"
fi

echo ""

# ==============================================================================
# 5. Diagnóstico de Fix #4: Resource Profiles
# ==============================================================================

echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}5. DIAGNÓSTICO FIX #4: DYNAMIC RESOURCE PROFILES${NC}"
echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
echo ""

echo "Buscando lógica de perfiles dinámicos..."
if grep -q "def select_resource_profile" orchestration/resource_manager.py; then
    echo -e "${GREEN}✓${NC} Método select_resource_profile existe"
    
    if grep -A20 "def select_resource_profile" orchestration/resource_manager.py | grep -q "cpu_percent"; then
        echo -e "${GREEN}  ✓ CPU consideration detectado${NC}"
    else
        echo -e "${RED}  ✗ Sin consideración de CPU (MEJORA REQUERIDA)${NC}"
        echo "     → Fix #4 RECOMENDADA"
    fi
else
    echo -e "${RED}✗${NC} Método NO existe"
fi

echo ""

# ==============================================================================
# 6. Diagnóstico de Fix #5: Streaming
# ==============================================================================

echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}6. DIAGNÓSTICO FIX #5: REAL STREAMING${NC}"
echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
echo ""

echo "Buscando streaming en CognitiveExecutor..."
if grep -q "_stream_response" services/executor/cognitive.py; then
    echo -e "${GREEN}✓${NC} Método _stream_response existe"
    
    if grep "execute" services/executor/cognitive.py | grep -q "_stream"; then
        echo -e "${GREEN}  ✓ Streaming está siendo invocado${NC}"
    else
        echo -e "${RED}  ✗ Streaming NO está integrado (MEJORA REQUERIDA)${NC}"
        echo "     → Fix #5 RECOMENDADA"
    fi
else
    echo -e "${RED}✗${NC} Método _stream_response NO existe"
fi

echo ""

# ==============================================================================
# 7. Diagnóstico de Fix #6: Critical Routes
# ==============================================================================

echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}7. DIAGNÓSTICO FIX #6: CRITICAL ROUTES PROTECTION${NC}"
echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
echo ""

echo "Analizando rutas críticas (spotify, linux)..."
critical_routes=(
    "agents/spotify_player/routes/reproducir.yaml"
    "agents/spotify_player/routes/control_directo.yaml"
    "agents/spotify_player/routes/control_rapido.yaml"
    "agents/experto_linux/routes/comandos_basicos.yaml"
)

protected=0
unprotected=0

for route in "${critical_routes[@]}"; do
    if [ -f "$route" ]; then
        if grep -q "gatekeeper_required: true" "$route"; then
            echo -e "${GREEN}✓${NC} $route (PROTEGIDA)"
            ((protected++))
        else
            echo -e "${RED}✗${NC} $route (SIN PROTEGER)"
            ((unprotected++))
        fi
    else
        echo -e "${YELLOW}?${NC} $route (no encontrada)"
    fi
done

echo ""
echo "Resumen: $protected protegidas, $unprotected sin proteger"

if [ "$unprotected" -gt 0 ]; then
    echo -e "${RED}  ✗ Rutas críticas sin protección (VULNERABLE)${NC}"
    echo "     → Fix #6 REQUERIDA"
else
    echo -e "${GREEN}  ✓ Todas las rutas críticas están protegidas${NC}"
fi

echo ""

# ==============================================================================
# 8. Diagnóstico General
# ==============================================================================

echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}8. SINTAXIS Y LIBRERÍAS${NC}"
echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
echo ""

echo "Verificando sintaxis Python..."
python_errors=0

files_to_check=(
    "core/engine.py"
    "services/executor/cognitive.py"
    "services/vector_store.py"
    "orchestration/resource_manager.py"
)

for file in "${files_to_check[@]}"; do
    if python3 -m py_compile "$file" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} $file (sintaxis OK)"
    else
        echo -e "${RED}✗${NC} $file (ERRORES DE SINTAXIS)"
        ((python_errors++))
    fi
done

echo ""

if [ "$python_errors" -gt 0 ]; then
    echo -e "${RED}✗ Hay errores de sintaxis detectados${NC}"
else
    echo -e "${GREEN}✓ Sintaxis Python OK${NC}"
fi

echo ""

# ==============================================================================
# RESUMEN FINAL
# ==============================================================================

echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}RESUMEN DE RECOMENDACIONES${NC}"
echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
echo ""

echo -e "${RED}FIXES CRÍTICAS (REQUIEREN CORRECCIÓN):${NC}"
echo "  □ Fix #1: Validación de Stages"
echo "  □ Fix #3: RAG Injection Hardening"
echo "  □ Fix #6: Critical Routes Protection"
echo ""

echo -e "${YELLOW}FIXES RECOMENDADAS (MEJORA):${NC}"
echo "  □ Fix #2: Gatekeeper Activation"
echo "  □ Fix #4: Dynamic Resource Profiles"
echo "  □ Fix #5: Real Streaming"
echo ""

echo -e "${GREEN}SIGUIENTES PASOS:${NC}"
echo "  1. Ejecutar: bash /home/claude/fix_interactive.sh"
echo "  2. O ejecutar: bash /home/claude/MASTER_FIX.sh"
echo "  3. Luego: pytest tests/ -v"
echo "  4. Finalmente: python main.py"
echo ""

echo "═════════════════════════════════════════════════════════════════"
echo "              ✓ VERIFICACIÓN COMPLETADA"
echo "═════════════════════════════════════════════════════════════════"
echo ""
