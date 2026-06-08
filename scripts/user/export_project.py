#!/usr/bin/env python
"""
Genera un archivo de texto plano con toda la estructura y contenido del proyecto,
excluyendo directorios y archivos no relevantes (venv, __pycache__, .git, logs, backups, etc.)
"""
import os
import sys
import argparse
from datetime import datetime

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

def write_output(output_path, root_dir, files):
    """Escribe el contenido de todos los archivos en un solo txt."""
    with open(output_path, 'w', encoding='utf-8') as out:
        out.write(f"=== PROYECTO FERDONAN - ESTRUCTURA Y CONTENIDO ===\n")
        out.write(f"Generado el: {datetime.now().strftime('%a %d %b %Y %H:%M:%S %Z')}\n\n")
        
        # Escribir estructura de árbol (usando tree si está disponible, sino simple)
        out.write("=== ESTRUCTURA DE DIRECTORIOS ===\n")
        os.system(f"tree -a -I 'venv|__pycache__|*.pyc|logs|backups|data|.git' {root_dir} >> {output_path} 2>/dev/null")
        out.write("\n\n=== CONTENIDO DE ARCHIVOS ===\n")
        
        for filepath in files:
            relpath = os.path.relpath(filepath, root_dir)
            out.write(f"\n===== FILE: {relpath} =====\n")
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    out.write(f.read())
            except Exception as e:
                out.write(f"Error leyendo archivo: {e}\n")
            out.write("\n")
    
    print(f"✅ Exportación completada: {output_path}")

def main():
    parser = argparse.ArgumentParser(description='Exporta todo el proyecto a un solo archivo de texto.')
    parser.add_argument('-o', '--output', default='ferdonan_export.txt', help='Archivo de salida (por defecto: ferdonan_export.txt)')
    parser.add_argument('-d', '--dir', default='.', help='Directorio raíz del proyecto (por defecto: actual)')
    args = parser.parse_args()
    
    root_dir = os.path.abspath(args.dir)
    exclude_dirs = {'.git', '__pycache__', 'venv', '.venv', 'logs', 'backups', 'data', '.pytest_cache', 'ferdonan.egg-info'}
    exclude_extensions = {'.pyc', '.pyo', '.so', '.dll', '.exe', '.zip', '.tar', '.gz', '.jpg', '.png', '.gif', '.ico', '.mp3', '.wav', '.mp4'}
    
    files = collect_files(root_dir, exclude_dirs, exclude_extensions)
    write_output(args.output, root_dir, files)

if __name__ == "__main__":
    main()
