import chromadb
import datetime
import os
import hashlib
from sentence_transformers import SentenceTransformer
from core.logger import logger

class RAGEngine:
    def __init__(self, storage_path="data/rag_storage"):
        os.makedirs(storage_path, exist_ok=True)
        self.client = chromadb.PersistentClient(path=storage_path)
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.collection_cache = {}

    def _get_collection(self, agent_id):
        if agent_id in self.collection_cache:
            return self.collection_cache[agent_id]
        name = f"agent_{agent_id}_knowledge"
        collection = self.client.get_or_create_collection(name=name)
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

    def rag_query(self, agent_id, query_text, top_k=3):
        collection = self._get_collection(agent_id)
        query_embedding = self.model.encode(query_text).tolist()
        results = collection.query(query_embeddings=[query_embedding], n_results=top_k)
        logger.info(f"RAG_QUERY: Consulta realizada en {agent_id}, {len(results['documents'][0])} resultados")
        return results

    def index_conversation_turn(self, agent_id, user_msg, assistant_msg, metadata=None):
        """Indexa un turno de conversación para memoria a largo plazo."""
        content = f"Usuario: {user_msg}\nAsistente: {assistant_msg}"
        meta = {"type": "conversation", "timestamp": datetime.datetime.now().isoformat()}
        if metadata:
            meta.update(metadata)
        return self.index_document(agent_id, content, meta)

    def process_and_index(self, agent_id, file_path):
        import docx
        import pandas as pd
        ext = os.path.splitext(file_path)[1].lower()
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

    def delete_namespace(self, agent_id):
        self.client.delete_collection(f"agent_{agent_id}_knowledge")
        if agent_id in self.collection_cache:
            del self.collection_cache[agent_id]
        logger.info(f"RAG_NAMESPACE_DELETED: {agent_id}")
