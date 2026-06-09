#!/usr/bin/env python
"""
Genera un archivo de texto plano con toda la estructura y contenido del proyecto,
excluyendo directorios y archivos no relevantes (venv, __pycache__, .git, logs, backups, etc.)
"""
import os
import sys
import argparse
import subprocess
from datetime import datetime
from pathlib import Path

def should_exclude(path, exclude_dirs, exclude_extensions):
    """Determina si un archivo o directorio debe ser excluido."""
    name = os.path.basename(path)
    if name in exclude_dirs:
        return True
    if os.path.isfile(path):
        ext = os.path.splitext(name)[1].lower()
        if ext in exclude_extensions:
            return True
    return False

def generate_tree(root_dir, exclude_dirs):
    """Genera estructura de árbol usando tree o fallback Python."""
    exclude_pattern = '|'.join(exclude_dirs)
    
    # Intentar usar tree primero
    try:
        result = subprocess.run(
            ['tree', '-a', '-I', exclude_pattern, root_dir],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            return result.stdout
    except (subprocess.SubprocessError, FileNotFoundError):
        pass
    
    # Fallback: generar árbol con Python
    lines = [root_dir]
    for root, dirs, files in os.walk(root_dir):
        # Filtrar directorios excluidos
        dirs[:] = [d for d in dirs if d not in exclude_dirs and not d.startswith('.')]
        
        level = root.replace(root_dir, '').count(os.sep)
        indent = '│   ' * level
        lines.append(f'{indent}├── {os.path.basename(root)}/')
        
        subindent = '│   ' * (level + 1)
        for f in sorted(files):
            # Excluir archivos temporales y binarios
            if not should_exclude(os.path.join(root, f), exclude_dirs, {'.pyc', '.pyo', '.so', '.dll', '.exe'}):
                lines.append(f'{subindent}├── {f}')
    
    return '\n'.join(lines)

def collect_files(root_dir, exclude_dirs, exclude_extensions):
    """Recorre el directorio y devuelve lista de archivos a incluir."""
    files = []
    for root, dirs, filenames in os.walk(root_dir):
        # Filtrar directorios excluidos (modificando dirs in-place)
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for filename in filenames:
            filepath = os.path.join(root, filename)
            if not should_exclude(filepath, exclude_dirs, exclude_extensions):
                files.append(filepath)
    return sorted(files)

def safe_read_file(filepath):
    """Lee un archivo de forma segura, manejando binarios y encoding."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        # Intentar con latin-1 como fallback
        try:
            with open(filepath, 'r', encoding='latin-1') as f:
                return f.read()
        except:
            return f"[ERROR: No se pudo leer el archivo (encoding problem)]"
    except Exception as e:
        return f"[ERROR: {str(e)}]"

def write_output(output_path, root_dir, files):
    """Escribe el contenido de todos los archivos en un solo txt."""
    with open(output_path, 'w', encoding='utf-8') as out:
        out.write(f"=== PROYECTO FERDONAN - ESTRUCTURA Y CONTENIDO ===\n")
        out.write(f"Generado el: {datetime.now().strftime('%a %d %b %Y %H:%M:%S %Z')}\n\n")
        
        # Escribir estructura de árbol
        out.write("=== ESTRUCTURA DE DIRECTORIOS ===\n")
        exclude_dirs = {'venv', '__pycache__', '.git', 'logs', 'backups', 'data', '.pytest_cache'}
        tree_output = generate_tree(root_dir, exclude_dirs)
        out.write(tree_output)
        out.write("\n\n=== CONTENIDO DE ARCHIVOS ===\n")
        
        for filepath in files:
            relpath = os.path.relpath(filepath, root_dir)
            out.write(f"\n===== FILE: {relpath} =====\n")
            content = safe_read_file(filepath)
            out.write(content)
            out.write("\n")
    
    print(f"✅ Exportación completada: {output_path}")
    print(f"📊 Archivos exportados: {len(files)}")

def main():
    parser = argparse.ArgumentParser(description='Exporta todo el proyecto a un solo archivo de texto.')
    parser.add_argument('-o', '--output', default='ferdonan_export.txt', help='Archivo de salida (por defecto: ferdonan_export.txt)')
    parser.add_argument('-d', '--dir', default='.', help='Directorio raíz del proyecto (por defecto: actual)')
    args = parser.parse_args()
    
    root_dir = os.path.abspath(args.dir)
    exclude_dirs = {
        '.git', '__pycache__', 'venv', '.venv', 'logs', 'backups', 'data', 
        '.pytest_cache', 'ferdonan.egg-info', '.env',  # Añadido .env por seguridad
        'cache', '.cache'
    }
    exclude_extensions = {
        '.pyc', '.pyo', '.so', '.dll', '.exe', '.zip', '.tar', '.gz', 
        '.jpg', '.png', '.gif', '.ico', '.mp3', '.wav', '.mp4',
        '.db', '.sqlite', '.sqlite3'  # Excluir bases de datos
    }
    
    files = collect_files(root_dir, exclude_dirs, exclude_extensions)
    write_output(args.output, root_dir, files)

if __name__ == "__main__":
    main()
