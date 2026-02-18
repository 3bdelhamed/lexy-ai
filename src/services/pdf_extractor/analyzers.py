import logging
from typing import List, Dict, Tuple
from .models import ContentType, Strategy, BoundingBox, PageRegion, PageAnalysis

logger = logging.getLogger(__name__)

class PageAnalyzer:
    def __init__(self, image_threshold: float = 0.15, full_ocr_threshold: float = 0.70, repeated_xref_counts: Dict[int, int] = None):
        self.image_threshold = image_threshold
        self.full_ocr_threshold = full_ocr_threshold
        self.repeated_xref_counts = repeated_xref_counts or {}
    
    def analyze(self, page, page_num: int) -> PageAnalysis:
        page_rect = page.rect
        page_area = page_rect.width * page_rect.height
        text_blocks = page.get_text("blocks")
        text_area = sum((b[2]-b[0])*(b[3]-b[1]) for b in text_blocks if len(b) >= 6)
        text_ratio = text_area / page_area if page_area > 0 else 0
        
        # Image analysis logic from source [cite: 24-35]
        image_regions = []
        significant_image_area = 0
        
        for img in page.get_images(full=True):
            try:
                xref = img[0]
                # Filter logos (repeated images)
                if self.repeated_xref_counts.get(xref, 0) > 2:
                    continue
                    
                for rect in page.get_image_rects(xref):
                    # Filter header/footer/tiny images
                    if (rect.y1 < page_rect.height * 0.10) or (rect.y0 > page_rect.height * 0.90): continue
                    if (rect.width * rect.height / page_area) < 0.02: continue
                    
                    significant_image_area += rect.width * rect.height
                    image_regions.append(PageRegion(
                        bbox=BoundingBox(rect.x0, rect.y0, rect.x1, rect.y1),
                        content_type=ContentType.IMAGE,
                        metadata={'xref': xref}
                    ))
            except Exception as e:
                logger.warning(f"Image extract error: {e}")

        image_ratio = significant_image_area / page_area if page_area > 0 else 0
        
        # Strategy determination
        if image_ratio >= self.full_ocr_threshold:
            strategy = Strategy.FULL_OCR
            cost = 1.0
        elif image_ratio >= self.image_threshold or len(image_regions) > 0:
            strategy = Strategy.SELECTIVE_OCR
            cost = 0.3
        else:
            strategy = Strategy.TEXT_ONLY
            cost = 0.0
            
        return PageAnalysis(
            page_num=page_num, page_width=page_rect.width, page_height=page_rect.height,
            text_ratio=text_ratio, image_ratio=image_ratio, text_blocks=text_blocks,
            image_regions=image_regions, has_equations=False, has_tables=False,
            recommended_strategy=strategy, estimated_cost=cost
        )