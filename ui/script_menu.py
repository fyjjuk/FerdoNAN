#!/usr/bin/env python3
"""
Menú dinámico de utilidades y scripts.
Incluye comandos del CLI (scripts/cli.py) y scripts tradicionales.
"""
import subprocess
import sys
import os
from pathlib import Path
from typing import List, Tuple

BASE_DIR = Path(__file__).parent.parent
CLI_CMD = f"python {BASE_DIR / 'scripts/cli.py'}"

def discover_scripts() -> List[Tuple[str, str, str]]:
    """
    Descubre scripts y comandos.
    Retorna lista de (nombre, comando, categoría)
    """
    scripts = []
    base_dir = BASE_DIR
    
    # Scripts de usuario (user)
    user_dir = base_dir / "scripts" / "user"
    if user_dir.exists():
        for script in user_dir.glob("*.py"):
            # Excluir cli.py porque lo manejamos aparte
            if script.name == "cli.py":
                continue
            description = _get_script_description(script)
            command = f"python {script}"
            scripts.append((description, command, "user"))
    
    # Scripts de diagnóstico (diagnostic)
    diag_dir = base_dir / "scripts" / "diagnostic"
    if diag_dir.exists():
        for script in diag_dir.glob("*.py"):
            description = _get_script_description(script)
            command = f"python {script}"
            scripts.append((description, command, "diagnostic"))
    
    # Scripts shell
    for script in user_dir.glob("*.sh"):
        description = _get_script_description(script, is_shell=True)
        command = f"bash {script}"
        scripts.append((description, command, "shell"))
    
    # --- Comandos del CLI (usando python scripts/cli.py) ---
    cli_commands = [
        ("🔧 Validar rutas YAML", f"{CLI_CMD} validate-routes", "cli"),
        ("📊 Health check", f"{CLI_CMD} health", "cli"),
        ("💾 Backup del proyecto", f"{CLI_CMD} backup", "cli"),
        ("📜 Ver logs", f"{CLI_CMD} logs", "cli"),
        ("📁 Exportar proyecto (V2)", f"{CLI_CMD} export", "cli"),
        ("🧹 Limpiar temporales", f"{CLI_CMD} clean", "cli"),
        ("ℹ️ Info del proyecto", f"{CLI_CMD} info", "cli"),
        ("🔍 Buscar duplicados", f"{CLI_CMD} duplicates", "cli"),
        ("📊 Cobertura de tests", f"{CLI_CMD} test-all", "cli"),
        ("🔒 Tests de seguridad", f"{CLI_CMD} test-security", "cli"),
    ]
    for name, cmd, cat in cli_commands:
        scripts.append((name, cmd, cat))
    
    # --- Comandos Repomix ---
    repomix_commands = [
        ("📦 Repomix Pack (Markdown + compresión)", f"{CLI_CMD} repomix-config", "repomix"),
        ("📊 Repomix Estadísticas (tokens)", f"{CLI_CMD} repomix-stats", "repomix"),
        ("🌐 Repomix Remote (GitHub)", f"{CLI_CMD} repomix-remote", "repomix"),
        ("📄 Repomix Básico (XML)", f"{CLI_CMD} repomix", "repomix"),
    ]
    for name, cmd, cat in repomix_commands:
        scripts.append((name, cmd, cat))
    
    # Ordenar por nombre
    scripts.sort(key=lambda x: x[0])
    return scripts

def _get_script_description(script_path: Path, is_shell: bool = False) -> str:
    """Extrae descripción del script."""
    try:
        if is_shell:
            with open(script_path, 'r') as f:
                content = f.read()
                for line in content.split('\n')[:10]:
                    if line.startswith('#') and len(line) > 5 and 'Uso' not in line and 'bin' not in line:
                        return line.strip('#').strip()
                return script_path.stem.replace('_', ' ').title()
        else:
            with open(script_path, 'r') as f:
                content = f.read()
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
        result = subprocess.run(command, shell=True, text=True, cwd=BASE_DIR)
        if result.returncode != 0:
            print(f"\n⚠️ El comando terminó con código {result.returncode}")
    except KeyboardInterrupt:
        print("\n⏹️ Ejecución interrumpida por el usuario")
    except Exception as e:
        print(f"\n❌ Error al ejecutar: {e}")
    print("─" * 60)
    input("\nPresiona Enter para continuar...")

def show_menu():
    """Muestra el menú dinámico y maneja la selección."""
    scripts = discover_scripts()
    
    if not scripts:
        print("\n❌ No se encontraron utilidades.")
        return
    
    while True:
        print("\n" + "="*60)
        print("🛠️  MENÚ DE UTILIDADES FERDONAN")
        print("="*60)
        
        current_category = None
        category_names = {
            "user": "👤 Scripts de Usuario",
            "diagnostic": "🔍 Diagnóstico", 
            "shell": "🐚 Scripts Shell",
            "cli": "⚙️ Comandos CLI",
            "repomix": "📦 Repomix (IA Export)"
        }
        
        for idx, (name, command, category) in enumerate(scripts, start=1):
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
    show_menu()

if __name__ == "__main__":
    run()
