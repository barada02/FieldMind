"""
Jina AI Embeddings Client for Field Mind RAG Pipeline.
Handles text-to-vector conversion using Jina AI's embedding API.
"""

import requests
import json
from typing import List, Union
from backend.app.config import get_settings


class JinaEmbeddingClient:
    """Client for interacting with Jina AI Embeddings API."""
    
    def __init__(self):
        """Initialize the Jina embedding client with settings."""
        self.settings = get_settings()
        self.api_key = self.settings.jina_api_key
        self.model = self.settings.jina_model
        self.url = "https://api.jina.ai/v1/embeddings"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
    
    def get_embedding(
        self, 
        text: str, 
        task: str = None,
        normalized: bool = True
    ) -> List[float]:
        """
        Get embedding vector for a single text string.
        
        Args:
            text: The text to embed
            task: Task type ("retrieval.query" or "retrieval.passage"). 
                  Defaults to settings value.
            normalized: Whether to normalize the embedding vector
            
        Returns:
            List of floats representing the embedding vector
            
        Raises:
            requests.exceptions.HTTPError: If API request fails
            ValueError: If response format is invalid
        """
        if task is None:
            task = self.settings.jina_task
            
        data = {
            "model": self.model,
            "task": task,
            "normalized": normalized,
            "input": [text]
        }
        
        try:
            response = requests.post(
                self.url, 
                headers=self.headers, 
                data=json.dumps(data),
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            
            # Extract embedding from response
            if "data" in result and len(result["data"]) > 0:
                return result["data"][0]["embedding"]
            else:
                raise ValueError("Invalid response format from Jina API")
                
        except requests.exceptions.HTTPError as err:
            print(f"HTTP error occurred: {err}")
            print(f"Response content: {response.text}")
            raise
        except requests.exceptions.RequestException as err:
            print(f"An error occurred: {err}")
            raise
    
    def get_embeddings_batch(
        self,
        texts: List[str],
        task: str = None,
        normalized: bool = True
    ) -> List[List[float]]:
        """
        Get embedding vectors for multiple texts in a single API call.
        
        Args:
            texts: List of texts to embed
            task: Task type ("retrieval.query" or "retrieval.passage").
                  Defaults to settings value.
            normalized: Whether to normalize the embedding vectors
            
        Returns:
            List of embedding vectors (each vector is a list of floats)
            
        Raises:
            requests.exceptions.HTTPError: If API request fails
            ValueError: If response format is invalid
        """
        if task is None:
            task = self.settings.jina_task
            
        data = {
            "model": self.model,
            "task": task,
            "normalized": normalized,
            "input": texts
        }
        
        try:
            response = requests.post(
                self.url,
                headers=self.headers,
                data=json.dumps(data),
                timeout=60
            )
            response.raise_for_status()
            
            result = response.json()
            
            # Extract embeddings from response
            if "data" in result:
                return [item["embedding"] for item in result["data"]]
            else:
                raise ValueError("Invalid response format from Jina API")
                
        except requests.exceptions.HTTPError as err:
            print(f"HTTP error occurred: {err}")
            print(f"Response content: {response.text}")
            raise
        except requests.exceptions.RequestException as err:
            print(f"An error occurred: {err}")
            raise


# Global client instance
_client = None


def get_jina_client() -> JinaEmbeddingClient:
    """Get or create the global Jina embedding client instance."""
    global _client
    if _client is None:
        _client = JinaEmbeddingClient()
    return _client


def embed_text(text: str, task: str = "retrieval.query") -> List[float]:
    """
    Convenience function to embed a single text string.
    
    Args:
        text: The text to embed
        task: Task type ("retrieval.query" or "retrieval.passage")
        
    Returns:
        Embedding vector as list of floats
    """
    client = get_jina_client()
    return client.get_embedding(text, task=task)


def embed_texts(texts: List[str], task: str = "retrieval.passage") -> List[List[float]]:
    """
    Convenience function to embed multiple texts.
    
    Args:
        texts: List of texts to embed
        task: Task type ("retrieval.query" or "retrieval.passage")
        
    Returns:
        List of embedding vectors
    """
    client = get_jina_client()
    return client.get_embeddings_batch(texts, task=task)

# Made with Bob
