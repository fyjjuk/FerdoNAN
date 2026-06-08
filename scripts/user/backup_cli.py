#!/usr/bin/env python
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from persistence.backup import BackupManager

def main():
    mgr = BackupManager()
    
    if len(sys.argv) < 2:
        print("Uso: python scripts/user/backup_cli.py [crear|listar|restaurar] [nombre]")
        return
    
    cmd = sys.argv[1]
    
    if cmd == "crear":
        name = sys.argv[2] if len(sys.argv) > 2 else None
        path = mgr.create_backup(name)
        print(f"✅ Backup creado: {path}")
    
    elif cmd == "listar":
        backups = mgr.list_backups()
        print("\n📦 Backups disponibles:")
        for b in backups:
            print(f"   {b['name']} - {b['size_mb']:.2f} MB - {b['modified']}")
    
    elif cmd == "restaurar":
        if len(sys.argv) < 3:
            print("❌ Especifica el nombre del backup")
            return
        temp_dir = mgr.restore_backup(sys.argv[2])
        print(f"✅ Backup restaurado en: {temp_dir}")
    
    else:
        print("❌ Comando no reconocido")

if __name__ == "__main__":
    main()
