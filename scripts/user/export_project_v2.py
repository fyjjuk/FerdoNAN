#!/usr/bin/env python
"""
Exportador mejorado de FERDONAN: estructura, contenido y estadísticas.
Genera un índice navegable y prioriza contenido crítico.
"""
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
import argparse

class ProjectExporter:
    def __init__(self, root_dir: str = '.', output_file: str = 'ferdonan_export.txt'):
        self.root_dir = Path(root_dir).resolve()
        self.output_file = output_file
        self.files_by_category = {
            'config': [],
            'core': [],
            'security': [],
            'services': [],
            'tests': [],
            'tools': [],
            'docs': [],
            'other': []
        }
        self.file_stats = {}
        
    def should_exclude(self, path: Path) -> bool:
        """Determina si un archivo debe ser excluido."""
        exclude_dirs = {
            '.git', '__pycache__', 'venv', '.venv', 'logs', 'backups', 
            '.pytest_cache', 'ferdonan.egg-info', '.env', 'cache', '.cache',
            'node_modules', 'dist', 'build', '.next', '__pycache__'
        }
        
        exclude_extensions = {
            '.pyc', '.pyo', '.so', '.dll', '.exe', '.zip', '.tar', '.gz',
            '.jpg', '.jpeg', '.png', '.gif', '.ico', '.mp3', '.wav', '.mp4',
            '.db', '.sqlite', '.sqlite3', '.tar.gz', '.whl'
        }
        
        # Excluir si está en directorio excluido
        if any(excluded in path.parts for excluded in exclude_dirs):
            return True
        
        # Excluir extensiones
        if path.suffix.lower() in exclude_extensions:
            return True
        
        # Excluir archivos temporales
        if path.name.startswith('.') and path.name not in {'.gitignore', '.env.example'}:
            return True
            
        if path.name.endswith(('.bak', '.backup', '.old', '.orig', '.swp', '.swo')):
            return True
        
        return False
    
    def categorize_file(self, filepath: Path):
        """Categoriza archivo por importancia y tipo."""
        rel_path = filepath.relative_to(self.root_dir)
        parts = rel_path.parts
        
        # Prioridad por patrón
        priority_map = {
            ('config',): 'config',
            ('core',): 'core',
            ('security',): 'security',
            ('services',): 'services',
            ('tests',): 'tests',
            ('tools',): 'tools',
            ('README.md',): 'docs',
            ('LICENSE',): 'docs',
            ('.gitignore',): 'docs',
        }
        
        for pattern, category in priority_map.items():
            if len(parts) > 0 and parts[0] in pattern or rel_path.name in pattern:
                return category
        
        return 'other'
    
    def collect_files(self) -> Dict[str, List[Path]]:
        """Recopila archivos organizados por categoría."""
        for filepath in self.root_dir.rglob('*'):
            if filepath.is_file() and not self.should_exclude(filepath):
                category = self.categorize_file(filepath)
                self.files_by_category[category].append(filepath)
                self.file_stats[filepath] = {
                    'size': filepath.stat().st_size,
                    'lines': self._count_lines(filepath)
                }
        
        # Ordenar dentro de cada categoría
        for category in self.files_by_category:
            self.files_by_category[category].sort(key=lambda x: x.name)
        
        return self.files_by_category
    
    def _count_lines(self, filepath: Path) -> int:
        """Cuenta líneas de un archivo."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return len(f.readlines())
        except:
            return 0
    
    def safe_read_file(self, filepath: Path) -> str:
        """Lee archivo de forma segura."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            try:
                with open(filepath, 'r', encoding='latin-1') as f:
                    return f.read()
            except:
                return "[ERROR: No se pudo leer (encoding)]"
        except Exception as e:
            return f"[ERROR: {str(e)}]"
    
    def generate_tree(self, max_depth: int = 3) -> str:
        """Genera árbol visual del proyecto."""
        lines = [f"📦 {self.root_dir.name}/"]
        
        def add_tree(path: Path, prefix: str = "", depth: int = 0):
            if depth > max_depth:
                return
            
            try:
                items = sorted([p for p in path.iterdir() if not self.should_exclude(p)])
            except PermissionError:
                return
            
            dirs = [p for p in items if p.is_dir()]
            files = [p for p in items if p.is_file()]
            
            # Mostrar directorios primero
            for i, d in enumerate(dirs):
                is_last = (i == len(dirs) - 1) and len(files) == 0
                connector = "└── " if is_last else "├── "
                lines.append(f"{prefix}{connector}📁 {d.name}/")
                
                next_prefix = prefix + ("    " if is_last else "│   ")
                add_tree(d, next_prefix, depth + 1)
            
            # Luego archivos
            for i, f in enumerate(files):
                is_last = i == len(files) - 1
                connector = "└── " if is_last else "├── "
                icon = self._get_file_icon(f.suffix)
                lines.append(f"{prefix}{connector}{icon} {f.name}")
        
        add_tree(self.root_dir)
        return "\n".join(lines)
    
    def _get_file_icon(self, extension: str) -> str:
        """Retorna icono según extensión."""
        icons = {
            '.py': '🐍',
            '.yaml': '⚙️',
            '.yml': '⚙️',
            '.md': '📄',
            '.txt': '📝',
            '.json': '📋',
            '.sh': '🔧',
            '.gitignore': '🚫',
        }
        return icons.get(extension.lower(), '📄')
    
    def generate_index(self) -> str:
        """Genera índice de contenidos."""
        lines = ["📑 ÍNDICE DE CONTENIDOS\n"]
        
        for category, files in self.files_by_category.items():
            if not files:
                continue
            
            lines.append(f"\n{'='*60}")
            lines.append(f"📂 {category.upper()}")
            lines.append(f"{'='*60}")
            
            for filepath in files:
                rel_path = filepath.relative_to(self.root_dir)
                stats = self.file_stats.get(filepath, {})
                size_kb = stats.get('size', 0) / 1024
                lines_count = stats.get('lines', 0)
                lines.append(f"  • {rel_path} ({size_kb:.1f}KB, {lines_count} lines)")
        
        return "\n".join(lines)
    
    def generate_statistics(self) -> str:
        """Genera estadísticas del proyecto."""
        total_files = sum(len(files) for files in self.files_by_category.values())
        total_size = sum(stats['size'] for stats in self.file_stats.values())
        total_lines = sum(stats['lines'] for stats in self.file_stats.values())
        
        stats_by_category = {}
        for category, files in self.files_by_category.items():
            if files:
                cat_size = sum(self.file_stats[f]['size'] for f in files)
                cat_lines = sum(self.file_stats[f]['lines'] for f in files)
                stats_by_category[category] = {
                    'files': len(files),
                    'size': cat_size,
                    'lines': cat_lines
                }
        
        lines = [
            "\n📊 ESTADÍSTICAS DEL PROYECTO",
            "=" * 60,
            f"\n🔢 Resumen General:",
            f"  • Archivos totales: {total_files}",
            f"  • Tamaño total: {total_size / 1024 / 1024:.2f} MB",
            f"  • Líneas de código: {total_lines:,}",
            f"\n📈 Por Categoría:",
        ]
        
        for category, stats in sorted(stats_by_category.items(), key=lambda x: x[1]['lines'], reverse=True):
            lines.append(
                f"  • {category:12} : {stats['files']:2} files | "
                f"{stats['size']/1024:7.1f}KB | {stats['lines']:,} lines"
            )
        
        return "\n".join(lines)
    
    def export(self):
        """Exporta proyecto completo a archivo."""
        print("🔍 Reccopilando archivos...")
        self.collect_files()
        
        print("✍️  Generando exportación...")
        with open(self.output_file, 'w', encoding='utf-8') as out:
            # Header
            out.write("╔" + "="*78 + "╗\n")
            out.write(f"║ {'FERDONAN - PROJECT EXPORT':^76} ║\n")
            out.write(f"║ Generated: {datetime.now().strftime('%a %d %b %Y %H:%M:%S'):^65} ║\n")
            out.write("╚" + "="*78 + "╝\n\n")
            
            # Árbol visual
            out.write("📦 PROJECT STRUCTURE\n")
            out.write("=" * 60 + "\n")
            out.write(self.generate_tree())
            out.write("\n\n")
            
            # Índice
            out.write(self.generate_index())
            out.write("\n\n")
            
            # Estadísticas
            out.write(self.generate_statistics())
            out.write("\n\n")
            
            # Contenido de archivos por categoría
            out.write("╔" + "="*78 + "╗\n")
            out.write(f"║ {'FILE CONTENTS':^76} ║\n")
            out.write("╚" + "="*78 + "╝\n\n")
            
            for category, files in self.files_by_category.items():
                if not files:
                    continue
                
                out.write(f"\n{'━'*80}\n")
                out.write(f"📂 {category.upper()}\n")
                out.write(f"{'━'*80}\n\n")
                
                for filepath in files:
                    rel_path = filepath.relative_to(self.root_dir)
                    stats = self.file_stats.get(filepath, {})
                    
                    out.write(f"\n{'─'*80}\n")
                    out.write(f"📄 {rel_path}\n")
                    out.write(f"   Size: {stats.get('size', 0)/1024:.1f}KB | Lines: {stats.get('lines', 0)}\n")
                    out.write(f"{'─'*80}\n\n")
                    
                    content = self.safe_read_file(filepath)
                    out.write(content)
                    out.write("\n\n")
            
            # Footer
            out.write("\n" + "="*80 + "\n")
            out.write(f"✅ Export completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            out.write(f"📁 Output: {self.output_file}\n")
            out.write("="*80 + "\n")
        
        # Estadísticas de salida
        output_size = Path(self.output_file).stat().st_size / 1024 / 1024
        print(f"\n✅ Exportación completada!")
        print(f"   📊 Archivos exportados: {sum(len(f) for f in self.files_by_category.values())}")
        print(f"   📦 Archivo de salida: {self.output_file}")
        print(f"   💾 Tamaño: {output_size:.2f} MB")


def main():
    parser = argparse.ArgumentParser(
        description='FERDONAN Project Exporter v2 - Exporta proyecto con índice y estadísticas'
    )
    parser.add_argument('-o', '--output', default='ferdonan_export.txt',
                        help='Archivo de salida (default: ferdonan_export.txt)')
    parser.add_argument('-d', '--dir', default='.',
                        help='Directorio raíz del proyecto (default: current)')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Modo verbose (muestra archivos procesados)')
    
    args = parser.parse_args()
    
    try:
        exporter = ProjectExporter(root_dir=args.dir, output_file=args.output)
        exporter.export()
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
