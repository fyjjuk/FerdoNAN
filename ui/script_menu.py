#!/usr/bin/env python3
"""
Menú dinámico de utilidades y scripts.
Escanea automáticamente scripts/user/ y scripts/diagnostic/
"""
import subprocess
import sys
import os
from pathlib import Path
from typing import List, Tuple

def discover_scripts() -> List[Tuple[str, str, str]]:
    """
    Descubre scripts en las carpetas de utilidades.
    Retorna lista de (nombre, comando, categoría)
    """
    scripts = []
    base_dir = Path(__file__).parent.parent
    
    # Scripts de usuario (user)
    user_dir = base_dir / "scripts" / "user"
    if user_dir.exists():
        for script in user_dir.glob("*.py"):
            # Obtener descripción de la primera línea del docstring
            description = _get_script_description(script)
            command = f"python {script}"
            scripts.append((script.stem.replace('_', ' ').title(), command, "user"))
    
    # Scripts de diagnóstico (diagnostic)
    diag_dir = base_dir / "scripts" / "diagnostic"
    if diag_dir.exists():
        for script in diag_dir.glob("*.py"):
            description = _get_script_description(script)
            command = f"python {script}"
            scripts.append((script.stem.replace('_', ' ').title(), command, "diagnostic"))
    
    # Scripts shell
    for script in user_dir.glob("*.sh"):
        description = _get_script_description(script, is_shell=True)
        command = f"bash {script}"
        scripts.append((script.stem.replace('_', ' ').title(), command, "shell"))
    
    # Ordenar por nombre
    scripts.sort(key=lambda x: x[0])
    return scripts

def _get_script_description(script_path: Path, is_shell: bool = False) -> str:
    """Extrae descripción del script desde su docstring o comentarios."""
    try:
        if is_shell:
            with open(script_path, 'r') as f:
                content = f.read()
                for line in content.split('\n')[:10]:
                    if line.startswith('#') and 'desc:' in line.lower():
                        return line.strip('#').strip()
                    elif line.startswith('#') and len(line) > 5:
                        return line.strip('#').strip()
                return script_path.stem.replace('_', ' ').title()
        else:
            with open(script_path, 'r') as f:
                content = f.read()
                # Buscar docstring
                import ast
                try:
                    tree = ast.parse(content)
                    docstring = ast.get_docstring(tree)
                    if docstring:
                        first_line = docstring.split('\n')[0]
                        if len(first_line) > 60:
                            return first_line[:57] + "..."
                        return first_line
                except:
                    pass
    except:
        pass
    return script_path.stem.replace('_', ' ').title()

def run_script(command: str, description: str):
    """Ejecuta un comando y muestra la salida."""
    print(f"\n⏳ Ejecutando: {description}")
    print(f"   Comando: {command}\n")
    print("─" * 60)
    try:
        result = subprocess.run(command, shell=True, text=True)
        if result.returncode != 0:
            print(f"\n⚠️ El script terminó con código {result.returncode}")
    except KeyboardInterrupt:
        print("\n⏹️ Ejecución interrumpida por el usuario")
    except Exception as e:
        print(f"\n❌ Error al ejecutar: {e}")
    print("─" * 60)
    input("\nPresiona Enter para continuar...")

def show_menu():
    """Muestra el menú dinámico y maneja la selección."""
    # Descubrir scripts
    scripts = discover_scripts()
    
    if not scripts:
        print("\n❌ No se encontraron scripts en scripts/user/ o scripts/diagnostic/")
        return
    
    while True:
        print("\n" + "="*60)
        print("🛠️  MENÚ DE UTILIDADES FERDONAN (Dinámico)")
        print("="*60)
        
        # Mostrar scripts por categoría
        current_category = None
        for idx, (name, command, category) in enumerate(scripts, start=1):
            # Mostrar separador de categoría
            category_names = {"user": "👤 Utilidades", "diagnostic": "🔍 Diagnóstico", "shell": "🐚 Shell"}
            if category != current_category:
                current_category = category
                print(f"\n  ┌─ {category_names.get(category, '📦 Otros')} ─")
            
            print(f"  │ {idx:2}. {name}")
        
        print("\n  └─" + "─"*40)
        print("  0. Volver al selector de agentes")
        print("="*60)
        
        choice = input("\n👉 Elige una opción: ").strip()
        
        if choice == "0":
            break
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(scripts):
                name, command, category = scripts[idx]
                run_script(command, name)
            else:
                print("❌ Opción inválida")
        except ValueError:
            print("❌ Entrada inválida. Ingresa un número o 0 para salir.")

def run():
    """Punto de entrada del menú."""
    show_menu()


if __name__ == "__main__":
    run()
