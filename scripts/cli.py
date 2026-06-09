#!/usr/bin/env python3
"""CLI unificado para FerdoNAN - Agrupa utilidades y scripts."""

import click
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent

def run_script(script_path, *args):
    """Ejecuta un script de Python y maneja la salida."""
    cmd = [sys.executable, str(script_path)] + list(args)
    return subprocess.run(cmd)

@click.group()
def cli():
    """FerdoNAN Toolbelt – comandos unificados."""
    pass

# ------------------------------------------------------------
# Utilidades de usuario (scripts/user/)
# ------------------------------------------------------------
@cli.command()
def backup():
    """Crear backup del proyecto."""
    script = PROJECT_ROOT / "scripts/user/backup_cli.py"
    if script.exists():
        run_script(script, "crear")
    else:
        click.echo("❌ backup_cli.py no encontrado")

@cli.command()
def logs():
    """Ver logs en tiempo real (tail)."""
    script = PROJECT_ROOT / "scripts/user/logs_tail.py"
    if script.exists():
        run_script(script)
    else:
        click.echo("❌ logs_tail.py no encontrado")

@cli.command()
@click.argument('route_name')
@click.argument('agent_id')
def copy_route(route_name, agent_id):
    """Copiar una ruta desde docs/route_templates a un agente."""
    script = PROJECT_ROOT / "scripts/user/copy_route.sh"
    if script.exists():
        subprocess.run(["bash", str(script), route_name, agent_id])
    else:
        click.echo("❌ copy_route.sh no encontrado")

@cli.command()
def export():
    """Exportar proyecto completo (usando export_project_v2.py)."""
    script = PROJECT_ROOT / "scripts/user/export_project_v2.py"
    if script.exists():
        run_script(script)
    else:
        click.echo("❌ export_project_v2.py no encontrado")

# ------------------------------------------------------------
# Scripts de diagnóstico (scripts/diagnostic/)
# ------------------------------------------------------------
@cli.command()
def health():
    """Health check (Ollama, ChromaDB, disco)."""
    script = PROJECT_ROOT / "scripts/diagnostic/check_health.py"
    if script.exists():
        run_script(script)
    else:
        click.echo("❌ check_health.py no encontrado")

@cli.command()
def duplicates():
    """Buscar archivos duplicados."""
    script = PROJECT_ROOT / "scripts/diagnostic/find_duplicates.py"
    if script.exists():
        run_script(script)
    else:
        click.echo("❌ find_duplicates.py no encontrado")

@cli.command()
def clean():
    """Limpiar archivos temporales y backups."""
    script = PROJECT_ROOT / "scripts/diagnostic/clean_project.py"
    if script.exists():
        run_script(script)
    else:
        click.echo("❌ clean_project.py no encontrado")

@cli.command()
def info():
    """Mostrar información detallada del proyecto."""
    script = PROJECT_ROOT / "scripts/diagnostic/project_info.py"
    if script.exists():
        run_script(script)
    else:
        click.echo("❌ project_info.py no encontrado")

@cli.command()
def validate_routes():
    """Validar todas las rutas YAML de los agentes."""
    script = PROJECT_ROOT / "scripts/diagnostic/validate_routes.py"
    if script.exists():
        run_script(script)
    else:
        click.echo("❌ validate_routes.py no encontrado")

@cli.command()
def audit():
    """Auditoría completa de archivos (clasificación por tipo)."""
    script = PROJECT_ROOT / "scripts/diagnostic/audit_full.py"
    if script.exists():
        run_script(script)
    else:
        click.echo("❌ audit_full.py no encontrado")

# ------------------------------------------------------------
# Comandos adicionales útiles
# ------------------------------------------------------------
@cli.command()
def test():
    """Ejecutar tests unitarios con pytest."""
    result = subprocess.run(["pytest", "tests/", "-v"])
    sys.exit(result.returncode)

@cli.command()
def dashboard():
    """Iniciar el dashboard web (puerto 8000)."""
    subprocess.run([sys.executable, "web/dashboard.py"])

@cli.command()
def run():
    """Ejecutar el asistente principal (main.py)."""
    subprocess.run([sys.executable, "main.py"])

@cli.command()
def test_security():
    """Ejecutar tests de estrés de firewalls."""
    subprocess.run(["pytest", "tests/test_firewall_stress.py", "-v"])


if __name__ == "__main__":
    cli()
