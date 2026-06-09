import chromadb
import datetime
import os
import hashlib
from sentence_transformers import SentenceTransformer
from chromadb.utils import embedding_functions
from core.logger import logger

class RAGEngine:
    def __init__(self, storage_path="data/rag_storage"):
        os.makedirs(storage_path, exist_ok=True)
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name='all-MiniLM-L6-v2'
        )
        self.client = chromadb.PersistentClient(path=storage_path)
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.collection_cache = {}

    def _get_collection(self, agent_id):
        if agent_id in self.collection_cache:
            return self.collection_cache[agent_id]
        name = f"agent_{agent_id}_knowledge"
        collection = self.client.get_or_create_collection(
            name=name,
            embedding_function=self.embedding_fn
        )
        self.collection_cache[agent_id] = collection
        return collection

    def index_document(self, agent_id, content, metadata):
        collection = self._get_collection(agent_id)
        embedding = self.model.encode(content).tolist()
        doc_id = hashlib.md5(f"{agent_id}{content}{metadata.get('timestamp', '')}".encode()).hexdigest()
        collection.add(
            embeddings=[embedding],
            documents=[content],
            metadatas=[metadata],
            ids=[doc_id]
        )
        logger.info(f"RAG_INDEX: Documento {doc_id} indexado en {agent_id}")
        return doc_id

    def rag_query(self, agent_id, query_text, top_k=5, similarity_threshold=0.75):
        """Consulta RAG con filtro de similitud."""
        collection = self._get_collection(agent_id)
        query_embedding = self.model.encode(query_text).tolist()
        # Pedir más resultados para filtrar después
        results = collection.query(
            query_embeddings=[query_embedding], 
            n_results=top_k * 3
        )
        
        # Filtrar por similitud si hay distancias
        if results and results.get('distances') and results['distances'][0]:
            filtered_docs = []
            filtered_metadatas = []
            filtered_distances = []
            for i, dist in enumerate(results['distances'][0]):
                # Convertir distancia a similitud
                similarity = 1 - dist if dist <= 1 else 0
                if similarity >= similarity_threshold:
                    filtered_docs.append(results['documents'][0][i])
                    filtered_distances.append(dist)
                    if results.get('metadatas') and results['metadatas'][0]:
                        filtered_metadatas.append(results['metadatas'][0][i])
            
            # Actualizar resultados
            results['documents'][0] = filtered_docs[:top_k]
            results['distances'][0] = filtered_distances[:top_k]
            if filtered_metadatas:
                results['metadatas'][0] = filtered_metadatas[:top_k]
        
        logger.info(f"RAG_QUERY: {agent_id} - {len(results['documents'][0])} resultados (threshold={similarity_threshold})")
        return results

    def index_conversation_turn(self, agent_id, user_msg, assistant_msg, metadata=None):
        content = f"Usuario: {user_msg}\nAsistente: {assistant_msg}"
        meta = {"type": "conversation", "timestamp": datetime.datetime.now().isoformat()}
        if metadata:
            meta.update(metadata)
        return self.index_document(agent_id, content, meta)

    def process_and_index(self, agent_id, file_path):
        try:
            import docx
            import pandas as pd
        except ImportError as e:
            logger.error(f"Dependencia faltante para indexar {file_path}: {e}")
            return None
            
        ext = os.path.splitext(file_path)[1].lower()
        try:
            if ext == '.docx':
                doc = docx.Document(file_path)
                text = "\n".join([para.text for para in doc.paragraphs])
            elif ext == '.xlsx':
                df = pd.read_excel(file_path)
                text = df.to_string()
            elif ext == '.md' or ext == '.txt':
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
            else:
                raise ValueError(f"Formato no soportado: {ext}")
            metadata = {"source": file_path, "timestamp": str(os.path.getmtime(file_path))}
            return self.index_document(agent_id, text, metadata)
        except Exception as e:
            logger.error(f"Error procesando {file_path}: {e}")
            return None

    def delete_namespace(self, agent_id):
        self.client.delete_collection(f"agent_{agent_id}_knowledge")
        if agent_id in self.collection_cache:
            del self.collection_cache[agent_id]
        logger.info(f"RAG_NAMESPACE_DELETED: {agent_id}")
