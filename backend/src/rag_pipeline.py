"""RAG Pipeline orchestrator - coordinates all components."""

from typing import List, Dict, Any, Optional
from pathlib import Path

from .embedding.embeddings import EmbeddingModel
from .vectorstore.qdrant_client import QdrantStore
from .llm.llm import LLMProvider
from .retrieval.retriver import HybridRetriever
from .ingestion.pdf_loader import PDFProcessor
from .core.config import settings
from .core.logger import logger


class RAGPipeline:
    """Main RAG pipeline coordinating all components."""

    def __init__(self):
        """Initialize RAG pipeline."""
        logger.info("Initializing RAG Pipeline")
        
        # Initialize components
        self.embedder = EmbeddingModel()
        self.vector_store = QdrantStore(embedding_dimension=self.embedder.dimension)
        self.llm = LLMProvider()
        self.retriever = HybridRetriever(self.vector_store, self.embedder)
        self.pdf_processor = PDFProcessor()
        
        logger.info("RAG Pipeline initialized successfully")

    async def ingest_document(self, pdf_path: str) -> int:
        """
        Ingest a PDF document into the vector store.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Number of chunks added
        """
        logger.info(f"Ingesting document: {pdf_path}")
        
        try:
            # Load and process PDF
            chunks = self.pdf_processor.load_pdf(pdf_path)
            
            if not chunks:
                logger.warning(f"No chunks extracted from {pdf_path}")
                return 0
            
            # Extract texts and metadata
            texts = [chunk["text"] for chunk in chunks]
            metadatas = [chunk["metadata"] for chunk in chunks]
            
            # Generate embeddings
            logger.info(f"Generating embeddings for {len(texts)} chunks")
            embeddings = self.embedder.embed_texts(texts)
            
            # Store in vector database
            logger.info("Storing in vector database")
            ids = self.vector_store.add_documents(texts, embeddings, metadatas)
            
            # Index for BM25 (sparse retrieval)
            self.retriever.index_for_bm25(texts)
            
            logger.info(f"Successfully ingested {len(ids)} chunks from {pdf_path}")
            return len(ids)
            
        except Exception as e:
            logger.error(f"Error ingesting document: {e}")
            raise

    async def ingest_directory(self, directory_path: str) -> Dict[str, int]:
        """
        Ingest all PDFs in a directory.
        
        Args:
            directory_path: Path to directory
            
        Returns:
            Dictionary of filename -> chunk count
        """
        logger.info(f"Ingesting directory: {directory_path}")
        
        dir_path = Path(directory_path)
        if not dir_path.exists():
            raise ValueError(f"Directory not found: {directory_path}")
        
        results = {}
        pdf_files = list(dir_path.glob("*.pdf"))
        
        for pdf_file in pdf_files:
            try:
                num_chunks = await self.ingest_document(str(pdf_file))
                results[pdf_file.name] = num_chunks
            except Exception as e:
                logger.error(f"Failed to ingest {pdf_file.name}: {e}")
                results[pdf_file.name] = 0
        
        total_chunks = sum(results.values())
        logger.info(f"Directory ingestion complete. Total chunks: {total_chunks}")
        
        return results

    async def query(
        self,
        query: str,
        top_k: int = 5,
        use_hybrid: bool = True,
        use_reranker: bool = False,
        history: Optional[List[Dict]] = None,
    ) -> Dict[str, Any]:
        """
        Query the RAG system.
        
        Args:
            query: User question
            top_k: Number of documents to retrieve
            use_hybrid: Use hybrid retrieval (dense + sparse)
            use_reranker: Apply reranking
            history: Conversation history
            
        Returns:
            Answer with sources
        """
        logger.info(f"Processing query: {query[:100]}")
        
        try:
            # Retrieve relevant documents
            if use_hybrid:
                logger.info("Using hybrid retrieval")
                results = self.retriever.retrieve_hybrid(
                    query=query,
                    top_k=top_k,
                    use_reranker=use_reranker,
                )
            else:
                logger.info("Using dense retrieval only")
                results = self.retriever.retrieve_dense(query, top_k=top_k)
            
            if not results:
                logger.warning("No relevant documents found")
                return {
                    "answer": "I couldn't find any relevant information to answer your question. Please try rephrasing or ask about Nepal government services like passports, citizenship, or driving licenses.",
                    "sources": [],
                }
            
            # Format context for LLM
            context_docs = []
            for i, result in enumerate(results):
                context_docs.append({
                    "text": result["text"],
                    "metadata": result.get("metadata", {}),
                    "score": result.get("score", 0.0),
                })
            
            # Generate answer
            logger.info(f"Generating answer with {len(context_docs)} context documents")
            answer = self.llm.generate(
                prompt=query,
                context=context_docs,
                max_tokens=1000,
                temperature=0.7,
            )
            
            # Format sources
            sources = []
            for i, doc in enumerate(context_docs, 1):
                source = {
                    "rank": i,
                    "text": doc["text"][:300] + "..." if len(doc["text"]) > 300 else doc["text"],
                    "full_text": doc["text"],
                    "metadata": doc["metadata"],
                    "score": doc["score"],
                }
                sources.append(source)
            
            return {
                "answer": answer,
                "sources": sources,
            }
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            raise

    async def query_stream(
        self,
        query: str,
        top_k: int = 5,
        use_hybrid: bool = True,
        use_reranker: bool = False,
    ):
        """
        Query with streaming response.
        
        Args:
            query: User question
            top_k: Number of documents to retrieve
            use_hybrid: Use hybrid retrieval
            use_reranker: Apply reranking
            
        Yields:
            Answer chunks
        """
        logger.info(f"Processing streaming query: {query[:100]}")
        
        try:
            # Retrieve documents (same as non-streaming)
            if use_hybrid:
                results = self.retriever.retrieve_hybrid(
                    query=query,
                    top_k=top_k,
                    use_reranker=use_reranker,
                )
            else:
                results = self.retriever.retrieve_dense(query, top_k=top_k)
            
            if not results:
                yield "I couldn't find any relevant information to answer your question."
                return
            
            # Format context
            context_docs = [
                {"text": r["text"], "metadata": r.get("metadata", {})}
                for r in results
            ]
            
            # Stream answer
            async for chunk in self.llm.generate_stream(
                prompt=query,
                context=context_docs,
                max_tokens=1000,
                temperature=0.7,
            ):
                yield chunk
                
        except Exception as e:
            logger.error(f"Error in streaming query: {e}")
            yield f"Error: {str(e)}"

    def get_stats(self) -> Dict[str, Any]:
        """
        Get pipeline statistics.
        
        Returns:
            Stats dictionary
        """
        return {
            "vector_store": self.vector_store.get_collection_info(),
            "embedding_model": self.embedder.model_name,
            "embedding_dimension": self.embedder.dimension,
            "llm_provider": self.llm.provider,
        }
