"""Dependency injection for API routes."""

from functools import lru_cache
from typing import Optional

from ..embedding.embeddings import EmbeddingModel
from ..vectorstore.qdrant_client import QdrantStore
from ..llm.llm import LLMProvider
from ..retrieval.retriver import HybridRetriever
from ..core.logger import logger


# Singletons
_embedding_model: Optional[EmbeddingModel] = None
_vector_store: Optional[QdrantStore] = None
_llm_provider: Optional[LLMProvider] = None
_hybrid_retriever: Optional[HybridRetriever] = None
_rag_pipeline: Optional['RAGPipeline'] = None
_cache_manager: Optional['CacheManager'] = None
_memory_manager: Optional['MemoryManager'] = None


def get_embedding_model() -> EmbeddingModel:
    """Get or create embedding model singleton."""
    global _embedding_model
    if _embedding_model is None:
        logger.info("Initializing embedding model")
        _embedding_model = EmbeddingModel()
    return _embedding_model


def get_vector_store() -> QdrantStore:
    """Get or create vector store singleton."""
    global _vector_store
    if _vector_store is None:
        logger.info("Initializing vector store")
        embedder = get_embedding_model()
        _vector_store = QdrantStore(embedding_dimension=embedder.dimension)
    return _vector_store


def get_llm_provider() -> LLMProvider:
    """Get or create LLM provider singleton."""
    global _llm_provider
    if _llm_provider is None:
        logger.info("Initializing LLM provider")
        _llm_provider = LLMProvider()
    return _llm_provider


def get_hybrid_retriever() -> HybridRetriever:
    """Get or create hybrid retriever singleton."""
    global _hybrid_retriever
    if _hybrid_retriever is None:
        logger.info("Initializing hybrid retriever")
        vector_store = get_vector_store()
        embedder = get_embedding_model()
        _hybrid_retriever = HybridRetriever(vector_store, embedder)
    return _hybrid_retriever


def get_rag_pipeline():
    """Get or create RAG pipeline singleton."""
    global _rag_pipeline
    if _rag_pipeline is None:
        logger.info("Initializing RAG pipeline")
        from ..rag_pipeline import RAGPipeline
        _rag_pipeline = RAGPipeline()
    return _rag_pipeline


def get_cache_manager():
    """Get or create cache manager singleton."""
    global _cache_manager
    if _cache_manager is None:
        logger.info("Initializing cache manager")
        from ..cache.cache_manager import CacheManager
        _cache_manager = CacheManager()
    return _cache_manager


def get_memory_manager():
    """Get or create memory manager singleton."""
    global _memory_manager
    if _memory_manager is None:
        logger.info("Initializing memory manager")
        from ..cache.memory_manager import MemoryManager
        _memory_manager = MemoryManager()
    return _memory_manager
