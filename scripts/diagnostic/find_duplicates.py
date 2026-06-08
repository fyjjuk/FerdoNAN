#!/usr/bin/env python
import os
import hashlib
from collections import defaultdict

def hash_file(path):
    hasher = hashlib.md5()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hasher.update(chunk)
    return hasher.hexdigest()

def find_duplicates(root_dir='.'):
    exclude_dirs = {'.git', '__pycache__', 'venv', '.venv', 'logs', 'backups'}
    hashes = defaultdict(list)
    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            if file.endswith('.py') or file.endswith('.yaml') or file.endswith('.json'):
                path = os.path.join(root, file)
                # Ignorar archivos vacíos (tamaño 0)
                if os.path.getsize(path) == 0:
                    continue
                try:
                    file_hash = hash_file(path)
                    hashes[file_hash].append(path)
                except:
                    pass
    duplicates = {h: paths for h, paths in hashes.items() if len(paths) > 1}
    if duplicates:
        print("⚠️ Archivos duplicados encontrados:")
        for h, paths in duplicates.items():
            print(f"\n  Hash {h[:8]}...")
            for p in paths:
                print(f"    - {p}")
    else:
        print("✅ No se encontraron archivos duplicados (ignorando vacíos).")
    return duplicates

if __name__ == "__main__":
    find_duplicates()
