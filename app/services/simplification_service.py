import logging
import time
from typing import Optional, Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.runnables import Runnable
from langchain_core.output_parsers import StrOutputParser
from fastapi import HTTPException
from app.config.settings import Settings
from app.models.schemas import SimplificationOptions, SimplificationMode, SimplificationIntensity
from app.services.prompts import get_simplification_prompt

logger = logging.getLogger(__name__)


class SimplificationService:
    """Service for simplifying text using LangChain and Google Gemini."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self._llm = None
        # self._chains is now self._runnables
        self._runnables: Dict[str, Runnable] = {}

    @property
    def llm(self):
        """Lazy initialization of the LLM."""
        if self._llm is None:
            try:
                self._llm = ChatGoogleGenerativeAI(
                    model="gemini-2.0-flash-lite",
                    google_api_key=self.settings.gemini_api_key,
                    temperature=0.6,
                    max_output_tokens=4000,
                )
            except Exception as e:
                logger.error(f"Failed to initialize Google Gemini: {str(e)}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to initialize language model: {str(e)}"
                )
        return self._llm

    def _get_chain_runnable(self, options: SimplificationOptions) -> Runnable:
        """
        Get or create a cached LCEL Runnable for the specific options.
        This replaces the old _get_chain method.
        """
        # Create a key based on mode and intensity
        key = f"{options.mode.value}_{options.intensity.value}"

        if key not in self._runnables:
            try:
                # 1. Get the prompt template from our new prompt factory
                prompt = get_simplification_prompt(options)

                # 2. Define the LCEL chain (now called a "runnable")
                #    The syntax is: prompt | llm | output_parser
                chain = prompt | self.llm | StrOutputParser()

                self._runnables[key] = chain

            except Exception as e:
                logger.error(f"Failed to create LLM runnable: {str(e)}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to create processing pipeline: {str(e)}"
                )

        return self._runnables[key]

    def _get_template_values(self, options: SimplificationOptions) -> Dict[str, Any]:
        """Get the values to fill in the template based on options."""
        # Default values
        values = {
            "max_sentence_length": 15,
            "paragraph_length": 3,
            "complex_word_threshold": 6
        }

        # Update based on intensity
        if options.intensity == SimplificationIntensity.light:
            values["max_sentence_length"] = 20
            values["complex_word_threshold"] = 8
        elif options.intensity == SimplificationIntensity.medium:
            values["max_sentence_length"] = 15
            values["complex_word_threshold"] = 6
        elif options.intensity == SimplificationIntensity.heavy:
            values["max_sentence_length"] = 10
            values["complex_word_threshold"] = 4
        elif options.intensity == SimplificationIntensity.custom and options.custom_max_sentence_length:
            values["max_sentence_length"] = options.custom_max_sentence_length

        # Update based on custom controls (if they exist)
        if options.sentence_structure:
            if options.sentence_structure.max_sentence_length:
                values["max_sentence_length"] = options.sentence_structure.max_sentence_length

        if options.formatting:
            if options.formatting.paragraph_length:
                values["paragraph_length"] = options.formatting.paragraph_length

        if options.vocabulary:
            if options.vocabulary.complex_word_replacement == "light":
                values["complex_word_threshold"] = 8
            elif options.vocabulary.complex_word_replacement == "medium":
                values["complex_word_threshold"] = 6
            elif options.vocabulary.complex_word_replacement == "heavy":
                values["complex_word_threshold"] = 4
            elif options.vocabulary.complex_word_replacement == "off":
                # Effectively disable replacement
                values["complex_word_threshold"] = 100

        return values

    async def simplify_text(self, text: str, options: Optional[SimplificationOptions] = None) -> tuple[str, int, SimplificationOptions]:
        """
        Simplify text for dyslexic readers.

        Args:
            text: The text to simplify
            options: Simplification options

        Returns:
            Tuple of (simplified_text, processing_time_ms, options_used)

        Raises:
            HTTPException: If simplification fails
        """
        if not text or not text.strip():
            raise HTTPException(
                status_code=400,
                detail="Input text cannot be empty"
            )

        # Use default options if none provided
        if options is None:
            options = SimplificationOptions()

        start_time = time.time()

        try:
            # Get the appropriate runnable
            chain = self._get_chain_runnable(options)

            # Get template values
            template_values = self._get_template_values(options)

            # Create the input dictionary for the runnable
            # It must contain all keys the prompt template expects
            input_dict = {
                "input_text": text,
                **template_values
            }

            # Run the chain using .ainvoke() instead of .arun()
            result = await chain.ainvoke(input_dict)

            # Calculate processing time
            processing_time = int((time.time() - start_time) * 1000)

            return result, processing_time, options

        except Exception as e:
            logger.error(f"Error simplifying text: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error simplifying text: {str(e)}"
            )
