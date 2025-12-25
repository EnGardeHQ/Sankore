from typing import List
from src.services.trends.base import TrendProvider, TrendResult

class MetaTrendProvider(TrendProvider):
    async def fetch_trends(self, industry: str) -> List[TrendResult]:
        # Integrated with Production Env Var
        import os
        access_token = os.getenv("META_API_KEY")
        
        if access_token and access_token != "mock_token":
            # TODO: Implement actual Graph API call here using access_token
            # For now, we return mock data even if token exists to avoid breaking without full implementation
            pass

        # MOCK IMPLEMENTATION
        return [
            TrendResult(
                platform="meta",
                format="video",
                trend_type="visual_style",
                trend_name="UGC Testimonial - Split Screen",
                description="High performing format showing product demo on top, reaction on bottom.",
                score=85.5,
                metadata={"duration": "15s", "aspect_ratio": "9:16"}
            ),
            TrendResult(
                platform="meta",
                format="carousel",
                trend_type="copy_angle",
                trend_name="Problem-Agitation-Solution",
                description="Carousel cards walking through pain points before revealing product.",
                score=92.0,
                metadata={"card_count": 5}
            )
        ]
