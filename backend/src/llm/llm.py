"""LLM provider wrapper for generating responses."""

from typing import List, Dict, Optional, Any
import os

from ..core.config import settings
from ..core.logger import logger


class LLMProvider:
    """Unified LLM provider supporting multiple models."""

    def __init__(self, provider: Optional[str] = None):
        """
        Initialize LLM provider.
        
        Args:
            provider: LLM provider name (gemini, openai)
        """
        self.provider = provider or settings.llm_provider
        self.model = None
        
        logger.info(f"Initializing LLM provider: {self.provider}")
        self._initialize_model()

    def _initialize_model(self):
        """Initialize the appropriate LLM model."""
        if self.provider == "gemini":
            self._initialize_gemini()
        elif self.provider == "openai":
            self._initialize_openai()
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")

    def _initialize_gemini(self):
        """Initialize Google Gemini model."""
        try:
            import google.generativeai as genai
            
            api_key = settings.gemini_api_key or settings.google_api_key
            if not api_key:
                raise ValueError("Gemini API key not found in settings")
            
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-pro')
            
            logger.info("Gemini model initialized successfully")
            
        except ImportError:
            logger.error("google-generativeai package not installed")
            raise
        except Exception as e:
            logger.error(f"Error initializing Gemini: {e}")
            raise

    def _initialize_openai(self):
        """Initialize OpenAI model."""
        try:
            from openai import OpenAI
            
            api_key = settings.openai_api_key
            if not api_key:
                raise ValueError("OpenAI API key not found in settings")
            
            self.model = OpenAI(api_key=api_key)
            self.openai_model = "gpt-3.5-turbo"  # Default model
            
            logger.info("OpenAI model initialized successfully")
            
        except ImportError:
            logger.error("openai package not installed")
            raise
        except Exception as e:
            logger.error(f"Error initializing OpenAI: {e}")
            raise

    def generate(self, 
                prompt: str, 
                context: Optional[List[Dict]] = None,
                max_tokens: int = 1000,
                temperature: float = 0.7) -> str:
        """
        Generate response from LLM.
        
        Args:
            prompt: User query/prompt
            context: Optional list of context documents
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0-1)
            
        Returns:
            Generated response text
        """
        logger.info(f"Generating response with {self.provider}")
        
        # Build full prompt with context
        full_prompt = self._build_prompt_with_context(prompt, context)
        
        try:
            if self.provider == "gemini":
                return self._generate_gemini(full_prompt, max_tokens, temperature)
            elif self.provider == "openai":
                return self._generate_openai(full_prompt, max_tokens, temperature)
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")
                
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise

    def _build_prompt_with_context(self, query: str, context: Optional[List[Dict]] = None) -> str:
        """
        Build prompt with retrieved context.
        
        Args:
            query: User query
            context: Retrieved documents
            
        Returns:
            Full prompt string
        """
        if not context:
            return query
        
        # Build context string
        context_str = "\n\n".join([
            f"Document {i+1}:\n{doc.get('text', '')}"
            for i, doc in enumerate(context)
        ])
        
        # Build full prompt
        prompt = f"""You are a helpful assistant for Nepal Government Services. Answer the user's question based on the provided context.

Context:
{context_str}

User Question: {query}

Instructions:
- Answer based primarily on the provided context
- If the context doesn't contain enough information, say so
- Be clear, concise, and accurate
- Provide specific details when available
- If mentioning forms or procedures, be precise

Answer:"""
        
        return prompt

    def _generate_gemini(self, prompt: str, max_tokens: int, temperature: float) -> str:
        """Generate response using Gemini."""
        try:
            generation_config = {
                "max_output_tokens": max_tokens,
                "temperature": temperature,
            }
            
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config,
            )
            
            return response.text
            
        except Exception as e:
            logger.error(f"Gemini generation error: {e}")
            raise

    def _generate_openai(self, prompt: str, max_tokens: int, temperature: float) -> str:
        """Generate response using OpenAI."""
        try:
            response = self.model.chat.completions.create(
                model=self.openai_model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant for Nepal Government Services."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature,
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI generation error: {e}")
            raise

    def generate_stream(self, 
                       prompt: str, 
                       context: Optional[List[Dict]] = None,
                       max_tokens: int = 1000,
                       temperature: float = 0.7):
        """
        Generate streaming response from LLM.
        
        Args:
            prompt: User query/prompt
            context: Optional list of context documents
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0-1)
            
        Yields:
            Response chunks
        """
        full_prompt = self._build_prompt_with_context(prompt, context)
        
        try:
            if self.provider == "gemini":
                yield from self._generate_gemini_stream(full_prompt, max_tokens, temperature)
            elif self.provider == "openai":
                yield from self._generate_openai_stream(full_prompt, max_tokens, temperature)
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")
                
        except Exception as e:
            logger.error(f"Error in streaming generation: {e}")
            raise

    def _generate_gemini_stream(self, prompt: str, max_tokens: int, temperature: float):
        """Generate streaming response using Gemini."""
        try:
            generation_config = {
                "max_output_tokens": max_tokens,
                "temperature": temperature,
            }
            
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config,
                stream=True,
            )
            
            for chunk in response:
                if chunk.text:
                    yield chunk.text
                    
        except Exception as e:
            logger.error(f"Gemini streaming error: {e}")
            raise

    def _generate_openai_stream(self, prompt: str, max_tokens: int, temperature: float):
        """Generate streaming response using OpenAI."""
        try:
            response = self.model.chat.completions.create(
                model=self.openai_model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant for Nepal Government Services."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature,
                stream=True,
            )
            
            for chunk in response:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            logger.error(f"OpenAI streaming error: {e}")
            raise
