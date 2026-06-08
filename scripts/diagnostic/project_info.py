#!/usr/bin/env python3
"""
Muestra información detallada del proyecto: estructura, líneas de código, últimos cambios, etc.
"""
import os
import subprocess
from datetime import datetime
from pathlib import Path
from collections import Counter

def get_file_extension_counts(root_dir):
    counts = Counter()
    for root, dirs, files in os.walk(root_dir):
        # Excluir directorios
        dirs[:] = [d for d in dirs if d not in {'.git', 'venv', '__pycache__', 'logs', 'backups', 'data', '.pytest_cache'}]
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext:
                counts[ext] += 1
    return counts

def get_line_counts(root_dir):
    total_lines = 0
    py_lines = 0
    yaml_lines = 0
    md_lines = 0
    
    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d not in {'.git', 'venv', '__pycache__', 'logs', 'backups', 'data', '.pytest_cache'}]
        for file in files:
            path = os.path.join(root, file)
            if file.endswith('.py'):
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = len(f.readlines())
                    py_lines += lines
                    total_lines += lines
            elif file.endswith(('.yaml', '.yml')):
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = len(f.readlines())
                    yaml_lines += lines
                    total_lines += lines
            elif file.endswith('.md'):
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = len(f.readlines())
                    md_lines += lines
                    total_lines += lines
    
    return {
        'python': py_lines,
        'yaml': yaml_lines,
        'markdown': md_lines,
        'total': total_lines
    }

def get_last_modified(root_dir):
    latest = None
    latest_file = None
    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d not in {'.git', 'venv', '__pycache__', 'logs', 'backups', 'data'}]
        for file in files:
            path = os.path.join(root, file)
            mtime = os.path.getmtime(path)
            if latest is None or mtime > latest:
                latest = mtime
                latest_file = path
    return latest_file, datetime.fromtimestamp(latest) if latest else None

def git_status():
    try:
        result = subprocess.run(['git', 'status', '--short'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0 and result.stdout:
            lines = result.stdout.strip().split('\n')
            modified = [l for l in lines if l.startswith(' M') or l.startswith('M')]
            untracked = [l for l in lines if l.startswith('??')]
            return {'modified': len(modified), 'untracked': len(untracked)}
    except:
        pass
    return None

def main():
    root = Path(".")
    
    print("=" * 60)
    print("📊 INFORME DE PROYECTO FERDONAN")
    print("=" * 60)
    print(f"📁 Directorio: {root.absolute()}")
    print()
    
    # 1. Estructura de directorios (resumida)
    print("📂 ESTRUCTURA PRINCIPAL")
    for item in sorted(root.iterdir()):
        if item.is_dir() and item.name not in {'.git', 'venv', '__pycache__', 'logs', 'backups', 'data', '.pytest_cache'}:
            subdirs = len([x for x in item.iterdir() if x.is_dir() and x.name not in {'__pycache__', 'venv'}])
            files = len([x for x in item.iterdir() if x.is_file()])
            print(f"  📁 {item.name}/ ({subdirs} subdirs, {files} archivos)")
    print()
    
    # 2. Agentes disponibles
    agents_dir = root / "agents"
    if agents_dir.exists():
        agents = [d for d in agents_dir.iterdir() if d.is_dir()]
        print(f"🤖 AGENTES DISPONIBLES ({len(agents)})")
        for agent in sorted(agents):
            config = agent / "config.yaml"
            if config.exists():
                import yaml
                try:
                    with open(config, 'r') as f:
                        data = yaml.safe_load(f)
                        name = data.get('name', agent.name)
                        desc = data.get('description', '')[:60]
                        print(f"  • {name} (ID: {agent.name})")
                        if desc:
                            print(f"    📝 {desc}...")
                except:
                    print(f"  • {agent.name}")
    print()
    
    # 3. Estadísticas de código
    print("📈 ESTADÍSTICAS DE CÓDIGO")
    extensions = get_file_extension_counts(root)
    lines = get_line_counts(root)
    print(f"  📄 Archivos por extensión: {dict(extensions)}")
    print(f"  📝 Líneas de código:")
    print(f"     Python: {lines['python']:,}")
    print(f"     YAML:   {lines['yaml']:,}")
    print(f"     Markdown: {lines['markdown']:,}")
    print(f"     Total:  {lines['total']:,}")
    print()
    
    # 4. Últimos cambios
    last_file, last_date = get_last_modified(root)
    if last_file:
        print(f"🕒 ÚLTIMO CAMBIO")
        print(f"  Archivo: {last_file}")
        print(f"  Fecha:   {last_date}")
    print()
    
    # 5. Estado Git
    git = git_status()
    if git:
        print(f"🔧 GIT STATUS")
        print(f"  Modificados: {git['modified']}")
        print(f"  No trackeados: {git['untracked']}")
    else:
        print("🔧 Git: no disponible o no es un repositorio")
    print()
    
    # 6. Recomendaciones
    print("💡 RECOMENDACIONES")
    if git and git['untracked'] > 10:
        print("  • Considera añadir archivos no trackeados a .gitignore o hacer git add")
    if lines['python'] > 5000:
        print("  • El proyecto está creciendo; considera dividir módulos muy grandes")
    print("  • Ejecuta 'python scripts/diagnostic/clean_project.py' para limpiar temporales")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
