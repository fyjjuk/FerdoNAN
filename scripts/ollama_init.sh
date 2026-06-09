#!/bin/bash
# Script para inicializar Ollama con modelos comunes
ollama pull phi3:mini
ollama pull llama3.2:3b
ollama pull phi4-mini
echo "Modelos descargados. Ollama listo."
