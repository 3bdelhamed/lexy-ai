from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum

class ContentType(Enum):
    TEXT = "text"
    IMAGE = "image"
    TABLE = "table"
    EQUATION = "equation"
    CHART = "chart"
    UNKNOWN = "unknown"

class Strategy(Enum):
    TEXT_ONLY = "text_only"
    SELECTIVE_OCR = "selective_ocr"
    FULL_OCR = "full_ocr"

@dataclass
class BoundingBox:
    x0: float
    y0: float
    x1: float
    y1: float
    
    @property
    def width(self) -> float: return self.x1 - self.x0
    @property
    def height(self) -> float: return self.y1 - self.y0
    @property
    def area(self) -> float: return self.width * self.height
    def to_list(self) -> List[float]: return [self.x0, self.y0, self.x1, self.y1]

@dataclass
class PageRegion:
    bbox: BoundingBox
    content_type: ContentType
    content: Optional[str] = None
    confidence: float = 0.0
    ocr_cost: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PageAnalysis:
    page_num: int
    page_width: float
    page_height: float
    text_ratio: float
    image_ratio: float
    text_blocks: List
    image_regions: List[PageRegion]
    has_equations: bool
    has_tables: bool
    recommended_strategy: Strategy
    estimated_cost: float

@dataclass
class ExtractedItem:
    type: str
    content: str
    method: str
    page_num: int
    bbox: Optional[BoundingBox] = None
    confidence: float = 0.0
    ocr_cost: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)