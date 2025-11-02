import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Dict, Any, Optional
from config import settings


class ChromaService:
    def __init__(self):
        # Use the new PersistentClient API (chromadb 0.4.0+)
        self.client = chromadb.PersistentClient(
            path=settings.chroma_persist_dir,
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        self.collection_name = "pdf_chunks"
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"description": "PDF document chunks with embeddings"}
        )
    
    def add_chunks(
        self,
        documents: List[str],
        metadatas: List[Dict[str, Any]],
        ids: List[str],
        embeddings: List[List[float]]
    ) -> None:
        """
        Add chunks to Chroma collection.
        
        Args:
            documents: List of text chunks
            metadatas: List of metadata dicts
            ids: List of unique IDs
            embeddings: List of embedding vectors
        """
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids,
            embeddings=embeddings
        )
        # Note: PersistentClient auto-persists; no explicit persist() needed
    
    def query(
        self,
        query_embeddings: List[List[float]],
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None,
        include: List[str] = None
    ) -> Dict[str, Any]:
        """
        Query the collection for similar chunks.
        
        Args:
            query_embeddings: List of query embedding vectors
            n_results: Number of results to return
            where: Filter conditions
            include: Fields to include in results
        
        Returns:
            Query results
        """
        if include is None:
            include = ["documents", "metadatas", "distances"]
        
        return self.collection.query(
            query_embeddings=query_embeddings,
            n_results=n_results,
            where=where,
            include=include
        )
    
    def get_by_ids(
        self,
        ids: List[str],
        include: List[str] = None
    ) -> Dict[str, Any]:
        """
        Get chunks by their IDs.
        
        Args:
            ids: List of chunk IDs
            include: Fields to include in results
        
        Returns:
            Chunks data
        """
        if include is None:
            include = ["documents", "metadatas"]
        
        return self.collection.get(
            ids=ids,
            include=include
        )
    
    def delete_by_file_id(self, file_id: str) -> None:
        """
        Delete all chunks for a specific file.
        
        Args:
            file_id: File ID to delete chunks for
        """
        self.collection.delete(
            where={"file_id": file_id}
        )
        # Note: PersistentClient auto-persists; no explicit persist() needed
    
    def count(self) -> int:
        """Get total number of chunks in collection."""
        return self.collection.count()


# Global Chroma service instance
chroma_service = ChromaService()
