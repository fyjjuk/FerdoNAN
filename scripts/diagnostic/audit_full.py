#!/usr/bin/env python3
"""
Analiza el proyecto y clasifica archivos por tipo y utilidad.
Identifica archivos innecesarios (backups, logs, cachés, binarios, etc.)
"""
import os
from pathlib import Path
from collections import defaultdict

# Extensiones de archivos según su utilidad
CATEGORIES = {
    'source': {'.py', '.yaml', '.yml', '.md', '.txt', '.json', '.sh', '.bash'},
    'binary': {'.xlsx', '.docx', '.pdf', '.jpg', '.png', '.gif', '.ico'},
    'backup': {'.bak', '.backup', '.old', '.orig', '.swp', '.swo'},
    'temp': {'.tmp', '.log', '.pyc', '.cache'},
    'config': {'.yaml', '.yml', '.json', '.conf', '.cfg', '.ini'},
    'db': {'.sqlite', '.sqlite3', '.db'},
    'executable': {'.exe', '.dll', '.so', '.dylib'},
    'archive': {'.zip', '.tar', '.gz', '.rar', '.7z'},
    'media': {'.mp3', '.wav', '.mp4', '.avi', '.mov'},
    'other': set()
}

def get_file_info(path):
    """Devuelve información del archivo: tamaño, tipo, categoría"""
    stat = path.stat()
    size = stat.st_size
    ext = path.suffix.lower()
    category = 'other'
    for cat, exts in CATEGORIES.items():
        if ext in exts:
            category = cat
            break
    return {
        'name': path.name,
        'path': str(path),
        'size': size,
        'ext': ext,
        'category': category,
        'mtime': stat.st_mtime
    }

def main():
    root = Path('.')
    results = defaultdict(list)
    total_size = 0
    file_count = 0
    
    print("=" * 70)
    print("📊 ANÁLISIS COMPLETO DE ARCHIVOS - FERDONAN")
    print("=" * 70)
    
    for path in root.rglob('*'):
        if path.is_file():
            # Excluir directorios del sistema y venv
            if 'venv' in str(path) or '__pycache__' in str(path) or '.git' in str(path):
                continue
            
            info = get_file_info(path)
            results[info['category']].append(info)
            total_size += info['size']
            file_count += 1
    
    # Mostrar por categoría
    print("\n📁 CLASIFICACIÓN DE ARCHIVOS\n")
    
    for cat in ['source', 'config', 'binary', 'backup', 'temp', 'db', 'executable', 'archive', 'media', 'other']:
        files = results.get(cat, [])
        if files:
            size_mb = sum(f['size'] for f in files) / (1024 * 1024)
            print(f"\n{'='*40}")
            print(f"📂 {cat.upper()} ({len(files)} archivos, {size_mb:.2f} MB)")
            print(f"{'='*40}")
            for f in sorted(files, key=lambda x: x['size'], reverse=True)[:10]:  # Top 10 más grandes
                if f['size'] < 1024*1024:
                    print(f"  📄 {f['name']} ({f['size']/1024:.1f} KB)")
                else:
                    print(f"  📄 {f['name']} ({f['size']/(1024*1024):.2f} MB)")
            if len(files) > 10:
                print(f"  ... y {len(files)-10} archivos más")
    
    # Resumen final
    print("\n" + "=" * 70)
    print("📊 RESUMEN GENERAL")
    print("=" * 70)
    print(f"📄 Total archivos analizados: {file_count}")
    print(f"💾 Espacio total: {total_size/(1024*1024):.2f} MB")
    
    # Recomendaciones
    print("\n💡 RECOMENDACIONES")
    if results.get('backup'):
        print("  • Elimina archivos de backup (*.bak, *.old) - No son necesarios en el código fuente")
    if results.get('temp'):
        print("  • Limpia archivos temporales (*.tmp, *.log) y cachés (*.pyc)")
    if results.get('binary'):
        print("  • Revisa archivos binarios (*.xlsx, *.docx). Si no son esenciales, muévelos a otro directorio")
    if results.get('db'):
        print("  • Las bases de datos locales (*.sqlite) pueden regenerarse, no es necesario trackearlas")
    if results.get('media'):
        print("  • Archivos multimedia grandes pueden externalizarse")

if __name__ == "__main__":
    main()
