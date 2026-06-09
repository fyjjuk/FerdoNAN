#!/usr/bin/env python3
"""Valida estáticamente todas las rutas YAML de agentes y la librería."""
import sys
import os
from pathlib import Path

# Añadir el directorio raíz del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import yaml
from models.route_models import validate_route

def main():
    root = Path(".")
    errors = 0
    for yaml_file in root.glob("agents/*/routes/*.yaml"):
        with open(yaml_file) as f:
            data = yaml.safe_load(f)
        ok, _, errs = validate_route(data)
        if not ok:
            print(f"❌ {yaml_file}: {errs}")
            errors += 1
        else:
            print(f"✅ {yaml_file}")
    sys.exit(1 if errors else 0)

if __name__ == "__main__":
    main()
