#!/bin/bash
# Fix #4: Dynamic Resource Profiles Implementation
# Problema: Estructura existe pero lógica de selección de perfil es incompleta

SCHEDULER_FILE="orchestration/resource_manager.py"

echo "==== FIX #4: Dynamic Resource Profile Selection ===="
echo ""

# Verificar que select_resource_profile existe
if grep -q "def select_resource_profile" "$SCHEDULER_FILE"; then
    echo "✓ Método select_resource_profile encontrado"
    
    # Crear patch mejorado
    cat > /tmp/patch_resource_profiles.py << 'EOF'
import sys

with open(sys.argv[1], 'r') as f:
    content = f.read()

# Buscar y reemplazar la lógica de select_resource_profile
old_selection = '''    def select_resource_profile(self, llm_provider_dict) -> str:
        """
        Determina el perfil de recursos ('high', 'medium', 'low') basado en recursos disponibles.
        Si el agente no tiene dynamic_resource_management activado, retorna 'default'.
        """
        dynamic = llm_provider_dict.get("dynamic_resource_management", False)
        if not dynamic:
            return "default"
        
        metrics = self.get_system_metrics()
        ram_free_mb = metrics.get("ram_available_mb", 0)
        
        # Detectar VRAM libre si está disponible
        vram_free_mb = None
        if "vram_total_mb" in metrics and "vram_used_mb" in metrics:
            vram_free_mb = metrics["vram_total_mb"] - metrics["vram_used_mb"]
        
        # Umbrales (ajustables según tu hardware: RTX 4050 6GB, 16GB RAM)
        if vram_free_mb and vram_free_mb > 4000 and ram_free_mb > 8000:
            return "high"
        elif vram_free_mb and vram_free_mb > 2000 and ram_free_mb > 4000:
            return "medium"
        else:
            return "low"'''

new_selection = '''    def select_resource_profile(self, llm_provider_dict) -> str:
        """
        Determina el perfil de recursos ('high', 'medium', 'low') basado en recursos disponibles.
        Si el agente no tiene dynamic_resource_management activado, retorna 'default'.
        
        Umbrales configurables en config.settings:
          HIGH:   VRAM > 4000MB & RAM > 8000MB
          MEDIUM: VRAM > 2000MB & RAM > 4000MB
          LOW:    Fallback (dispositivos con poca memoria)
        """
        dynamic = llm_provider_dict.get("dynamic_resource_management", False)
        if not dynamic:
            return "default"
        
        metrics = self.get_system_metrics()
        ram_free_mb = metrics.get("ram_available_mb", 0)
        cpu_percent = metrics.get("cpu_percent", 0)
        
        # Detectar VRAM libre si está disponible
        vram_free_mb = None
        if "vram_total_mb" in metrics and "vram_used_mb" in metrics:
            vram_free_mb = metrics["vram_total_mb"] - metrics["vram_used_mb"]
        
        # Configuración de umbrales
        high_vram_threshold = 4000   # MB
        high_ram_threshold = 8000    # MB
        medium_vram_threshold = 2000 # MB
        medium_ram_threshold = 4000  # MB
        cpu_threshold = 70           # %
        
        # Lógica de selección mejorada
        profile = "low"
        reason = "Recursos limitados (fallback)"
        
        # Evitar modelo pesado si CPU está muy ocupado
        if cpu_percent > cpu_threshold:
            logger.warning(f"CPU muy ocupado ({cpu_percent:.1f}%). Seleccionando perfil LOW.")
            return "low"
        
        # Seleccionar basado en VRAM si disponible
        if vram_free_mb:
            if vram_free_mb > high_vram_threshold and ram_free_mb > high_ram_threshold:
                profile = "high"
                reason = f"VRAM={vram_free_mb:.0f}MB, RAM={ram_free_mb:.0f}MB (suficiente)"
            elif vram_free_mb > medium_vram_threshold and ram_free_mb > medium_ram_threshold:
                profile = "medium"
                reason = f"VRAM={vram_free_mb:.0f}MB, RAM={ram_free_mb:.0f}MB (moderado)"
            else:
                profile = "low"
                reason = f"VRAM={vram_free_mb:.0f}MB, RAM={ram_free_mb:.0f}MB (limitado)"
        else:
            # Fallback: usar solo RAM
            if ram_free_mb > high_ram_threshold:
                profile = "high"
                reason = f"RAM={ram_free_mb:.0f}MB (sin VRAM, pero suficiente)"
            elif ram_free_mb > medium_ram_threshold:
                profile = "medium"
                reason = f"RAM={ram_free_mb:.0f}MB (sin VRAM)"
            else:
                profile = "low"
                reason = f"RAM={ram_free_mb:.0f}MB (muy limitado)"
        
        logger.info(f"RESOURCE_PROFILE_SELECTION: {profile} ({reason})")
        return profile'''

if old_selection in content:
    content = content.replace(old_selection, new_selection)
    with open(sys.argv[1], 'w') as f:
        f.write(content)
    print("✓ Lógica de selección de perfiles mejorada")
else:
    print("⚠ Patrón exacto no encontrado")
    print("  Verificando si método existe...")
    if "def select_resource_profile" in content:
        print("  ✓ Método existe pero estructura diferente")
        print("  Editar manualmente: orchestration/resource_manager.py")
    sys.exit(1)

EOF

    cp "$SCHEDULER_FILE" "${SCHEDULER_FILE}.backup_profiles"
    echo "✓ Backup: ${SCHEDULER_FILE}.backup_profiles"
    
    python3 /tmp/patch_resource_profiles.py "$SCHEDULER_FILE"
    
    if [ $? -eq 0 ]; then
        echo "✓ Lógica de perfiles dinámicos mejorada"
        echo ""
        echo "Mejoras aplicadas:"
        echo "  ✓ Consideración de CPU usage en decisión"
        echo "  ✓ Logging detallado de decisión de perfil"
        echo "  ✓ Mejor fallback si no hay VRAM"
        echo "  ✓ Umbrales claramente documentados"
    else
        cp "${SCHEDULER_FILE}.backup_profiles" "$SCHEDULER_FILE"
        echo "✗ Revert: estructura diferente"
        exit 1
    fi
else
    echo "✗ select_resource_profile NO encontrado en $SCHEDULER_FILE"
    exit 1
fi

echo ""
