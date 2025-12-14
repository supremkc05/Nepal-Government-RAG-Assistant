"""Hybrid retriever combining dense and sparse search."""

from typing import List, Dict, Optional, Any
from rank_bm25 import BM25Okapi
from ..core.logger import logger
from ..core.config import settings


class HybridRetriever:
    """Combines dense (vector) and sparse (BM25) retrieval."""

    def __init__(self, vector_store, embedding_model):
        """
        Initialize hybrid retriever.
        
        Args:
            vector_store: QdrantStore instance
            embedding_model: EmbeddingModel instance
        """
        self.vector_store = vector_store
        self.embedding_model = embedding_model
        self.bm25_index = None
        self.bm25_docs = []

    def index_for_bm25(self, documents: List[str]):
        """
        Build BM25 index for keyword search.
        
        Args:
            documents: List of document texts
        """
        logger.info(f"Building BM25 index for {len(documents)} documents")
        tokenized_docs = [doc.lower().split() for doc in documents]
        self.bm25_index = BM25Okapi(tokenized_docs)
        self.bm25_docs = documents
        logger.info("BM25 index built successfully")

    def retrieve_dense(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Dense retrieval using vector similarity.
        
        Args:
            query: Query string
            top_k: Number of results
            
        Returns:
            List of retrieved documents
        """
        logger.debug(f"Dense retrieval for: {query[:50]}...")
        query_vector = self.embedding_model.embed_query(query)
        results = self.vector_store.search(query_vector, top_k=top_k)
        return results

    def retrieve_sparse(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Sparse retrieval using BM25.
        
        Args:
            query: Query string
            top_k: Number of results
            
        Returns:
            List of retrieved documents
        """
        if self.bm25_index is None:
            logger.warning("BM25 index not built, skipping sparse retrieval")
            return []
        
        logger.debug(f"Sparse (BM25) retrieval for: {query[:50]}...")
        tokenized_query = query.lower().split()
        scores = self.bm25_index.get_scores(tokenized_query)
        
        # Get top-k indices
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
        
        results = []
        for idx in top_indices:
            results.append({
                "text": self.bm25_docs[idx],
                "score": float(scores[idx]),
                "metadata": {"retrieval_type": "bm25"},
            })
        
        return results

    def _normalize_scores(self, results: List[Dict], method: str = "min_max") -> List[Dict]:
        """
        Normalize scores to [0,1] range.
        
        Args:
            results: List of results with scores
            method: Normalization method (min_max, z_score)
            
        Returns:
            Results with normalized scores
        """
        if not results:
            return results
            
        scores = [r["score"] for r in results]
        
        if method == "min_max":
            min_score = min(scores)
            max_score = max(scores)
            score_range = max_score - min_score
            
            if score_range == 0:
                # All scores are the same
                for result in results:
                    result["normalized_score"] = 1.0
            else:
                for result in results:
                    result["normalized_score"] = (result["score"] - min_score) / score_range
        
        return results

    def retrieve_hybrid(self, 
                       query: str, 
                       top_k: int = 5, 
                       alpha: float = 0.7,
                       use_reranker: bool = False) -> List[Dict]:
        """
        Hybrid retrieval combining dense and sparse.
        
        Args:
            query: Query string
            top_k: Number of results
            alpha: Weight for dense retrieval (1-alpha for sparse)
            use_reranker: Whether to apply cross-encoder reranking
            
        Returns:
            Combined and reranked results
        """
        logger.info(f"Hybrid retrieval for: {query[:50]}...")
        
        # Get results from both methods (more candidates for better fusion)
        dense_k = min(top_k * 2, 20)
        sparse_k = min(top_k * 2, 20)
        
        dense_results = self.retrieve_dense(query, top_k=dense_k)
        sparse_results = self.retrieve_sparse(query, top_k=sparse_k)
        
        # Normalize scores
        dense_results = self._normalize_scores(dense_results)
        sparse_results = self._normalize_scores(sparse_results)
        
        # Combine using RRF (Reciprocal Rank Fusion) + score fusion
        combined = {}
        
        # Add dense results
        for rank, result in enumerate(dense_results, 1):
            text = result["text"]
            rrf_score = 1.0 / (60 + rank)  # RRF with k=60
            score_fusion = alpha * result.get("normalized_score", result["score"])
            
            combined[text] = {
                **result,
                "dense_score": result["score"],
                "sparse_score": 0.0,
                "rrf_score": rrf_score,
                "fusion_score": score_fusion,
                "retrieval_methods": ["dense"]
            }
        
        # Add sparse results
        for rank, result in enumerate(sparse_results, 1):
            text = result["text"]
            rrf_score = 1.0 / (60 + rank)
            score_fusion = (1 - alpha) * result.get("normalized_score", result["score"])
            
            if text in combined:
                # Document found in both - combine scores
                combined[text]["sparse_score"] = result["score"]
                combined[text]["rrf_score"] += rrf_score
                combined[text]["fusion_score"] += score_fusion
                combined[text]["retrieval_methods"].append("sparse")
            else:
                # Only in sparse results
                combined[text] = {
                    **result,
                    "dense_score": 0.0,
                    "sparse_score": result["score"],
                    "rrf_score": rrf_score,
                    "fusion_score": score_fusion,
                    "retrieval_methods": ["sparse"]
                }
        
        # Calculate final hybrid score (RRF + weighted fusion)
        for doc in combined.values():
            doc["hybrid_score"] = 0.6 * doc["rrf_score"] + 0.4 * doc["fusion_score"]
        
        # Sort by hybrid score
        final_results = sorted(
            combined.values(),
            key=lambda x: x["hybrid_score"],
            reverse=True
        )[:top_k]
        
        # Apply reranking if requested
        if use_reranker and settings.use_reranker:
            final_results = self._rerank_results(query, final_results)
        
        logger.info(f"Hybrid retrieval returned {len(final_results)} results")
        return final_results
        
    def _rerank_results(self, query: str, results: List[Dict]) -> List[Dict]:
        """
        Rerank results using a cross-encoder model.
        
        Args:
            query: Original query
            results: Results to rerank
            
        Returns:
            Reranked results
        """
        try:
            from sentence_transformers import CrossEncoder
            
            # Use a cross-encoder model for reranking
            reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
            
            # Prepare query-document pairs
            pairs = [(query, result["text"][:500]) for result in results]  # Truncate for efficiency
            
            # Get reranking scores
            rerank_scores = reranker.predict(pairs)
            
            # Add rerank scores to results
            for result, score in zip(results, rerank_scores):
                result["rerank_score"] = float(score)
            
            # Sort by rerank score
            reranked = sorted(results, key=lambda x: x["rerank_score"], reverse=True)
            logger.info("Applied cross-encoder reranking")
            
            return reranked
            
        except ImportError:
            logger.warning("Cross-encoder not available, skipping reranking")
            return results
        except Exception as e:
            logger.error(f"Reranking failed: {e}")
            return results
