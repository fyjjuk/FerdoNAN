#!/usr/bin/env python3
"""
Herramienta nativa para análisis y revisión de código.
"""

import json
import sys
from typing import Dict, Any, List


def analyze_code(code: str, language: str = "python") -> Dict:
    """
    Analiza código y retorna sugerencias de mejora.
    Nota: En una implementación real, esto podría usar un LLM o linters especializados.
    """
    issues = []
    suggestions = []
    
    # Análisis básico (puede expandirse con AST, linters, etc.)
    lines = code.split('\n')
    
    # Detectar líneas muy largas
    for i, line in enumerate(lines, 1):
        if len(line) > 100:
            issues.append({
                "line": i,
                "type": "style",
                "message": f"Línea demasiado larga ({len(line)} > 100 caracteres)"
            })
    
    # Detectar TODOs y FIXMEs
    for i, line in enumerate(lines, 1):
        if "TODO" in line.upper():
            suggestions.append({
                "line": i,
                "type": "task",
                "message": "TODO pendiente encontrado"
            })
        if "FIXME" in line.upper():
            issues.append({
                "line": i,
                "type": "bug",
                "message": "FIXME: necesita corrección"
            })
    
    # Detectar funciones sin docstring (simplificado)
    in_function = False
    for i, line in enumerate(lines, 1):
        if line.strip().startswith("def ") and not in_function:
            in_function = True
            # Verificar si la siguiente línea no vacía es docstring
            j = i
            while j < len(lines) and not lines[j].strip():
                j += 1
            if j < len(lines) and not lines[j].strip().startswith('"""') and not lines[j].strip().startswith("'''"):
                suggestions.append({
                    "line": i,
                    "type": "documentation",
                    "message": "Función sin docstring"
                })
            in_function = False
    
    return {
        "language": language,
        "total_lines": len(lines),
        "issues_count": len(issues),
        "suggestions_count": len(suggestions),
        "issues": issues,
        "suggestions": suggestions
    }


def run(input_data: Dict[str, Any]) -> Dict:
    """Punto de entrada para la herramienta nativa."""
    code = input_data.get("code", "")
    language = input_data.get("language", "python")
    
    if not code:
        return {"error": "Se requiere código para analizar"}
    
    return analyze_code(code, language)


if __name__ == "__main__":
    args = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
    result = run(args)
    print(json.dumps(result, indent=2))
