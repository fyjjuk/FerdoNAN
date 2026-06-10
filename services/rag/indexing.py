"""
Indexación de documentos para RAG
"""
import os
import datetime
from typing import Dict, Any, Optional
from core.logger import logger
from .utils import generate_document_id, validate_agent_id
from .collection import CollectionManager


class IndexingService:
    """Servicio para indexar documentos en RAG."""
    
    def __init__(self, collection_manager: CollectionManager, embedding_model):
        self.collection_manager = collection_manager
        self.model = embedding_model
    
    def index_document(self, agent_id: str, content: str, metadata: Dict[str, Any]) -> Optional[str]:
        """
        Indexa un documento en la colección del agente.
        
        Args:
            agent_id: Identificador del agente
            content: Contenido del documento
            metadata: Metadatos asociados
            
        Returns:
            str: ID del documento indexado o None si error
        """
        if not validate_agent_id(agent_id):
            return None
        
        collection = self.collection_manager.get_collection(agent_id)
        if collection is None:
            return None
        
        embedding = self.model.encode(content).tolist()
        doc_id = generate_document_id(agent_id, content, metadata.get('timestamp', ''))
        
        collection.add(
            embeddings=[embedding],
            documents=[content],
            metadatas=[metadata],
            ids=[doc_id]
        )
        logger.info(f"RAG_INDEX: Documento {doc_id} indexado en {agent_id}")
        return doc_id
    
    def index_conversation_turn(self, agent_id: str, user_msg: str, 
                                 assistant_msg: str, metadata: Optional[Dict] = None) -> Optional[str]:
        """
        Indexa un turno de conversación.
        
        Args:
            agent_id: Identificador del agente
            user_msg: Mensaje del usuario
            assistant_msg: Respuesta del asistente
            metadata: Metadatos adicionales
            
        Returns:
            str: ID del documento indexado
        """
        content = f"Usuario: {user_msg}\nAsistente: {assistant_msg}"
        meta = {"type": "conversation", "timestamp": datetime.datetime.now().isoformat()}
        if metadata:
            meta.update(metadata)
        return self.index_document(agent_id, content, meta)
    
    def process_and_index_file(self, agent_id: str, file_path: str) -> Optional[str]:
        """
        Procesa y indexa un archivo (docx, xlsx, txt, md).
        
        Args:
            agent_id: Identificador del agente
            file_path: Ruta del archivo
            
        Returns:
            str: ID del documento indexado o None si error
        """
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
