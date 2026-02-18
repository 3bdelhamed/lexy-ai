from collections import defaultdict
from typing import Dict, List, Tuple
from .models import ExtractedItem, BoundingBox

class ResultCleaner:
    def clean(self, content: Dict[int, List[ExtractedItem]], dimensions: Dict[int, Tuple[float, float]], total_pages: int) -> Dict[int, List[ExtractedItem]]:
        cleaned_content = {}
        text_counts = defaultdict(int)

        # 1. Frequency Analysis for Headers/Footers
        for items in content.values():
            seen = set()
            for item in items:
                if item.type == 'text' and item.content.strip():
                    key = item.content.strip().lower()
                    if key not in seen:
                        text_counts[key] += 1
                        seen.add(key)
        
        noise_threshold = max(2, total_pages * 0.40) 

        for page_num, items in content.items():
            valid_items = []
            page_h = dimensions.get(page_num, (0, 0))[1]
            
            native_bboxes = [i.bbox for i in items if i.method == 'native_extraction' and i.bbox]

            for item in items:
                text_clean = item.content.strip().lower()
                
                # Filter headers
                if text_counts[text_clean] > noise_threshold and len(items) > 3:
                    continue
                    
                # Filter spatial margins
                if item.bbox and page_h > 0:
                    y_mid = (item.bbox.y0 + item.bbox.y1) / 2
                    if (y_mid < page_h * 0.05 or y_mid > page_h * 0.95) and text_counts[text_clean] > 1:
                        continue
                
                # Deduplicate OCR vs Native
                if item.method == 'selective_ocr' and item.bbox:
                    is_dup = False
                    for nb in native_bboxes:
                        if self._calculate_iou(item.bbox, nb) > 0.4:
                            is_dup = True; break
                    if is_dup: continue
                
                valid_items.append(item)
            cleaned_content[page_num] = valid_items
        return cleaned_content

    @staticmethod
    def _calculate_iou(box1: BoundingBox, box2: BoundingBox) -> float:
        x_left = max(box1.x0, box2.x0)
        y_top = max(box1.y0, box2.y0)
        x_right = min(box1.x1, box2.x1)
        y_bottom = min(box1.y1, box2.y1)
        if x_right < x_left or y_bottom < y_top: return 0.0
        intersection = (x_right - x_left) * (y_bottom - y_top)
        union = box1.area + box2.area - intersection
        return intersection / union if union > 0 else 0.0