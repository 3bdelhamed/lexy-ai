import logging
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from app.config.settings import Settings, get_settings
from app.models.schemas import TextInput, SimplificationResponse, ErrorResponse, SimplificationOptions
from app.services.simplification_service import SimplificationService
from app.utils.file_parser import FileParser

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/text", response_model=SimplificationResponse)
async def simplify_text(
    text_input: TextInput,
    settings: Settings = Depends(get_settings)
):
    """
    Simplify text for dyslexic readers.
    
    - **text**: The text to simplify
    - **options**: Optional simplification settings including mode, intensity, and formatting controls
    """
    try:
        # Initialize the service
        service = SimplificationService(settings)
        
        # Simplify the text
        simplified_text, processing_time, options_used = await service.simplify_text(
            text_input.text, 
            text_input.options
        )
        
        return SimplificationResponse(
            original_text=text_input.text,
            simplified_text=simplified_text,
            processing_time_ms=processing_time,
            options_used=options_used
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in simplify_text: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred"
        )


@router.post("/file", response_model=SimplificationResponse)
async def simplify_file(
    file: UploadFile = File(...),
    mode: str = Form("general"),
    intensity: str = Form("medium"),
    custom_max_sentence_length: int = Form(None),
    sentence_breaking_mode: bool = Form(True),
    active_voice_enforcement: bool = Form(True),
    complex_word_replacement: str = Form("medium"),
    synonym_suggestion_mode: str = Form("auto-replace"),
    jargon_handling: str = Form("define"),
    paragraph_length: int = Form(3),
    use_bullets: bool = Form(True),
    generous_whitespace: bool = Form(True),
    settings: Settings = Depends(get_settings)
):
    """
    Simplify text from uploaded file for dyslexic readers.
    
    - **file**: The file to process (supports TXT, PDF, DOCX)
    - **mode**: Simplification mode (general, academic, technical, narrative, interactive)
    - **intensity**: Simplification intensity (light, medium, heavy, custom)
    - **custom_max_sentence_length**: Custom max sentence length (only used when intensity is 'custom')
    - **sentence_breaking_mode**: Automatically split long sentences
    - **active_voice_enforcement**: Convert passive to active voice
    - **complex_word_replacement**: Complexity threshold for word replacement (light, medium, heavy, off)
    - **synonym_suggestion_mode**: How to present word replacements (auto-replace, suggest-options, highlight-only)
    - **jargon_handling**: How to handle technical terms (remove, define, preserve)
    - **paragraph_length**: Maximum sentences per paragraph
    - **use_bullets**: Use bullet points for lists
    - **generous_whitespace**: Add extra line spacing
    """
    try:
        # Check file size
        file_size = 0
        content = await file.read()
        file_size = len(content)
        await file.seek(0)  # Reset file pointer
        
        max_size_bytes = settings.max_file_size_mb * 1024 * 1024
        if file_size > max_size_bytes:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size is {settings.max_file_size_mb}MB"
            )
        
        # Extract text from file
        file_type, text = await FileParser.extract_text_from_file(file)
        
        # Create options from form data
        options = SimplificationOptions(
            mode=mode,
            intensity=intensity,
            custom_max_sentence_length=custom_max_sentence_length,
            sentence_structure={
                "max_sentence_length": custom_max_sentence_length if intensity == "custom" else None,
                "sentence_breaking_mode": sentence_breaking_mode,
                "active_voice_enforcement": active_voice_enforcement
            },
            vocabulary={
                "complex_word_replacement": complex_word_replacement,
                "synonym_suggestion_mode": synonym_suggestion_mode,
                "jargon_handling": jargon_handling
            },
            formatting={
                "paragraph_length": paragraph_length,
                "use_bullets": use_bullets,
                "generous_whitespace": generous_whitespace
            }
        )
        
        # Initialize the service
        service = SimplificationService(settings)
        
        # Simplify the text
        simplified_text, processing_time, options_used = await service.simplify_text(text, options)
        
        return SimplificationResponse(
            original_text=text,
            simplified_text=simplified_text,
            processing_time_ms=processing_time,
            options_used=options_used
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in simplify_file: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred"
        )


@router.get("/options", response_model=dict)
async def get_simplification_options():
    """
    Get available simplification options and their descriptions.
    """
    return {
        "modes": {
            "general": "Simplify general daily content for readability",
            "academic": "Simplify academic text while preserving educational value",
            "technical": "Simplify technical documentation for accessibility",
            "narrative": "Simplify stories while maintaining emotional impact",
            "interactive": "Provide multiple simplification options without automatically changing text"
        },
        "intensities": {
            "light": "Focus on breaking sentences over 20 words, minimal vocabulary changes",
            "medium": "Break sentences over 15 words, replace most complex vocabulary",
            "heavy": "Keep sentences under 10 words, use only common vocabulary",
            "custom": "Use user-defined sentence length limit"
        },
        "sentence_structure": {
            "max_sentence_length": "Maximum words per sentence (5-50)",
            "sentence_breaking_mode": "Automatically split long sentences",
            "active_voice_enforcement": "Convert passive voice to active voice"
        },
        "vocabulary": {
            "complex_word_replacement": {
                "light": "Replace words over 8 letters",
                "medium": "Replace words over 6 letters",
                "heavy": "Replace words over 4 letters",
                "off": "Keep original vocabulary"
            },
            "synonym_suggestion_mode": {
                "auto-replace": "Automatically substitute simpler words",
                "suggest-options": "Show 2-3 alternatives in brackets",
                "highlight-only": "Mark complex words without replacing"
            },
            "jargon_handling": {
                "remove": "Replace all jargon with plain language",
                "define": "Keep term but add simple definition in parentheses",
                "preserve": "Keep original technical terms"
            }
        },
        "formatting": {
            "paragraph_length": "Maximum sentences per paragraph (1-5)",
            "use_bullets": "Use bullet points for lists",
            "generous_whitespace": "Add extra line spacing"
        }
    }