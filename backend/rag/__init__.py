"""
RAG (Retrieval-Augmented Generation) Pipeline for Field Mind.
High-level interface for document retrieval and context generation.
"""

from typing import List, Dict, Optional, Any
from backend.rag.embeddings import get_jina_client, embed_text
from backend.rag.vector_store import get_chroma_manager


def rag_tool(
    query: str,
    n_results: int = 5,
    where: Optional[Dict[str, Any]] = None,
    include_metadata: bool = True
) -> Dict[str, Any]:
    """
    High-level RAG tool that performs the complete retrieval pipeline.
    
    Pipeline Flow:
    1. Query text → Jina Client → Query embedding vector
    2. Query vector → ChromaDB → Top-K similar documents
    3. Return context text with metadata
    
    Args:
        query: The search query text
        n_results: Number of top results to return (default: 5)
        where: Optional metadata filter for ChromaDB query
        include_metadata: Whether to include metadata in results (default: True)
        
    Returns:
        Dictionary containing:
            - query: Original query text
            - context: Combined text from retrieved documents
            - documents: List of retrieved document texts
            - ids: List of document IDs
            - distances: List of similarity distances
            - metadatas: List of metadata dicts (if include_metadata=True)
            - count: Number of results returned
    """
    # Get ChromaDB manager
    chroma_manager = get_chroma_manager()
    
    # Query the vector store (this internally generates the embedding)
    results = chroma_manager.query_documents(
        query=query,
        n_results=n_results,
        where=where
    )
    
    # Combine documents into context text
    context = "\n\n---\n\n".join(results["documents"]) if results["documents"] else ""
    
    # Build response
    response = {
        "query": query,
        "context": context,
        "documents": results["documents"],
        "ids": results["ids"],
        "distances": results["distances"],
        "count": len(results["documents"])
    }
    
    if include_metadata:
        response["metadatas"] = results["metadatas"]
    
    return response


def add_documents_to_rag(
    documents: List[str],
    metadatas: Optional[List[Dict[str, Any]]] = None,
    ids: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Add documents to the RAG system's vector store.
    
    Args:
        documents: List of text documents to add
        metadatas: Optional list of metadata dicts for each document
        ids: Optional list of unique IDs for each document
        
    Returns:
        Dictionary with operation status:
            - success: Boolean indicating success
            - count: Number of documents added
            - message: Status message
    """
    try:
        chroma_manager = get_chroma_manager()
        chroma_manager.add_documents(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        return {
            "success": True,
            "count": len(documents),
            "message": f"Successfully added {len(documents)} documents to RAG system"
        }
    except Exception as e:
        return {
            "success": False,
            "count": 0,
            "message": f"Error adding documents: {str(e)}"
        }


def add_document_to_rag(
    document: str,
    metadata: Optional[Dict[str, Any]] = None,
    doc_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Add a single document to the RAG system's vector store.
    
    Args:
        document: Text document to add
        metadata: Optional metadata dict for the document
        doc_id: Optional unique ID for the document
        
    Returns:
        Dictionary with operation status:
            - success: Boolean indicating success
            - doc_id: ID of the added document
            - message: Status message
    """
    try:
        chroma_manager = get_chroma_manager()
        doc_id = chroma_manager.add_document(
            document=document,
            metadata=metadata,
            doc_id=doc_id
        )
        
        return {
            "success": True,
            "doc_id": doc_id,
            "message": f"Successfully added document with ID: {doc_id}"
        }
    except Exception as e:
        return {
            "success": False,
            "doc_id": None,
            "message": f"Error adding document: {str(e)}"
        }


def get_rag_stats() -> Dict[str, Any]:
    """
    Get statistics about the RAG system's vector store.
    
    Returns:
        Dictionary with statistics:
            - total_documents: Total number of documents in the store
            - collection_name: Name of the ChromaDB collection
            - persist_directory: Path to ChromaDB persistence directory
    """
    from backend.app.config import get_settings
    
    settings = get_settings()
    chroma_manager = get_chroma_manager()
    
    return {
        "total_documents": chroma_manager.count_documents(),
        "collection_name": settings.chroma_collection_name,
        "persist_directory": settings.chroma_persist_directory
    }


# Export main functions
__all__ = [
    "rag_tool",
    "add_documents_to_rag",
    "add_document_to_rag",
    "get_rag_stats",
    "get_jina_client",
    "get_chroma_manager"
]

# Made with Bob
