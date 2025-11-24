"""Embedding model wrapper for text vectorization."""

from typing import List, Optional
from sentence_transformers import SentenceTransformer
from ..core.config import settings
from ..core.logger import logger


class EmbeddingModel:
    """Wrapper for embedding model."""

    def __init__(self, model_name: Optional[str] = None, device: Optional[str] = None):
        """
        Initialize embedding model.
        
        Args:
            model_name: HuggingFace model name
            device: cpu or cuda
        """
        self.model_name = model_name or settings.embedding_model
        self.device = device or settings.embedding_device
        
        logger.info(f"Loading embedding model: {self.model_name} on {self.device}")
        self.model = SentenceTransformer(self.model_name, device=self.device)
        logger.info("Embedding model loaded successfully")

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for texts.
        
        Args:
            texts: List of text strings
            
        Returns:
            List of embedding vectors
        """
        if not texts:
            logger.warning("Empty text list provided for embedding")
            return []
            
        logger.debug(f"Embedding {len(texts)} texts")
        embeddings = self.model.encode(texts, show_progress_bar=False)
        return embeddings.tolist()

    def embed_query(self, query: str) -> List[float]:
        """
        Generate embedding for a single query.
        
        Args:
            query: Query string
            
        Returns:
            Embedding vector
        """
        if not query or not query.strip():
            logger.warning("Empty query provided for embedding")
            return []
            
        logger.debug(f"Embedding query: {query[:50]}...")
        embedding = self.model.encode([query], show_progress_bar=False)[0]
        return embedding.tolist()

    @property
    def dimension(self) -> int:
        """Get embedding dimension."""
        return self.model.get_sentence_embedding_dimension()