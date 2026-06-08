#!/usr/bin/env python3
"""
Limpia el proyecto de archivos temporales, backups y cachés innecesarios.
Ejecutar con precaución: revisa la lista de archivos a eliminar antes de proceder.
"""
import os
import shutil
from pathlib import Path

def get_size(path):
    total = 0
    if os.path.isfile(path):
        return os.path.getsize(path)
    elif os.path.isdir(path):
        for root, dirs, files in os.walk(path):
            for f in files:
                fp = os.path.join(root, f)
                if os.path.exists(fp):
                    total += os.path.getsize(fp)
    return total

def human_size(size):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"

def main():
    root = Path(".")
    patterns = [
        "*.bak", "*.bak_*", "*.clean_backup", "*.dirty",
        "*.pyc", "__pycache__",
        ".pytest_cache",
        "logs/*.log", "logs/*.log.*",
        "cache/*.json",
        "data/rag_storage/chroma.sqlite3",
        "data/*.json",
        "ferdonan_export.txt",
        "exportacion_completa.txt",
    ]
    
    to_delete = []
    total_size = 0
    
    print("🔍 Buscando archivos temporales y backups...\n")
    
    for pattern in patterns:
        for path in root.glob(f"**/{pattern}"):
            if path.exists():
                size = get_size(path)
                total_size += size
                to_delete.append((path, size))
                print(f"  📄 {path} ({human_size(size)})")
    
    if not to_delete:
        print("✅ No se encontraron archivos temporales.")
        return
    
    print(f"\n📦 Total a liberar: {human_size(total_size)}")
    print("\n⚠️  ¿Eliminar estos archivos? (s/N): ", end="")
    confirm = input().strip().lower()
    
    if confirm == 's':
        for path, _ in to_delete:
            if path.is_file():
                path.unlink()
            elif path.is_dir():
                shutil.rmtree(path)
        print("✅ Limpieza completada.")
    else:
        print("❌ Operación cancelada.")

if __name__ == "__main__":
    main()
