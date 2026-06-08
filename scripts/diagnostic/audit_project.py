import os

def audit_project(root_dir='.'):
    exclude = {'.git', '__pycache__', 'venv', '.venv', '.pytest_cache', 'logs'}
    print(f"--- Mapeo de FerdoNAN ({os.path.abspath(root_dir)}) ---")
    
    for root, dirs, files in os.walk(root_dir):
        # Filtrar directorios excluidos
        dirs[:] = [d for d in dirs if d not in exclude]
        
        level = root.replace(root_dir, '').count(os.sep)
        indent = ' ' * 4 * (level)
        print(f"{indent}{os.path.basename(root)}/")
        
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            print(f"{subindent}{f}")

if __name__ == "__main__":
    audit_project()
