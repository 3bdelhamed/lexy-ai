import logging
from collections import defaultdict
import fitz  # PyMuPDF
from .models import ExtractedItem, Strategy, BoundingBox
from .analyzers import PageAnalyzer
from .ocr import MistralOCR
from .cleaner import ResultCleaner

logger = logging.getLogger(__name__)

class PDFExtractionService:
    def __init__(self):
        self.ocr = MistralOCR()
        self.cleaner = ResultCleaner()
        self.image_threshold = 0.15
        self.full_ocr_threshold = 0.70
        self.dpi = 300

    def extract_text(self, file_bytes: bytes) -> str:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        try:
            total_pages = len(doc)
            
            # Pass 1: Logo scan
            xref_counts = defaultdict(int)
            for i in range(total_pages):
                for img in doc[i].get_images(full=True):
                    xref_counts[img[0]] += 1
            
            analyzer = PageAnalyzer(self.image_threshold, self.full_ocr_threshold, xref_counts)
            extracted_content = {}
            page_dims = {}

            # Pass 2: Extraction
            for page_num in range(total_pages):
                page = doc[page_num]
                page_dims[page_num] = (page.rect.width, page.rect.height)
                analysis = analyzer.analyze(page, page_num)
                
                if analysis.recommended_strategy == Strategy.FULL_OCR:
                    items = self._full_ocr(page, page_num)
                elif analysis.recommended_strategy == Strategy.SELECTIVE_OCR:
                    items = self._selective_ocr(page, analysis)
                else:
                    items = self._text_only(page, page_num)
                    
                extracted_content[page_num] = items

            # Pass 3: Cleaning
            final_content = self.cleaner.clean(extracted_content, page_dims, total_pages)
            
            # Merge
            full_text = []
            for p in sorted(final_content.keys()):
                full_text.append("\n".join([i.content for i in final_content[p]]))
            return "\n\n".join(full_text)
            
        finally:
            doc.close()

    def _text_only(self, page, page_num):
        items = []
        for b in page.get_text("blocks"):
            if len(b) >= 6 and b[4].strip():
                items.append(ExtractedItem("text", b[4], "native_extraction", page_num, BoundingBox(*b[:4])))
        return items

    def _full_ocr(self, page, page_num):
        pix = page.get_pixmap(matrix=fitz.Matrix(self.dpi/72, self.dpi/72))
        text, _ = self.ocr.process(pix.tobytes("png"), "full_page")
        return [ExtractedItem("full_page", text, "full_ocr", page_num)]

    def _selective_ocr(self, page, analysis):
        items = self._text_only(page, analysis.page_num)
        for region in analysis.image_regions:
            clip = fitz.Rect(region.bbox.to_list())
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), clip=clip)
            text, _ = self.ocr.process(pix.tobytes("png"), region.content_type.value)
            items.append(ExtractedItem(region.content_type.value, text, "selective_ocr", analysis.page_num, region.bbox))
        return items