"""
ChromaDB Vector Store Manager for Field Mind RAG Pipeline.
Handles document storage, retrieval, and similarity search.
"""

import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Dict, Optional, Any
from backend.app.config import get_settings
from backend.rag.embeddings import embed_text, embed_texts


class ChromaDBManager:
    """Manager for ChromaDB vector store operations."""
    
    def __init__(self):
        """Initialize ChromaDB client and collection."""
        self.settings = get_settings()
        
        # Initialize ChromaDB client with persistence
        self.client = chromadb.PersistentClient(
            path=self.settings.chroma_persist_directory,
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Get or create collection
        self.collection_name = self.settings.chroma_collection_name
        self.collection = self._get_or_create_collection()
    
    def _get_or_create_collection(self):
        """Get existing collection or create a new one."""
        try:
            # Try to get existing collection
            collection = self.client.get_collection(name=self.collection_name)
            print(f"Loaded existing collection: {self.collection_name}")
        except Exception:
            # Create new collection if it doesn't exist
            collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "SOP documents for Field Mind"}
            )
            print(f"Created new collection: {self.collection_name}")
        
        return collection
    
    def add_documents(
        self,
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None
    ) -> None:
        """
        Add documents to the vector store.
        
        Args:
            documents: List of text documents to add
            metadatas: Optional list of metadata dicts for each document
            ids: Optional list of unique IDs for each document.
                 If not provided, auto-generated IDs will be used.
        
        Raises:
            ValueError: If documents list is empty or lengths don't match
        """
        if not documents:
            raise ValueError("Documents list cannot be empty")
        
        # Validate input lengths
        if metadatas and len(metadatas) != len(documents):
            raise ValueError("Metadatas length must match documents length")
        if ids and len(ids) != len(documents):
            raise ValueError("IDs length must match documents length")
        
        # Generate IDs if not provided
        if ids is None:
            # Use collection count to generate unique IDs
            start_id = self.collection.count()
            ids = [f"doc_{start_id + i}" for i in range(len(documents))]
        
        # Generate embeddings for documents
        print(f"Generating embeddings for {len(documents)} documents...")
        embeddings = embed_texts(documents, task="retrieval.passage")
        
        # Add to collection
        self.collection.add(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
        
        print(f"Successfully added {len(documents)} documents to collection")
    
    def add_document(
        self,
        document: str,
        metadata: Optional[Dict[str, Any]] = None,
        doc_id: Optional[str] = None
    ) -> str:
        """
        Add a single document to the vector store.
        
        Args:
            document: Text document to add
            metadata: Optional metadata dict for the document
            doc_id: Optional unique ID for the document
            
        Returns:
            The ID of the added document
        """
        if doc_id is None:
            doc_id = f"doc_{self.collection.count()}"
        
        # Generate embedding
        embedding = embed_text(document, task="retrieval.passage")
        
        # Add to collection
        self.collection.add(
            documents=[document],
            embeddings=[embedding],
            metadatas=[metadata] if metadata else None,
            ids=[doc_id]
        )
        
        print(f"Successfully added document with ID: {doc_id}")
        return doc_id
    
    def query_documents(
        self,
        query: str,
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None,
        where_document: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Query the vector store for similar documents.
        
        Args:
            query: Query text to search for
            n_results: Number of results to return (default: 5)
            where: Optional metadata filter
            where_document: Optional document content filter
            
        Returns:
            Dictionary containing:
                - ids: List of document IDs
                - documents: List of document texts
                - metadatas: List of metadata dicts
                - distances: List of similarity distances
        """
        # Generate query embedding
        query_embedding = embed_text(query, task="retrieval.query")
        
        # Query collection
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where,
            where_document=where_document
        )
        
        # Format results
        formatted_results = {
            "ids": results["ids"][0] if results["ids"] else [],
            "documents": results["documents"][0] if results["documents"] else [],
            "metadatas": results["metadatas"][0] if results["metadatas"] else [],
            "distances": results["distances"][0] if results["distances"] else []
        }
        
        return formatted_results
    
    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific document by ID.
        
        Args:
            doc_id: The document ID to retrieve
            
        Returns:
            Dictionary with document data or None if not found
        """
        try:
            result = self.collection.get(ids=[doc_id])
            if result["ids"]:
                return {
                    "id": result["ids"][0],
                    "document": result["documents"][0],
                    "metadata": result["metadatas"][0] if result["metadatas"] else None
                }
        except Exception as e:
            print(f"Error retrieving document {doc_id}: {e}")
        
        return None
    
    def delete_document(self, doc_id: str) -> bool:
        """
        Delete a document by ID.
        
        Args:
            doc_id: The document ID to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.collection.delete(ids=[doc_id])
            print(f"Successfully deleted document: {doc_id}")
            return True
        except Exception as e:
            print(f"Error deleting document {doc_id}: {e}")
            return False
    
    def delete_documents(self, doc_ids: List[str]) -> bool:
        """
        Delete multiple documents by IDs.
        
        Args:
            doc_ids: List of document IDs to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.collection.delete(ids=doc_ids)
            print(f"Successfully deleted {len(doc_ids)} documents")
            return True
        except Exception as e:
            print(f"Error deleting documents: {e}")
            return False
    
    def count_documents(self) -> int:
        """
        Get the total number of documents in the collection.
        
        Returns:
            Number of documents
        """
        return self.collection.count()
    
    def reset_collection(self) -> None:
        """
        Delete all documents from the collection.
        WARNING: This operation cannot be undone.
        """
        # Delete the collection
        self.client.delete_collection(name=self.collection_name)
        
        # Recreate empty collection
        self.collection = self._get_or_create_collection()
        print(f"Collection {self.collection_name} has been reset")


# Global manager instance
_manager = None


def get_chroma_manager() -> ChromaDBManager:
    """Get or create the global ChromaDB manager instance."""
    global _manager
    if _manager is None:
        _manager = ChromaDBManager()
    return _manager

# Made with Bob
