import logging
from fastapi import APIRouter, UploadFile, File, HTTPException
from api.schemas.extract import ExtractResponse
from services.pdf_extractor.service import PDFExtractionService
from utils import validate_uploaded_file

logger = logging.getLogger(__name__)

# Create a new router group
router = APIRouter(prefix="/extract", tags=["Extraction"])

@router.post("/pdf", response_model=ExtractResponse)
async def extract_pdf(
    file: UploadFile = File(..., description="PDF file to extract text from (max 10MB)")
):
    """
    **Dedicated PDF Extraction Endpoint**
    
    Extracts raw text from a PDF file using the Hybrid Extraction Engine.
    
    **Features:**
    - Removes headers/footers automatically
    - Uses OCR for images/tables (if configured)
    - Deduplicates overlapping text
    """
    # 1. Validate file is PDF
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=400, 
            detail="Invalid file type. This endpoint only supports .pdf files."
        )

    # 2. Validate size and get bytes
    content_bytes = await validate_uploaded_file(file)
    
    try:
        logger.info(f"Starting dedicated extraction for: {file.filename}")
        
        # 3. Initialize your custom service
        extractor = PDFExtractionService()
        
        # 4. Perform Extraction
        extracted_text = extractor.extract_text(content_bytes)
        
        return ExtractResponse(
            filename=file.filename,
            content=extracted_text,
            char_count=len(extracted_text)
        )

    except Exception as e:
        logger.error(f"Extraction failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")