import logging
import time
from typing import Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser  # Added this import
from fastapi import HTTPException
from app.config.settings import Settings

logger = logging.getLogger(__name__)


class SimplificationService:
    """Service for simplifying text using LangChain and Google Gemini."""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self._llm = None
        self._chain = None
    
    @property
    def llm(self):
        """Lazy initialization of the LLM."""
        if self._llm is None:
            try:
                self._llm = ChatGoogleGenerativeAI(
                    model="gemini-2.0-flash-lite",
                    google_api_key=self.settings.gemini_api_key,
                    temperature=0.6,
                    max_output_tokens=2000,
                )
            except Exception as e:
                logger.error(f"Failed to initialize Google Gemini: {str(e)}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to initialize language model: {str(e)}"
                )
        return self._llm
    
    @property
    def chain(self):
        """Lazy initialization of the LLM chain using LCEL."""
        if self._chain is None:
            template = """
            Simplify this text for someone with dyslexia:
            
            - Use short sentences (under 15 words)
            - Use common, simple words
            - Use active voice
            - Use bullet points for lists
            - Avoid complex jargon
            - Add line spacing between paragraphs
            
            Original text: {input_text}
            
            Simplified text:
            """
            
            prompt = PromptTemplate(
                input_variables=["input_text"],
                template=template,
            )
            
            try:
                # This is the new LCEL (LangChain Expression Language) syntax.
                # We "pipe" the prompt to the llm, and the llm's output to the string parser.
                self._chain = prompt | self.llm | StrOutputParser()
                
            except Exception as e:
                logger.error(f"Failed to create LLM chain: {str(e)}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to create processing pipeline: {str(e)}"
                )
        return self._chain
    
    async def simplify_text(self, text: str) -> tuple[str, int]:
        """
        Simplify text for dyslexic readers.
        
        Args:
            text: The text to simplify
            
        Returns:
            Tuple of (simplified_text, processing_time_ms)
            
        Raises:
            HTTPException: If simplification fails
        """
        if not text or not text.strip():
            raise HTTPException(
                status_code=400,
                detail="Input text cannot be empty"
            )
        
        start_time = time.time()
        
        try:
            # Run the chain using .ainvoke() and pass a dictionary
            # The 'result' will be a simple string because we used StrOutputParser
            result = await self.chain.ainvoke({"input_text": text})
            
            # Calculate processing time
            processing_time = int((time.time() - start_time) * 1000)
            
            return result, processing_time
            
        except Exception as e:
            logger.error(f"Error simplifying text: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error simplifying text: {str(e)}"
            )
