#!/bin/bash
# Fix #3: RAG Query Injection Hardening
# Problema: vector_store.py no sanitiza queries antes de ChromaDB

VECTOR_STORE_FILE="services/vector_store.py"
EXECUTOR_FILE="services/executor/cognitive.py"

echo "==== FIX #3: RAG Query Injection Hardening ===="
echo ""

# Verificar que rag_query existe
if grep -q "def rag_query" "$VECTOR_STORE_FILE"; then
    echo "✓ Método rag_query encontrado en vector_store.py"
    
    # Crear patch que agrega sanitización
    cat > /tmp/patch_rag_injection.py << 'EOF'
import sys

with open(sys.argv[1], 'r') as f:
    content = f.read()

# Buscar la función rag_query
old_func_start = '''    def rag_query(self, agent_id, query_text, top_k=5, similarity_threshold=0.75):
        """Consulta RAG con filtro de similitud."""
        collection = self._get_collection(agent_id)'''

new_func_start = '''    def rag_query(self, agent_id, query_text, top_k=5, similarity_threshold=0.75):
        """Consulta RAG con filtro de similitud."""
        # === SANITIZACIÓN DE QUERY ===
        if query_text is None or not isinstance(query_text, str):
            logger.error(f"RAG_QUERY: Input inválido (type={type(query_text)})")
            return {"documents": [[]], "distances": [[]], "metadatas": [[]]}
        
        query_text = query_text.strip()
        if len(query_text) > 1000:
            logger.warning(f"RAG_QUERY: Query muy largo ({len(query_text)} chars), truncando")
            query_text = query_text[:1000]
        
        if not query_text:
            logger.error("RAG_QUERY: Query vacío después de sanitización")
            return {"documents": [[]], "distances": [[]], "metadatas": [[]]}
        # === FIN SANITIZACIÓN ===
        
        collection = self._get_collection(agent_id)'''

if old_func_start in content:
    content = content.replace(old_func_start, new_func_start)
    with open(sys.argv[1], 'w') as f:
        f.write(content)
    print("✓ Sanitización RAG inyectada en vector_store.py")
else:
    print("⚠ Patrón no encontrado exactamente. Intentando búsqueda parcial...")
    if "def rag_query" in content:
        print("  → Método existe pero estructura diferente")
        print("  → Editar manualmente: services/vector_store.py")
    sys.exit(1)

EOF

    # Aplicar patch a vector_store.py
    cp "$VECTOR_STORE_FILE" "${VECTOR_STORE_FILE}.backup_rag"
    echo "✓ Backup: ${VECTOR_STORE_FILE}.backup_rag"
    
    python3 /tmp/patch_rag_injection.py "$VECTOR_STORE_FILE"
    if [ $? -eq 0 ]; then
        echo "✓ RAG sanitización inyectada"
    else
        cp "${VECTOR_STORE_FILE}.backup_rag" "$VECTOR_STORE_FILE"
        echo "✗ Revert: estructura diferente a la esperada"
        exit 1
    fi
    
    # Verificar que executor también está usando sanitización en el contexto
    echo ""
    echo "Verificando sanitización en CognitiveExecutor..."
    
    if grep -q "context_results = rag_engine.rag_query" "$EXECUTOR_FILE"; then
        echo "✓ CognitiveExecutor invoca rag_query"
        echo "  (Sanitización ocurre en vector_store.rag_query ahora)"
    else
        echo "⚠ CognitiveExecutor no invoca rag_query directamente"
    fi
    
else
    echo "✗ rag_query NO encontrado en $VECTOR_STORE_FILE"
    exit 1
fi

echo ""
echo "==== RESUMEN ===="
echo "Cambios aplicados a vector_store.py.rag_query():"
echo "  ✓ Validación de tipo de query"
echo "  ✓ Limitación de longitud (max 1000 chars)"
echo "  ✓ Check de query vacío"
echo "  ✓ Logging de errores en cada etapa"
echo ""
