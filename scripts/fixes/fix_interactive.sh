#!/bin/bash
# INTERACTIVE FIX SELECTOR

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(cd "$SCRIPT_DIR" && cd .. && pwd)"

cd "$PROJECT_DIR"

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

clear

echo -e "${BLUE}"
cat << 'BANNER'
╔════════════════════════════════════════════════════════════════════╗
║           FERDONAN v2.0 - INTERACTIVE FIX SUITE                    ║
║                                                                    ║
║  Selecciona qué vulnerabilidades corregir                         ║
║  (Prio 1=Seguridad | Prio 2=Funcionalidad | Prio 3=Observabilidad)║
╚════════════════════════════════════════════════════════════════════╝
BANNER
echo -e "${NC}"
echo ""

# Array de fixes disponibles
declare -a FIXES=(
    "1|PRIO 1 - Validación de Stages (CognitiveExecutor)|fix_stages_validation.sh"
    "2|PRIO 1 - Gatekeeper Activation Checkpoint|fix_gatekeeper_activation.sh"
    "3|PRIO 1 - RAG Query Injection Hardening|fix_rag_injection.sh"
    "4|PRIO 2 - Dynamic Resource Profiles|fix_resource_profiles.sh"
    "5|PRIO 2 - Real Streaming Implementation|fix_streaming.sh"
    "6|PRIO 2 - Critical Routes Protection|fix_critical_routes.sh"
    "ALL|Ejecutar TODOS los fixes (MASTER_FIX.sh)|MASTER_FIX.sh"
)

echo -e "${YELLOW}Fixes Disponibles:${NC}"
echo ""

for fix in "${FIXES[@]}"; do
    IFS='|' read -r num desc script <<< "$fix"
    printf "  %-2s) %-50s [%s]\n" "$num" "$desc" "$script"
done

echo ""
echo -e "${YELLOW}Opciones especiales:${NC}"
echo "  list)  Listar todos los fixes y sus detalles"
echo "  info)  Información sobre cada fix"
echo "  back)  Restaurar desde backups (rollback)"
echo "  exit)  Salir"
echo ""

# Loop de selección
while true; do
    echo -n -e "${BLUE}Selecciona opción [1-6|ALL|list|info|back|exit]: ${NC}"
    read -r selection
    
    case "$selection" in
        1)
            echo -e "\n${GREEN}Ejecutando: Fix #1 - Validación de Stages${NC}\n"
            bash "$SCRIPT_DIR/fix_stages_validation.sh"
            ;;
        2)
            echo -e "\n${GREEN}Ejecutando: Fix #2 - Gatekeeper Activation${NC}\n"
            bash "$SCRIPT_DIR/fix_gatekeeper_activation.sh"
            ;;
        3)
            echo -e "\n${GREEN}Ejecutando: Fix #3 - RAG Injection Hardening${NC}\n"
            bash "$SCRIPT_DIR/fix_rag_injection.sh"
            ;;
        4)
            echo -e "\n${GREEN}Ejecutando: Fix #4 - Dynamic Resource Profiles${NC}\n"
            bash "$SCRIPT_DIR/fix_resource_profiles.sh"
            ;;
        5)
            echo -e "\n${GREEN}Ejecutando: Fix #5 - Real Streaming${NC}\n"
            bash "$SCRIPT_DIR/fix_streaming.sh"
            ;;
        6)
            echo -e "\n${GREEN}Ejecutando: Fix #6 - Critical Routes Protection${NC}\n"
            bash "$SCRIPT_DIR/fix_critical_routes.sh"
            ;;
        ALL)
            echo -e "\n${GREEN}═══════════════════════════════════════════════════════════════${NC}"
            echo -e "${GREEN}Ejecutando MASTER_FIX.sh (TODOS los fixes)${NC}"
            echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}\n"
            bash "$SCRIPT_DIR/MASTER_FIX.sh"
            
            echo -e "\n${GREEN}═══════════════════════════════════════════════════════════════${NC}"
            echo -e "${GREEN}✓ MASTER_FIX completado${NC}"
            echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}\n"
            
            read -p "¿Deseas revisar más opciones? (s/N): " continue_opt
            if [[ ! "$continue_opt" =~ ^[Ss]$ ]]; then
                exit 0
            fi
            ;;
        list)
            echo -e "\n${YELLOW}Listado de Fixes Disponibles:${NC}\n"
            for fix in "${FIXES[@]}"; do
                IFS='|' read -r num desc script <<< "$fix"
                echo -e "${GREEN}Fix #$num:${NC} $desc"
                echo "  Script: $script"
                echo ""
            done
            ;;
        info)
            echo -e "\n${YELLOW}Información sobre cada Fix:${NC}\n"
            
            cat << 'INFO'
FIX #1 - Validación de Stages
  Problema: _validate_stage_output() existe pero no se invoca en flujo
  Solución: Inyectar validación en CognitiveExecutor.execute()
  Prioridad: CRÍTICA (seguridad)

FIX #2 - Gatekeeper Activation
  Problema: Gatekeeper existe pero gatekeeper_required=false en todas rutas
  Solución: Auditoría y activación en rutas críticas
  Prioridad: CRÍTICA (control de acceso)

FIX #3 - RAG Injection Hardening
  Problema: Sin sanitización de entrada antes de ChromaDB
  Solución: Validación y limitación de queries en vector_store.rag_query()
  Prioridad: CRÍTICA (inyección)

FIX #4 - Dynamic Resource Profiles
  Problema: Lógica incompleta de selección (CPU no considerado)
  Solución: Mejorar orchestration/resource_manager.select_resource_profile()
  Prioridad: ALTA (estabilidad)

FIX #5 - Real Streaming
  Problema: _stream_response() existe pero no se integra en execute()
  Solución: Integrar streaming en flujo normal con yield
  Prioridad: MEDIA (UX)

FIX #6 - Critical Routes Protection
  Problema: Rutas críticas (spotify, linux) sin protección
  Solución: Auditoría + activar gatekeeper en routes críticas
  Prioridad: CRÍTICA (seguridad)

INFO
            
            echo -e "\n${YELLOW}Recomendación:${NC}"
            echo "  Ejecuta fixes en orden: 1 → 3 → 6 → 4 → 5"
            echo ""
            ;;
        back)
            echo -e "\n${YELLOW}Opciones de Rollback:${NC}\n"
            
            # Listar backups disponibles
            backup_count=$(find . -name "*.backup*" -type f 2>/dev/null | wc -l)
            
            if [ "$backup_count" -eq 0 ]; then
                echo -e "${RED}No hay backups disponibles${NC}"
            else
                echo -e "${GREEN}Backups encontrados: $backup_count${NC}\n"
                find . -name "*.backup*" -type f -printf "  %p\n" | sort
                
                echo ""
                echo -e "${YELLOW}Para restaurar un archivo:${NC}"
                echo "  cp archivo.backup_tipo archivo_original"
                echo ""
                echo "Ej: cp core/engine.py.backup_gatekeeper core/engine.py"
            fi
            
            echo ""
            ;;
        exit)
            echo -e "\n${GREEN}Saliendo...${NC}\n"
            exit 0
            ;;
        *)
            echo -e "${RED}Opción no válida. Intenta nuevamente.${NC}\n"
            ;;
    esac
    
    echo ""
    read -p "Presiona Enter para continuar..."
    clear
    
    echo -e "${BLUE}"
    cat << 'BANNER'
╔════════════════════════════════════════════════════════════════════╗
║           FERDONAN v2.0 - INTERACTIVE FIX SUITE                    ║
╚════════════════════════════════════════════════════════════════════╝
BANNER
    echo -e "${NC}"
    echo ""
    
    for fix in "${FIXES[@]}"; do
        IFS='|' read -r num desc script <<< "$fix"
        printf "  %-2s) %-50s\n" "$num" "$desc"
    done
    
    echo ""
    echo -e "${YELLOW}Opciones especiales:${NC}"
    echo "  list)  Listar todos los fixes y sus detalles"
    echo "  info)  Información sobre cada fix"
    echo "  back)  Restaurar desde backups (rollback)"
    echo "  exit)  Salir"
    echo ""
done
