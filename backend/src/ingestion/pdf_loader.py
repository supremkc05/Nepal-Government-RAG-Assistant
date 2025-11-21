"""PDF loading and text extraction."""

from pathlib import Path
from typing import List, Dict
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from ..core.config import settings
from ..core.logger import logger

class PDFProcessor:
    """Process PDF documents for RAG."""
    
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            length_function=len,
        )
        self.use_langchain = True
        logger.info("Using LangChain PDF processing")

    def load_pdf(self, pdf_path: str) -> List[Dict]:
        """Load PDF and extract text with page metadata.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            List of document chunks with metadata
        """
        logger.info(f"Loading PDF: {pdf_path}")
        try:
            if self.use_langchain:
                # Use LangChain approach
                loader = PyPDFLoader(pdf_path)
                pages = loader.load()
                
                logger.info(f"Loaded {len(pages)} pages from {pdf_path}")
                
                # Split pages into chunks
                docs = self.text_splitter.split_documents(pages)
                logger.info(f"Split into {len(docs)} chunks")
                
                # Convert to list of dicts with metadata
                result = []
                for doc in docs:
                    chunk_data = {
                        "text": doc.page_content,
                        "metadata": doc.metadata
                    }
                    result.append(chunk_data)
                
                return result
            else:
                # Fallback processing (not implemented here)
                logger.error("Fallback PDF processing not implemented")
                return []
        except Exception as e:
            logger.error(f"Error loading PDF {pdf_path}: {e}")
            raise

    def save_processed(self, chunks: List[Dict], output_path: str) -> None:
        """Save processed chunks to disk.
        
        Args:
            chunks: List of document chunks with metadata
            output_path: Path to save the processed chunks
        """
        import json
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(chunks, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Saved {len(chunks)} chunks to {output_path}")

    def process_pdf_directory(self, pdf_dir: str) -> List[Dict]:
        """Process all PDFs in a directory.
        
        Args:
            pdf_dir: Path to directory containing PDF files
            
        Returns:
            Combined list of all document chunks
        """
        pdf_path = Path(pdf_dir)
        all_chunks = []
        
        if not pdf_path.exists():
            logger.error(f"Directory not found: {pdf_dir}")
            return []
        
        pdf_files = list(pdf_path.glob("*.pdf"))
        logger.info(f"Found {len(pdf_files)} PDF files in {pdf_dir}")
        
        for pdf_file in pdf_files:
            try:
                chunks = self.load_pdf(str(pdf_file))
                all_chunks.extend(chunks)
                logger.info(f"Processed {pdf_file.name}: {len(chunks)} chunks")
            except Exception as e:
                logger.error(f"Failed to process {pdf_file.name}: {e}")
                continue
        
        logger.info(f"Total chunks processed: {len(all_chunks)}")
        return all_chunks



