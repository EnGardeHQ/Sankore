from abc import ABC, abstractmethod
from typing import List, Dict, Any
from pydantic import BaseModel

class TrendResult(BaseModel):
    platform: str
    format: str # video, image, carousel
    trend_type: str # visual_style, audio, copy_angle
    trend_name: str
    description: str
    score: float
    metadata: Dict[str, Any] = {}

class TrendProvider(ABC):
    
    @abstractmethod
    async def fetch_trends(self, industry: str) -> List[TrendResult]:
        """
        Fetch trending ad formats/styles for a specific industry.
        """
        pass
